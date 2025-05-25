#!/usr/bin/env python3
import requests
import json
import os
import time
from typing import Dict, Any, Optional, List, Tuple
from dotenv import load_dotenv
from web3 import Web3
from eth_account import Account
from nba_markets import get_active_sports_markets, parse_token_ids, parse_outcomes, classify_market

# Load environment variables
load_dotenv()

# Constants
POLYMARKET_EXCHANGE = "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E"  # Polymarket Exchange contract
USDC_CONTRACT = "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359"  # USDC on Polygon
RPC_URL = "https://polygon-rpc.com"
CLOB_API_URL = "https://clob.polymarket.com"

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
    
    if balance == 0:
        print("You don't have any USDC in your wallet.")
        return False
    
    # Check current allowance
    current_allowance = usdc_contract.functions.allowance(
        wallet_address, 
        POLYMARKET_EXCHANGE
    ).call()
    current_allowance_usdc = current_allowance / 10**6
    
    print(f"Current Polymarket allowance: {current_allowance_usdc} USDC")
    
    # If allowance is sufficient, return True
    return current_allowance > 0 and current_allowance >= 1_000_000  # 1 USDC minimum

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
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
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

def select_market_and_outcome(markets: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], str, str]:
    """
    Let user select a market and outcome to bet on
    """
    print("\nAvailable markets:")
    for i, market in enumerate(markets):
        print(f"{i+1}. {market.get('question', 'Unknown')}")
    
    # Select market
    while True:
        try:
            market_index = int(input("\nSelect market number: ")) - 1
            if 0 <= market_index < len(markets):
                selected_market = markets[market_index]
                break
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Get outcomes for the selected market
    outcomes = parse_outcomes(selected_market)
    token_ids = parse_token_ids(selected_market)
    
    if not outcomes or not token_ids or len(outcomes) != len(token_ids):
        print("Invalid market data")
        return None, None, None
    
    # Display outcomes
    print("\nAvailable outcomes:")
    for i, outcome in enumerate(outcomes):
        print(f"{i+1}. {outcome}")
    
    # Select outcome
    while True:
        try:
            outcome_index = int(input("\nSelect outcome number: ")) - 1
            if 0 <= outcome_index < len(outcomes):
                selected_outcome = outcomes[outcome_index]
                selected_token_id = token_ids[outcome_index]
                break
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")
    
    return selected_market, selected_outcome, selected_token_id

def place_bet_on_market(
    token_id: str, 
    market_question: str, 
    outcome: str, 
    wallet_address: str, 
    private_key: str,
    w3: Web3
) -> None:
    """
    Place a bet of 1 USDC on a specific market outcome
    """
    # Fixed amount - 1 USDC worth of shares
    amount = 1.0
    
    print("\n" + "=" * 70)
    print(f"PLACING BET: {amount} USDC on {outcome}")
    print(f"MARKET: {market_question}")
    print("=" * 70)
    
    # Confirm the bet
    confirm = input("\nConfirm bet (y/n): ").strip().lower()
    if confirm != 'y':
        print("Bet cancelled")
        return
    
    # Place the order
    tx_hash = place_market_order(token_id, "buy", amount, wallet_address, private_key, w3)
    
    if tx_hash:
        print("\n" + "=" * 70)
        print(f"✅ BET PLACED SUCCESSFULLY!")
        print(f"Amount: {amount} USDC")
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
    Main function to place a bet on a Polymarket sports market
    """
    print("=" * 70)
    print("POLYMARKET SPORTS BETTING BOT")
    print("=" * 70)
    
    try:
        # Step 1: Get wallet info and web3 connection
        wallet_address, private_key, w3 = get_wallet_info()
        
        # Step 2: Check USDC approval
        if not check_usdc_approval(wallet_address, w3):
            print("\nYou need to approve USDC spending first.")
            print("Run 'python approve_usdc.py' to approve USDC.")
            return
        
        # Step 3: Get active sports markets
        print("\nFetching sports markets...")
        sports_markets = get_active_sports_markets()
        
        if not sports_markets:
            print("\nNo active sports markets found. Please try again later.")
            return
        
        # Step 4: Let user select market and outcome
        selected_market, selected_outcome, selected_token_id = select_market_and_outcome(sports_markets)
        
        if not selected_market or not selected_outcome or not selected_token_id:
            print("Failed to select market and outcome.")
            return
        
        # Step 5: Place the bet
        place_bet_on_market(
            selected_token_id,
            selected_market.get("question", "Unknown Market"),
            selected_outcome,
            wallet_address,
            private_key,
            w3
        )
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 