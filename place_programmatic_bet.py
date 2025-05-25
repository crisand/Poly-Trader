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
        print(f"Attempting to place {side.upper()} order for {size} shares...")
        
        # Step 1: Create the order structure
        order = {
            "token_id": token_id,
            "side": side.upper(),
            "type": "MARKET",
            "size": str(size),
            "time_in_force": "GTC"  # Good Till Cancelled (more flexible than FOK)
        }
        
        # Step 2: Try to place the order directly first
        order_url = f"{CLOB_API_URL}/orders"
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
        
        print("Submitting order to Polymarket...")
        order_response = requests.post(order_url, headers=headers, json=order)
        
        if order_response.status_code == 200:
            order_result = order_response.json()
            print("✅ Order submitted successfully!")
            
            # Check if we need to settle the order on-chain
            if "tx_data" in order_result:
                print("Order requires on-chain settlement...")
                tx_data = order_result["tx_data"]
                
                # Build transaction
                tx = {
                    'from': wallet_address,
                    'to': tx_data.get("to"),
                    'data': tx_data.get("data"),
                    'value': w3.to_wei(0, 'ether'),
                    'gas': 500000,
                    'gasPrice': w3.to_wei('50', 'gwei'),
                    'nonce': w3.eth.get_transaction_count(wallet_address),
                }
                
                # Sign and send transaction
                signed_tx = w3.eth.account.sign_transaction(tx, private_key)
                tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                
                print(f"Settlement transaction sent! Hash: {tx_hash.hex()}")
                print(f"View on PolygonScan: https://polygonscan.com/tx/{tx_hash.hex()}")
                
                # Wait for confirmation
                print("Waiting for transaction confirmation...")
                tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                
                if tx_receipt['status'] == 1:
                    print("✅ Transaction confirmed!")
                    return tx_hash.hex()
                else:
                    print("❌ Transaction failed.")
                    return None
            else:
                print("✅ Order completed off-chain!")
                return "success"
        
        # If direct order fails, try with signature
        elif order_response.status_code == 400 or order_response.status_code == 401:
            print("Direct order failed, trying with signature...")
            
            # Get signature for the order
            signature_url = f"{CLOB_API_URL}/orders/signature"
            
            signature_response = requests.post(signature_url, headers=headers, json={"order": order})
            
            if signature_response.status_code != 200:
                print(f"Failed to get order signature: {signature_response.status_code}")
                print(signature_response.text)
                return None
            
            signature_data = signature_response.json()
            
            # Add signature data to order
            signed_order = {
                **order,
                "nonce": signature_data.get("nonce"),
                "expiration": signature_data.get("expiration"),
                "signature": signature_data.get("signature"),
                "wallet": wallet_address
            }
            
            # Submit signed order
            final_response = requests.post(order_url, headers=headers, json=signed_order)
            
            if final_response.status_code == 200:
                print("✅ Signed order submitted successfully!")
                return "success"
            else:
                print(f"Failed to submit signed order: {final_response.status_code}")
                print(final_response.text)
                return None
        
        else:
            print(f"Order submission failed: {order_response.status_code}")
            print(order_response.text)
            return None
            
    except Exception as e:
        print(f"Error placing order: {str(e)}")
        return None

def get_all_active_markets() -> List[Dict[str, Any]]:
    """
    Fetch ALL active markets from Polymarket (not just sports)
    """
    print("Fetching all active markets...")
    
    markets_url = "https://gamma-api.polymarket.com/markets"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
    }
    
    params = {
        "limit": 100,
        "active": True
    }
    
    try:
        response = requests.get(markets_url, params=params, headers=headers)
        
        if response.status_code != 200:
            print(f"Failed to fetch markets: {response.status_code}")
            return []
        
        all_markets = response.json()
        
        if not isinstance(all_markets, list):
            print("Unexpected API response format")
            return []
        
        print(f"Retrieved {len(all_markets)} active markets from Polymarket")
        
        # Filter for tradable markets (with CLOB token IDs)
        tradable_markets = [
            market for market in all_markets 
            if market.get("clobTokenIds") and len(market.get("clobTokenIds", [])) > 0
        ]
        
        print(f"Found {len(tradable_markets)} tradable markets")
        return tradable_markets
        
    except Exception as e:
        print(f"Error fetching markets: {e}")
        return []

