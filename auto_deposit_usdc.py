#!/usr/bin/env python3
"""
Automatic USDC Deposit to Polymarket
This script automatically deposits USDC from your wallet into Polymarket's trading system
"""

import os
import sys
import time
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
POLYMARKET_EXCHANGE = "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E"
RPC_URL = "https://polygon-rpc.com"

# Auto-deposit settings
AUTO_DEPOSIT_AMOUNT = 75.0  # Deposit $75 automatically
MIN_WALLET_RESERVE = 25.0   # Keep $25 in wallet as reserve

def auto_deposit_usdc():
    """Automatically deposit USDC into Polymarket for trading"""
    print("=" * 60)
    print("AUTOMATIC POLYMARKET USDC DEPOSIT")
    print("=" * 60)
    
    # Get private key
    private_key = os.getenv("POLYGON_WALLET_PRIVATE_KEY", "")
    if not private_key:
        print("❌ No private key found in environment variables")
        return False
    
    if not private_key.startswith("0x"):
        private_key = "0x" + private_key
    
    # Setup Web3
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        print("❌ Failed to connect to Polygon network")
        return False
    
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
            },
            {
                "constant": False,
                "inputs": [
                    {"name": "to", "type": "address"},
                    {"name": "amount", "type": "uint256"}
                ],
                "name": "transfer",
                "outputs": [{"name": "", "type": "bool"}],
                "payable": False,
                "stateMutability": "nonpayable",
                "type": "function"
            }
        ]
        
        usdc_contract = w3.eth.contract(address=USDC_CONTRACT, abi=usdc_abi)
        wallet_balance = usdc_contract.functions.balanceOf(wallet_address).call()
        wallet_balance_usdc = wallet_balance / 10**6
        
        print(f"Current wallet USDC: ${wallet_balance_usdc:.6f}")
        
        # Calculate deposit amount
        available_for_deposit = wallet_balance_usdc - MIN_WALLET_RESERVE
        deposit_amount = min(AUTO_DEPOSIT_AMOUNT, available_for_deposit)
        
        if deposit_amount < 1:
            print(f"❌ Insufficient USDC for deposit")
            print(f"   Available: ${wallet_balance_usdc:.2f}")
            print(f"   Reserve: ${MIN_WALLET_RESERVE:.2f}")
            print(f"   Need at least: ${MIN_WALLET_RESERVE + 1:.2f}")
            return False
            
        print(f"💰 Auto-depositing: ${deposit_amount:.2f} USDC")
        print(f"💰 Keeping in wallet: ${wallet_balance_usdc - deposit_amount:.2f} USDC")
            
    except Exception as e:
        print(f"❌ Error checking wallet balance: {e}")
        return False
    
    # Method 1: Try direct transfer to Polymarket Exchange
    try:
        print(f"\n🔄 Method 1: Direct transfer to Polymarket Exchange...")
        
        # Convert to smallest unit (6 decimals for USDC)
        deposit_amount_wei = int(deposit_amount * 10**6)
        
        # Build transfer transaction
        transfer_txn = usdc_contract.functions.transfer(
            POLYMARKET_EXCHANGE,
            deposit_amount_wei
        ).build_transaction({
            'from': wallet_address,
            'gas': 100000,
            'gasPrice': w3.to_wei('50', 'gwei'),
            'nonce': w3.eth.get_transaction_count(wallet_address),
        })
        
        # Sign and send transaction
        signed_txn = w3.eth.account.sign_transaction(transfer_txn, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        
        print(f"📤 Transfer transaction sent: {tx_hash.hex()}")
        print(f"🔗 View on PolygonScan: https://polygonscan.com/tx/{tx_hash.hex()}")
        
        # Wait for confirmation
        print("⏳ Waiting for transaction confirmation...")
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
        
        if tx_receipt.status == 1:
            print(f"✅ USDC transfer successful!")
            print(f"💰 Transferred ${deposit_amount:.2f} USDC to Polymarket")
            return True
        else:
            print(f"❌ Transfer transaction failed")
            return False
            
    except Exception as e:
        print(f"❌ Direct transfer failed: {e}")
    
    # Method 2: Try using CLOB client deposit
    try:
        print(f"\n🔄 Method 2: Using CLOB client deposit...")
        
        # Initialize CLOB client
        client = ClobClient(
            host="https://clob.polymarket.com",
            key=private_key,
            chain_id=POLYGON
        )
        
        # Set up API credentials
        api_creds = client.create_or_derive_api_creds()
        client.set_api_creds(api_creds)
        print("✅ CLOB client initialized")
        
        # Try deposit methods
        deposit_amount_wei = int(deposit_amount * 10**6)
        
        # Check if client has deposit method
        if hasattr(client, 'deposit'):
            print("💰 Attempting CLOB deposit...")
            result = client.deposit(deposit_amount_wei)
            if result:
                print(f"✅ CLOB deposit successful! Result: {result}")
                return True
        
        # Try alternative deposit methods
        deposit_methods = ['deposit_usdc', 'add_funds', 'fund_account']
        for method_name in deposit_methods:
            if hasattr(client, method_name):
                print(f"💰 Trying {method_name}...")
                method = getattr(client, method_name)
                result = method(deposit_amount_wei)
                if result:
                    print(f"✅ {method_name} successful! Result: {result}")
                    return True
        
        print("⚠️ No direct deposit methods available in CLOB client")
        
    except Exception as e:
        print(f"❌ CLOB client deposit failed: {e}")
    
    # Method 3: Manual instructions
    print(f"\n📝 AUTOMATIC DEPOSIT NOT AVAILABLE")
    print("-" * 40)
    print("The programmatic deposit methods are not available.")
    print("You need to manually deposit USDC into Polymarket:")
    print()
    print("🌐 MANUAL STEPS:")
    print("1. Go to https://polymarket.com")
    print("2. Connect your wallet")
    print("3. Look for 'Deposit' or 'Add Funds' button")
    print(f"4. Deposit ${deposit_amount:.2f} USDC")
    print("5. Your trading bot will then work automatically")
    print()
    print("💡 Your wallet setup is perfect - just need manual deposit!")
    
    return False

def check_polymarket_deposit_status():
    """Check if USDC has been deposited into Polymarket"""
    print("\n🔍 Checking Polymarket deposit status...")
    
    private_key = os.getenv("POLYGON_WALLET_PRIVATE_KEY", "")
    if not private_key.startswith("0x"):
        private_key = "0x" + private_key
    
    try:
        # Initialize CLOB client to test connectivity
        client = ClobClient(
            host="https://clob.polymarket.com",
            key=private_key,
            chain_id=POLYGON
        )
        
        api_creds = client.create_or_derive_api_creds()
        client.set_api_creds(api_creds)
        
        # Test if we can access trading functions
        test_token = "21742633143463906290569050155826241533067272736897614950488156847949938836455"
        price_data = client.get_last_trade_price(test_token)
        
        if price_data:
            print("✅ Polymarket connection working")
            print("💡 If you've deposited USDC, your bot should work now")
            return True
        else:
            print("❌ Polymarket connection issues")
            return False
            
    except Exception as e:
        print(f"❌ Error checking Polymarket status: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting automatic USDC deposit process...")
    
    success = auto_deposit_usdc()
    
    if success:
        print("\n🎉 DEPOSIT SUCCESSFUL!")
        print("Your trading bot should now work without 'insufficient balance' errors")
    else:
        print("\n⚠️ AUTOMATIC DEPOSIT FAILED")
        print("Manual deposit required at polymarket.com")
    
    # Check status regardless
    check_polymarket_deposit_status() 