#!/usr/bin/env python3
"""
Check Polymarket Trading Balance
This script checks your actual trading balance on Polymarket using the CLOB client
"""

import os
import sys
from dotenv import load_dotenv
from web3 import Web3
from eth_account import Account

# Load environment variables
load_dotenv()

# Import py-clob-client
try:
    from py_clob_client.client import ClobClient
    from py_clob_client.constants import POLYGON
except ImportError:
    print("❌ py-clob-client not installed. Installing...")
    os.system("pip install py-clob-client")
    from py_clob_client.client import ClobClient
    from py_clob_client.constants import POLYGON

# Constants
USDC_CONTRACT = "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359"
RPC_URL = "https://polygon-rpc.com"

def check_polymarket_balance():
    """Check both wallet and Polymarket trading balances"""
    print("=" * 60)
    print("POLYMARKET TRADING BALANCE CHECKER")
    print("=" * 60)
    
    # Get private key
    private_key = os.getenv("POLYGON_WALLET_PRIVATE_KEY", "")
    if not private_key:
        print("❌ No private key found in environment variables")
        return
    
    if not private_key.startswith("0x"):
        private_key = "0x" + private_key
    
    # Setup Web3
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        print("❌ Failed to connect to Polygon network")
        return
    
    account = Account.from_key(private_key)
    wallet_address = account.address
    
    print(f"Wallet address: {wallet_address}")
    print()
    
    # Check wallet USDC balance
    print("1. WALLET USDC BALANCE:")
    print("-" * 30)
    try:
        usdc_abi = [
            {
                "constant": True,
                "inputs": [{"name": "account", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "", "type": "uint256"}],
                "payable": False,
                "stateMutability": "view",
                "type": "function"
            }
        ]
        
        usdc_contract = w3.eth.contract(address=USDC_CONTRACT, abi=usdc_abi)
        wallet_balance = usdc_contract.functions.balanceOf(wallet_address).call()
        wallet_balance_usdc = wallet_balance / 10**6
        
        print(f"Wallet USDC: ${wallet_balance_usdc:.6f}")
        
    except Exception as e:
        print(f"❌ Error checking wallet balance: {e}")
        wallet_balance_usdc = 0
    
    print()
    
    # Check MATIC balance for gas
    print("2. MATIC BALANCE (for gas):")
    print("-" * 30)
    try:
        matic_balance = w3.eth.get_balance(wallet_address)
        matic_balance_eth = matic_balance / 10**18
        print(f"MATIC: {matic_balance_eth:.6f}")
        
        if matic_balance_eth < 0.01:
            print("⚠️ Low MATIC! You need MATIC for gas fees.")
        else:
            print("✅ MATIC balance sufficient for gas fees.")
            
    except Exception as e:
        print(f"❌ Error checking MATIC balance: {e}")
    
    print()
    
    # Check Polymarket trading balance
    print("3. POLYMARKET TRADING BALANCE:")
    print("-" * 30)
    try:
        # Initialize CLOB client
        client = ClobClient(
            host="https://clob.polymarket.com",
            key=private_key,
            chain_id=POLYGON
        )
        
        # Try to set up API credentials
        try:
            api_creds = client.create_or_derive_api_creds()
            client.set_api_creds(api_creds)
            print("✅ API credentials set up successfully")
        except Exception as e:
            print(f"⚠️ API credentials warning: {e}")
        
        # Try to get balance from Polymarket
        try:
            # Method 1: Try to get balance directly
            balance_info = client.get_balance()
            if balance_info:
                print(f"Polymarket Balance: {balance_info}")
            else:
                print("❌ Could not retrieve Polymarket balance")
        except Exception as e:
            print(f"⚠️ Balance method 1 failed: {e}")
            
            # Method 2: Try alternative balance check
            try:
                # Check if we can access the client at all
                print("Checking client connectivity...")
                # This will test if the client is working
                test_token = "21742633143463906290569050155826241533067272736897614950488156847949938836455"
                price_data = client.get_last_trade_price(test_token)
                if price_data:
                    print("✅ CLOB client is working")
                    print("💡 Your USDC might need to be deposited into Polymarket")
                    print("💡 Or the balance API might not be available")
                else:
                    print("❌ CLOB client connectivity issues")
            except Exception as e2:
                print(f"❌ CLOB client test failed: {e2}")
                print("💡 This might be why trades are failing")
        
    except Exception as e:
        print(f"❌ Error initializing Polymarket client: {e}")
    
    print()
    print("4. DIAGNOSIS:")
    print("-" * 30)
    
    if wallet_balance_usdc > 0:
        print(f"✅ You have ${wallet_balance_usdc:.2f} USDC in your wallet")
        print("💡 Possible issues:")
        print("   - USDC needs to be deposited into Polymarket")
        print("   - API credentials not properly set up")
        print("   - Polymarket balance API not accessible")
        print("   - Network connectivity issues")
        print()
        print("🔧 SOLUTIONS TO TRY:")
        print("   1. Visit polymarket.com and manually deposit USDC")
        print("   2. Try placing a small manual trade first")
        print("   3. Check if your wallet is properly connected to Polymarket")
        print("   4. Verify API credentials are working")
    else:
        print("❌ No USDC found in wallet")
        print("💡 You need to add USDC to your wallet first")

if __name__ == "__main__":
    check_polymarket_balance() 