#!/usr/bin/env python3
"""
Deposit All USDC to Polymarket
This script deposits all available USDC from your wallet into Polymarket's trading system
"""

import os
import sys
import time
from dotenv import load_dotenv
from web3 import Web3
from eth_account import Account

# Load environment variables
load_dotenv()

# Constants
USDC_CONTRACT = "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359"
POLYMARKET_EXCHANGE = "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E"
RPC_URL = "https://polygon-rpc.com"

def deposit_all_usdc():
    """Deposit all available USDC into Polymarket for trading"""
    print("🚀 Starting automatic USDC deposit process...")
    print("=" * 60)
    print("DEPOSIT ALL USDC TO POLYMARKET")
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
    
    # Get current USDC balance
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
                {"name": "value", "type": "uint256"}
            ],
            "name": "transfer",
            "outputs": [{"name": "", "type": "bool"}],
            "payable": False,
            "stateMutability": "nonpayable",
            "type": "function"
        }
    ]
    
    usdc_contract = w3.eth.contract(address=USDC_CONTRACT, abi=usdc_abi)
    current_balance = usdc_contract.functions.balanceOf(wallet_address).call()
    current_balance_usdc = current_balance / 10**6
    
    print(f"Current wallet USDC: ${current_balance_usdc:.6f}")
    
    if current_balance_usdc < 1.0:
        print("❌ Insufficient USDC balance to deposit (minimum $1)")
        return False
    
    # Reserve a small amount for gas fees (keep $0.50 in wallet)
    reserve_amount = 0.5
    deposit_amount = current_balance_usdc - reserve_amount
    
    if deposit_amount <= 0:
        print("❌ Not enough USDC to deposit after reserving for gas")
        return False
    
    print(f"💰 Depositing: ${deposit_amount:.2f} USDC")
    print(f"💰 Keeping in wallet: ${reserve_amount:.2f} USDC")
    
    try:
        # Convert to wei (6 decimals for USDC)
        deposit_amount_wei = int(deposit_amount * 10**6)
        
        # Get current gas price
        gas_price = w3.eth.gas_price
        
        # Build transaction
        transaction = usdc_contract.functions.transfer(
            POLYMARKET_EXCHANGE,
            deposit_amount_wei
        ).build_transaction({
            'from': wallet_address,
            'gas': 100000,  # Standard gas limit for ERC20 transfer
            'gasPrice': gas_price,
            'nonce': w3.eth.get_transaction_count(wallet_address),
        })
        
        # Sign transaction
        signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
        
        # Send transaction
        print(f"🔄 Sending deposit transaction...")
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        tx_hash_hex = tx_hash.hex()
        
        print(f"📤 Transaction sent: {tx_hash_hex}")
        print(f"🔗 View on PolygonScan: https://polygonscan.com/tx/{tx_hash_hex}")
        
        # Wait for confirmation
        print("⏳ Waiting for transaction confirmation...")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
        
        if receipt.status == 1:
            print("✅ USDC deposit successful!")
            print(f"💰 Deposited ${deposit_amount:.2f} USDC to Polymarket")
            print(f"⛽ Gas used: {receipt.gasUsed:,}")
            
            # Check new balance
            new_balance = usdc_contract.functions.balanceOf(wallet_address).call()
            new_balance_usdc = new_balance / 10**6
            print(f"💰 Remaining wallet balance: ${new_balance_usdc:.6f} USDC")
            
            return True
        else:
            print("❌ Transaction failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error during deposit: {e}")
        return False

def main():
    """Main function"""
    print("💰 DEPOSIT ALL USDC TO POLYMARKET")
    print("This will deposit all your USDC (minus gas reserve) into Polymarket")
    print()
    
    success = deposit_all_usdc()
    
    if success:
        print("\n🎉 DEPOSIT SUCCESSFUL!")
        print("Your trading bot should now work without 'insufficient balance' errors")
        print("\n🔍 Testing bot balance recognition...")
        
        # Test the balance recognition
        try:
            import subprocess
            result = subprocess.run(
                ["python3", "real_auto_trader.py", "--test-balance"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if "Total Available" in result.stdout:
                print("✅ Bot can now recognize deposited funds")
            else:
                print("⚠️ Bot may still need time to recognize deposited funds")
        except:
            print("💡 You can now test your trading bot")
    else:
        print("\n❌ DEPOSIT FAILED")
        print("Please check your wallet balance and try again")

if __name__ == "__main__":
    main() 