def find_best_market() -> Tuple[Optional[Dict[str, Any]], Optional[str], Optional[str]]:
    """
    Find the best market to bet on (most liquid market from ALL markets)
    
    Returns:
        Tuple of (market, outcome, token_id)
    """
    print("Finding the best market to bet on...")
    
    # Get ALL active markets (not just sports)
    all_markets = get_all_active_markets()
    
    if not all_markets:
        print("No active markets found")
        return None, None, None
    
    print(f"Checking {len(all_markets)} markets for trading opportunities...")
    
    # Strategy 1: Try to find markets with active order books
    best_market = None
    best_liquidity = 0
    best_outcome = None
    best_token_id = None
    
    # Check first 20 markets for order books (to avoid rate limiting)
    for i, market in enumerate(all_markets[:20]):
        print(f"Checking market {i+1}/20: {market.get('question', 'Unknown')[:50]}...")
            
        token_ids = parse_token_ids(market)
        outcomes = parse_outcomes(market)
        
        if not token_ids or not outcomes or len(token_ids) != len(outcomes):
            continue
        
        for j, token_id in enumerate(token_ids):
            order_book = get_order_book(token_id)
            
            if not order_book:
                continue
                
            # Check for bids and asks
            bids = order_book.get("bids", [])
            asks = order_book.get("asks", [])
            
            if not bids or not asks:
                continue
            
            # Calculate liquidity score
            try:
                best_bid = float(bids[0]["price"])
                best_ask = float(asks[0]["price"])
                
                spread = best_ask - best_bid
                bid_volume = sum(float(bid["size"]) for bid in bids[:3])
                ask_volume = sum(float(ask["size"]) for ask in asks[:3])
                
                if spread > 0:
                    liquidity_score = (bid_volume + ask_volume) / spread
                else:
                    liquidity_score = bid_volume + ask_volume
                
                if liquidity_score > best_liquidity:
                    best_liquidity = liquidity_score
                    best_market = market
                    best_outcome = outcomes[j]
                    best_token_id = token_id
                    
                    print(f"✅ Found liquid market: {market.get('question', 'Unknown')[:50]}...")
                    print(f"Liquidity score: {liquidity_score:.2f}")
                    
            except (IndexError, ValueError, KeyError):
                continue
    
    # If we found a liquid market, use it
    if best_market:
        print(f"\n✅ Best market selected (with order book):")
        print(f"Market: {best_market.get('question')}")
        print(f"Outcome: {best_outcome}")
        print(f"Liquidity score: {best_liquidity:.2f}")
        return best_market, best_outcome, best_token_id
    
    # Strategy 2: Fallback - use market with highest volume
    print("\nNo markets with active order books found. Using volume-based selection...")
    
    # Sort markets by volume (highest first)
    volume_markets = []
    for market in all_markets:
        try:
            volume = float(market.get("volume", 0))
            if volume > 0:
                volume_markets.append((market, volume))
        except:
            continue
    
    if not volume_markets:
        print("No markets with volume data found")
        return None, None, None
    
    # Sort by volume
    volume_markets.sort(key=lambda x: x[1], reverse=True)
    
    # Try the top 5 highest volume markets
    for market, volume in volume_markets[:5]:
        token_ids = parse_token_ids(market)
        outcomes = parse_outcomes(market)
        
        if token_ids and outcomes and len(token_ids) == len(outcomes):
            # Use the first outcome (usually "Yes")
            selected_market = market
            selected_outcome = outcomes[0]
            selected_token_id = token_ids[0]
            
            print(f"\n✅ Selected high-volume market:")
            print(f"Market: {selected_market.get('question')}")
            print(f"Volume: ${volume:,.2f}")
            print(f"Outcome: {selected_outcome}")
            
            return selected_market, selected_outcome, selected_token_id
    
    print("No suitable markets found")
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