#!/usr/bin/env python3
import requests
import json
import os
from dotenv import load_dotenv
from eth_account import Account

# Load environment variables
load_dotenv()

def check_usdc_balance():
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
    
    # Check USDC balance using Moralis API (doesn't require API key for basic requests)
    try:
        print("Checking USDC balance via direct web3 call...")
        
        # USDC contract address on Polygon
        usdc_contract = "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359"
        
        # Polygon RPC URL - using public endpoint
        rpc_url = "https://polygon-rpc.com"
        
        # Create ERC20 balanceOf function call data
        # Function signature: balanceOf(address)
        function_signature = "0x70a08231"  # keccak256("balanceOf(address)") first 4 bytes
        address_param = wallet_address[2:].lower().zfill(64)  # Remove 0x and pad to 32 bytes
        data = function_signature + address_param
        
        # Create JSON-RPC request
        payload = {
            "jsonrpc": "2.0",
            "method": "eth_call",
            "params": [
                {
                    "to": usdc_contract,
                    "data": data
                },
                "latest"
            ],
            "id": 1
        }
        
        # Make request
        response = requests.post(rpc_url, json=payload)
        result = response.json()
        
        if "result" in result:
            # Convert hex result to decimal and divide by 10^6 (USDC has 6 decimals)
            balance_hex = result["result"]
            balance_int = int(balance_hex, 16)
            balance_usdc = balance_int / 10**6
            
            print(f"USDC balance: {balance_usdc} USDC")
            
            if balance_usdc > 0:
                print("\nLooks like you have USDC in your wallet!")
                print("But you still need to approve the Polymarket Exchange contract to spend it.")
                print("\nTo approve USDC spending:")
                print("1. You need to make an 'approve' transaction to the USDC contract")
                print("2. This tells USDC that the Polymarket Exchange can spend your tokens")
                print("3. The Polymarket Exchange contract address is: 0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E")
            else:
                print("\nNo USDC found in your wallet yet.")
                print("The withdrawal might still be processing. Check back in a few minutes.")
                print("You can also verify the transaction status on PolygonScan.")
        else:
            print(f"Error getting balance: {result.get('error')}")
    except Exception as e:
        print(f"Error checking USDC balance: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("POLYMARKET USDC BALANCE CHECKER")
    print("=" * 60)
    check_usdc_balance() 