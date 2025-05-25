#!/usr/bin/env python3
import requests
import json
import os
import sys
import time
from typing import Dict, Any, Optional, List, Tuple
from dotenv import load_dotenv
from web3 import Web3
from eth_account import Account
from nba_markets import get_active_sports_markets, parse_token_ids, parse_outcomes, get_order_book

# Load environment variables
load_dotenv()

# Constants
POLYMARKET_EXCHANGE = "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E"  # Polymarket Exchange contract
USDC_CONTRACT = "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359"  # USDC on Polygon
RPC_URL = "https://polygon-rpc.com"
CLOB_API_URL = "https://clob.polymarket.com"
BET_AMOUNT = 1.0  # Fixed bet amount in USDC

def get_wallet_info() -> Tuple[str, str, Web3]:
    """
    Get wallet address and web3 connection from private key
    """
    # Get private key from environment
    private_key = os.getenv("POLYGON_WALLET_PRIVATE_KEY", "")
    
    if not private_key:
        raise ValueError("No private key found in environment variables")
    
    # Add 0x prefix if missing
    if not private_key.startswith("0x"):
        private_key = "0x" + private_key
    
    # Connect to Polygon network
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    
    if not w3.is_connected():
        raise ConnectionError("Failed to connect to Polygon network")
    
    print(f"Connected to Polygon network. Chain ID: {w3.eth.chain_id}")
    
    # Get wallet address from private key
    account = Account.from_key(private_key)
    wallet_address = account.address
    print(f"Wallet address: {wallet_address}")
    
    return wallet_address, private_key, w3

def check_usdc_approval(wallet_address: str, w3: Web3) -> bool:
    """
    Check if USDC is approved for spending by Polymarket
    """
    # USDC contract ABI (for balanceOf and allowance functions)
    usdc_abi = json.loads('''[
        {
            "constant": true,
            "inputs": [{"name": "account", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"name": "", "type": "uint256"}],
            "payable": false,
            "stateMutability": "view",
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [
                {"name": "owner", "type": "address"},
                {"name": "spender", "type": "address"}
            ],
            "name": "allowance",
            "outputs": [{"name": "", "type": "uint256"}],
            "payable": false,
            "stateMutability": "view",
            "type": "function"
        }
    ]''')
    
    # Create contract instance
    usdc_contract = w3.eth.contract(address=USDC_CONTRACT, abi=usdc_abi)
    
    # Check USDC balance
    balance = usdc_contract.functions.balanceOf(wallet_address).call()
    balance_usdc = balance / 10**6  # USDC has 6 decimals
    
    print(f"USDC balance: {balance_usdc} USDC")
    
    if balance < 1_000_000:  # Less than 1 USDC
        print("Insufficient USDC balance (need at least 1 USDC)")
        return False
    
    # Check current allowance
    current_allowance = usdc_contract.functions.allowance(
        wallet_address, 
        POLYMARKET_EXCHANGE
    ).call()
    current_allowance_usdc = current_allowance / 10**6
    
    print(f"Current Polymarket allowance: {current_allowance_usdc} USDC")
    
    # If allowance is sufficient, return True
    return current_allowance >= 1_000_000  # 1 USDC minimum

def place_market_order(
    token_id: str, 
    side: str, 
    size: float, 
    wallet_address: str, 
    private_key: str,
    w3: Web3
) -> Optional[str]:
    """
    Place a market order on Polymarket
    
    Args:
        token_id: The token ID to trade
        side: Either 'buy' or 'sell'
        size: The size of the position in number of shares
        wallet_address: The wallet address
        private_key: The private key for signing
        w3: Web3 instance
        
    Returns:
        Optional transaction hash if successful
    """
    try:
        # Step 1: Create the order structure
        order = {
            "order": {
                "token_id": token_id,
                "side": side.upper(),
                "type": "MARKET",
                "size": str(size),
                "time_in_force": "FOK"  # Fill-or-Kill
            }
        }
        
        # Step 2: Get nonce, expiration, and order signature from the API
        signature_url = f"{CLOB_API_URL}/orders/signature"
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
        
        response = requests.post(signature_url, headers=headers, json=order)
        
        if response.status_code != 200:
            print(f"Failed to get order signature: {response.status_code}")
            print(response.text)
            return None
        
        signature_data = response.json()
        
        # Extract data for the signed order
        nonce = signature_data.get("nonce")
        expiration = signature_data.get("expiration")
        signature = signature_data.get("signature")
        
        if not all([nonce, expiration, signature]):
            print("Missing signature data")
            return None
        
        # Step 3: Create the final order with signature
        signed_order = {
            "token_id": token_id,
            "side": side.upper(),
            "type": "MARKET",
            "size": str(size),
            "time_in_force": "FOK",
            "nonce": nonce,
            "expiration": expiration,
            "signature": signature,
            "wallet": wallet_address
        }
        
        # Step 4: Submit the order
        order_url = f"{CLOB_API_URL}/orders"
        
        order_response = requests.post(order_url, headers=headers, json=signed_order)
        
        if order_response.status_code != 200:
            print(f"Failed to place order: {order_response.status_code}")
            print(order_response.text)
            return None
        
        order_result = order_response.json()
        
        # Step 5: Check if we need to settle the order
        if "tx_data" in order_result:
            tx_data = order_result["tx_data"]
            
            # Build transaction
            tx = {
                'from': wallet_address,
                'to': tx_data.get("to"),
                'data': tx_data.get("data"),
                'value': w3.to_wei(0, 'ether'),  # No ETH value
                'gas': 500000,  # Gas limit
                'gasPrice': w3.to_wei('50', 'gwei'),
                'nonce': w3.eth.get_transaction_count(wallet_address),
            }
            
            # Sign and send transaction
            signed_tx = w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            print(f"Settlement transaction sent! Hash: {tx_hash.hex()}")
            print(f"View on PolygonScan: https://polygonscan.com/tx/{tx_hash.hex()}")
            
            # Wait for transaction to be mined
            print("Waiting for transaction to be confirmed...")
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if tx_receipt['status'] == 1:
                print("✅ Transaction confirmed!")
                return tx_hash.hex()
            else:
                print("❌ Transaction failed. Please check PolygonScan for details.")
                return None
        else:
            print("Order placed successfully!")
            return "success"
            
    except Exception as e:
        print(f"Error placing order: {str(e)}")
        return None

