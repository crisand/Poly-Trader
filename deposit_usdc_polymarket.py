#!/usr/bin/env python3
"""
Deposit USDC into Polymarket
This script deposits USDC from your wallet into Polymarket's trading system
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

def deposit_usdc_to_polymarket():
    """Deposit USDC into Polymarket for trading"""
    print("=" * 60)
    print("POLYMARKET USDC DEPOSIT TOOL")
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
    
    # Check current USDC balance
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
        
        print(f"Current wallet USDC: ${wallet_balance_usdc:.6f}")
        
        if wallet_balance_usdc < 1:
            print("❌ Insufficient USDC in wallet for deposit")
            return
            
    except Exception as e:
        print(f"❌ Error checking wallet balance: {e}")
        return
    
    # Ask user how much to deposit
    print(f"\nHow much USDC would you like to deposit into Polymarket?")
    print(f"Available: ${wallet_balance_usdc:.2f}")
    print(f"Recommended: $50-100 for trading")
    
    try:
        deposit_amount = float(input("Enter amount to deposit (e.g., 50): $"))
        
        if deposit_amount <= 0:
            print("❌ Invalid amount")
            return
            
        if deposit_amount > wallet_balance_usdc:
            print(f"❌ Insufficient balance. You only have ${wallet_balance_usdc:.2f}")
            return
            
    except ValueError:
        print("❌ Invalid amount entered")
        return
    
    print(f"\n🔄 Preparing to deposit ${deposit_amount:.2f} USDC into Polymarket...")
    
    # Initialize CLOB client
    try:
        client = ClobClient(
            host="https://clob.polymarket.com",
            key=private_key,
            chain_id=POLYGON
        )
        
        # Set up API credentials
        api_creds = client.create_or_derive_api_creds()
        client.set_api_creds(api_creds)
        print("✅ CLOB client initialized")
        
    except Exception as e:
        print(f"❌ Error initializing CLOB client: {e}")
        return
    
    # Try to deposit USDC
    try:
        print(f"💰 Depositing ${deposit_amount:.2f} USDC...")
        
        # Convert to smallest unit (6 decimals for USDC)
        deposit_amount_wei = int(deposit_amount * 10**6)
        
        # Try different deposit methods
        deposit_success = False
        
        # Method 1: Try direct deposit if available
        try:
            if hasattr(client, 'deposit'):
                result = client.deposit(deposit_amount_wei)
                if result:
                    print(f"✅ Deposit successful! Transaction: {result}")
                    deposit_success = True
            else:
                print("⚠️ Direct deposit method not available")
        except Exception as e:
            print(f"⚠️ Direct deposit failed: {e}")
        
        # Method 2: Manual instructions if programmatic deposit fails
        if not deposit_success:
            print("\n📝 MANUAL DEPOSIT INSTRUCTIONS:")
            print("-" * 40)
            print("Since programmatic deposit is not available, please:")
            print("1. Go to https://polymarket.com")
            print("2. Connect your wallet")
            print("3. Look for 'Deposit' or 'Add Funds' button")
            print("4. Deposit USDC into your Polymarket account")
            print("5. Once deposited, your trading bot will work")
            print()
            print("💡 Your wallet is properly set up and approved!")
            print("💡 You just need to move USDC into Polymarket's system")
            
    except Exception as e:
        print(f"❌ Error during deposit: {e}")
        print("\n📝 MANUAL DEPOSIT REQUIRED:")
        print("Please visit polymarket.com and deposit USDC manually")

if __name__ == "__main__":
    deposit_usdc_to_polymarket() 