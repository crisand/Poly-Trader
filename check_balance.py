#!/usr/bin/env python3
import requests
import os
from dotenv import load_dotenv
from eth_account import Account

# Load environment variables
load_dotenv()

def check_wallet_balance():
    """Check the balance of USDC in the Polygon wallet"""
    # Get private key from environment
    private_key = os.getenv("POLYGON_WALLET_PRIVATE_KEY", "")
    
    if not private_key:
        print("No private key found in environment variables")
        return
    
    # Add 0x prefix if missing
    if not private_key.startswith("0x"):
        private_key = "0x" + private_key
    
    # Get wallet address from private key
    try:
        account = Account.from_key(private_key)
        wallet_address = account.address
        print(f"Wallet address: {wallet_address}")
    except Exception as e:
        print(f"Error getting wallet address: {e}")
        return
    
    # Check MATIC balance (native token)
    try:
        # Using Polygon scan API
        polygon_api_url = "https://api.polygonscan.com/api"
        
        params = {
            "module": "account",
            "action": "balance",
            "address": wallet_address,
            "tag": "latest"
        }
        
        response = requests.get(polygon_api_url, params=params)
        data = response.json()
        
        if data.get("status") == "1":
            # Convert from wei to MATIC
            matic_balance = int(data.get("result", "0")) / 10**18
            print(f"MATIC balance: {matic_balance}")
        else:
            print(f"Error getting MATIC balance: {data.get('message')}")
    except Exception as e:
        print(f"Error checking MATIC balance: {e}")
    
    # Check USDC balance
    try:
        # USDC contract address on Polygon
        usdc_contract = "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359"
        
        params = {
            "module": "account",
            "action": "tokenbalance",
            "contractaddress": usdc_contract,
            "address": wallet_address,
            "tag": "latest"
        }
        
        response = requests.get(polygon_api_url, params=params)
        data = response.json()
        
        if data.get("status") == "1":
            # Convert from smallest unit (6 decimals for USDC)
            usdc_balance = int(data.get("result", "0")) / 10**6
            print(f"USDC balance: {usdc_balance}")
        else:
            print(f"Error getting USDC balance: {data.get('message')}")
    except Exception as e:
        print(f"Error checking USDC balance: {e}")
    
    # Check Polymarket contract allowance
    try:
        # Polymarket Exchange contract address
        exchange_contract = "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E"
        
        # This would require more complex Web3 calls that are harder to implement
        # in a simple script, so just providing a note about it
        print("\nNote: To place bets, you need to:")
        print("1. Have USDC in your wallet")
        print("2. Approve the Polymarket Exchange contract to spend your USDC")
        print(f"3. The Exchange contract address is {exchange_contract}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("POLYMARKET WALLET BALANCE CHECKER")
    print("=" * 60)
    check_wallet_balance() 