def find_best_market() -> Tuple[Optional[Dict[str, Any]], Optional[str], Optional[str]]:
    """
    Find the best market to bet on (most liquid NBA market)
    
    Returns:
        Tuple of (market, outcome, token_id)
    """
    print("Finding the best market to bet on...")
    
    # Get active sports markets
    sports_markets = get_active_sports_markets()
    
    if not sports_markets:
        print("No active sports markets found")
        return None, None, None
    
    # Filter for NBA markets
    nba_markets = []
    for market in sports_markets:
        question = market.get("question", "").lower()
        if any(term in question for term in ["nba", "basketball"]):
            nba_markets.append(market)
    
    if not nba_markets:
        print("No NBA markets found, using general sports markets")
        filtered_markets = sports_markets
    else:
        print(f"Found {len(nba_markets)} NBA markets")
        filtered_markets = nba_markets
    
    # Find the market with the most liquid order book
    best_market = None
    best_liquidity = 0
    best_outcome = None
    best_token_id = None
    
    for market in filtered_markets:
        token_ids = parse_token_ids(market)
        outcomes = parse_outcomes(market)
        
        if not token_ids or not outcomes or len(token_ids) != len(outcomes):
            continue
        
        for i, token_id in enumerate(token_ids):
            order_book = get_order_book(token_id)
            
            if not order_book:
                continue
                
            # Check for bids and asks
            bids = order_book.get("bids", [])
            asks = order_book.get("asks", [])
            
            if not bids or not asks:
                continue
            
            # Calculate liquidity score based on depth and tightness of spread
            try:
                best_bid = float(bids[0]["price"])
                best_ask = float(asks[0]["price"])
                
                # Calculate bid-ask spread
                spread = best_ask - best_bid
                
                # Calculate total volume in order book (up to 3 levels)
                bid_volume = sum(float(bid["size"]) for bid in bids[:3])
                ask_volume = sum(float(ask["size"]) for ask in asks[:3])
                
                # Liquidity score: higher volume and tighter spread = better
                if spread > 0:
                    liquidity_score = (bid_volume + ask_volume) / spread
                else:
                    liquidity_score = 0
                
                # Update best market if this one has better liquidity
                if liquidity_score > best_liquidity:
                    best_liquidity = liquidity_score
                    best_market = market
                    best_outcome = outcomes[i]
                    best_token_id = token_id
            except (IndexError, ValueError, KeyError):
                continue
    
    if best_market:
        print(f"Best market found: {best_market.get('question')}")
        print(f"Outcome: {best_outcome}")
        print(f"Liquidity score: {best_liquidity:.2f}")
        return best_market, best_outcome, best_token_id
    else:
        print("No suitable market found")
        return None, None, None

def place_bet_on_best_market(wallet_address: str, private_key: str, w3: Web3) -> None:
    """
    Find the best market and place a 1 USDC bet
    """
    # Find best market
    market, outcome, token_id = find_best_market()
    
    if not market or not outcome or not token_id:
        print("No suitable market found for betting")
        return
    
    # Market details
    market_question = market.get("question", "Unknown Market")
    
    print("\n" + "=" * 70)
    print(f"PLACING BET: {BET_AMOUNT} USDC on {outcome}")
    print(f"MARKET: {market_question}")
    print("=" * 70)
    
    # Place the order
    tx_hash = place_market_order(token_id, "buy", BET_AMOUNT, wallet_address, private_key, w3)
    
    if tx_hash:
        print("\n" + "=" * 70)
        print(f"✅ BET PLACED SUCCESSFULLY!")
        print(f"Amount: {BET_AMOUNT} USDC")
        print(f"Market: {market_question}")
        print(f"Outcome: {outcome}")
        if tx_hash != "success":
            print(f"Transaction: https://polygonscan.com/tx/{tx_hash}")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("❌ FAILED TO PLACE BET")
        print("=" * 70)

def main() -> None:
    """
    Main function to programmatically place a 1 USDC bet on the best Polymarket sports market
    """
    print("=" * 70)
    print("POLYMARKET AUTOMATED BETTING BOT")
    print("=" * 70)
    
    try:
        # Step 1: Get wallet info and web3 connection
        wallet_address, private_key, w3 = get_wallet_info()
        
        # Step 2: Check USDC approval
        if not check_usdc_approval(wallet_address, w3):
            print("\nInsufficient USDC approval. Please run 'python approve_usdc.py' first.")
            return
        
        # Step 3: Place bet on best market
        place_bet_on_best_market(wallet_address, private_key, w3)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        
if __name__ == "__main__":
    main() 