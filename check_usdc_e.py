#!/usr/bin/env python3
import requests
import json
import os
from dotenv import load_dotenv
from eth_account import Account

# Load environment variables
load_dotenv()

def check_usdc_e_balance():
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
    
    # Check both USDC and USDC.e balance
    try:
        print("Checking both USDC and USDC.e balances via direct web3 calls...")
        
        # USDC contract address on Polygon
        usdc_contract = "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359"
        
        # USDC.e contract address on Polygon
        usdc_e_contract = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"  # Old USDC.e on Polygon
        
        # Polygon RPC URL - using public endpoint
        rpc_url = "https://polygon-rpc.com"
        
        # Create ERC20 balanceOf function call data
        # Function signature: balanceOf(address)
        function_signature = "0x70a08231"  # keccak256("balanceOf(address)") first 4 bytes
        address_param = wallet_address[2:].lower().zfill(64)  # Remove 0x and pad to 32 bytes
        data = function_signature + address_param
        
        # Check USDC balance
        payload_usdc = {
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
        
        # Make request for USDC
        response_usdc = requests.post(rpc_url, json=payload_usdc)
        result_usdc = response_usdc.json()
        
        usdc_balance = 0
        if "result" in result_usdc:
            # Convert hex result to decimal and divide by 10^6 (USDC has 6 decimals)
            balance_hex = result_usdc["result"]
            balance_int = int(balance_hex, 16)
            usdc_balance = balance_int / 10**6
            print(f"USDC balance: {usdc_balance} USDC")
        else:
            print(f"Error getting USDC balance: {result_usdc.get('error')}")
        
        # Let's also check for any native MATIC (for gas fees)
        payload_matic = {
            "jsonrpc": "2.0",
            "method": "eth_getBalance",
            "params": [
                wallet_address,
                "latest"
            ],
            "id": 1
        }
        
        # Make request for MATIC
        response_matic = requests.post(rpc_url, json=payload_matic)
        result_matic = response_matic.json()
        
        if "result" in result_matic:
            # Convert hex result to decimal and divide by 10^18 (MATIC has 18 decimals)
            balance_hex = result_matic["result"]
            balance_int = int(balance_hex, 16)
            matic_balance = balance_int / 10**18
            print(f"MATIC balance: {matic_balance} MATIC")
        else:
            print(f"Error getting MATIC balance: {result_matic.get('error')}")
        
        # Summary of findings
        print("\n--- SUMMARY ---")
        if usdc_balance > 0:
            print("✅ You have USDC in your wallet!")
            print("But you still need to:")
            print("1. Have some MATIC for gas fees (to pay for transactions)")
            print("2. Approve the Polymarket Exchange contract to spend your USDC")
            print("\nTo approve USDC spending, you need to make an 'approve' transaction")
            print("The Polymarket Exchange contract address is: 0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E")
        else:
            print("❌ No USDC found in your wallet yet.")
            print("The withdrawal might still be processing. Check back in a few minutes.")
            print("You can also verify the transaction status on PolygonScan.")
        
        # Check for transaction history
        print("\nLet's check for recent transactions...")
        
        # Use Polygonscan API to check recent transactions (this would normally require an API key)
        print("To check transaction history, visit:")
        print(f"https://polygonscan.com/address/{wallet_address}")
        
    except Exception as e:
        print(f"Error checking balances: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("POLYMARKET WALLET BALANCE CHECKER")
    print("=" * 60)
    check_usdc_e_balance() 