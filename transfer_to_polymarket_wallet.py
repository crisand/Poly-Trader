#!/usr/bin/env python3
"""
Transfer USDC to Polymarket Wallet
This script transfers USDC from the bot wallet to your Polymarket wallet
"""

import os
from dotenv import load_dotenv
from web3 import Web3
from eth_account import Account

# Load environment variables
load_dotenv()

def transfer_to_polymarket_wallet():
    """Transfer USDC from bot wallet to Polymarket wallet"""
    print("=" * 60)
    print("TRANSFER USDC TO POLYMARKET WALLET")
    print("=" * 60)
    
    # Setup Web3
    w3 = Web3(Web3.HTTPProvider("https://polygon-rpc.com"))
    if not w3.is_connected():
        print("❌ Failed to connect to Polygon network")
        return False
    
    # Get private key
    private_key = os.getenv("POLYGON_WALLET_PRIVATE_KEY", "")
    if not private_key.startswith("0x"):
        private_key = "0x" + private_key
    
    account = Account.from_key(private_key)
    from_wallet = account.address
    to_wallet = "0x3E1B662bB2FD32D7eb6c57221296205C9D48D012"  # Your Polymarket wallet
    
    print(f"From: {from_wallet}")
    print(f"To: {to_wallet}")
    print()
    
    # USDC contract setup
    usdc_contract = "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359"
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
    
    usdc = w3.eth.contract(address=usdc_contract, abi=usdc_abi)
    
    # Check current balance
    current_balance = usdc.functions.balanceOf(from_wallet).call()
    current_balance_usdc = current_balance / 10**6
    
    print(f"💰 Current balance: ${current_balance_usdc:.6f} USDC")
    
    if current_balance_usdc < 0.01:
        print("❌ Insufficient USDC to transfer")
        return False
    
    # Reserve small amount for gas (keep $0.01)
    transfer_amount_usdc = current_balance_usdc - 0.01
    transfer_amount_wei = int(transfer_amount_usdc * 10**6)
    
    print(f"💰 Transferring: ${transfer_amount_usdc:.6f} USDC")
    print(f"💰 Keeping for gas: $0.01 USDC")
    print()
    
    try:
        # Build transaction
        transaction = usdc.functions.transfer(
            to_wallet,
            transfer_amount_wei
        ).build_transaction({
            'from': from_wallet,
            'gas': 100000,
            'gasPrice': w3.eth.gas_price,
            'nonce': w3.eth.get_transaction_count(from_wallet),
        })
        
        # Sign transaction
        signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
        
        # Send transaction
        print("🔄 Sending transfer transaction...")
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        tx_hash_hex = tx_hash.hex()
        
        print(f"📤 Transaction sent: {tx_hash_hex}")
        print(f"🔗 View on PolygonScan: https://polygonscan.com/tx/{tx_hash_hex}")
        
        # Wait for confirmation
        print("⏳ Waiting for confirmation...")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
        
        if receipt.status == 1:
            print("✅ Transfer successful!")
            
            # Check new balances
            new_from_balance = usdc.functions.balanceOf(from_wallet).call() / 10**6
            new_to_balance = usdc.functions.balanceOf(to_wallet).call() / 10**6
            
            print(f"💰 Bot wallet balance: ${new_from_balance:.6f} USDC")
            print(f"💰 Polymarket wallet balance: ${new_to_balance:.6f} USDC")
            print()
            print("🎉 SUCCESS! Your USDC is now in your Polymarket wallet!")
            print("Now you can use polymarket.com to deposit it properly.")
            
            return True
        else:
            print("❌ Transaction failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error during transfer: {e}")
        return False

def main():
    """Main function"""
    print("🔄 TRANSFERRING USDC TO YOUR POLYMARKET WALLET")
    print("This will move your USDC from the bot wallet to your Polymarket wallet")
    print()
    
    success = transfer_to_polymarket_wallet()
    
    if success:
        print("\n🎯 NEXT STEPS:")
        print("1. Go to https://polymarket.com")
        print("2. Connect wallet 0x3E1B662bB2FD32D7eb6c57221296205C9D48D012")
        print("3. Use the official 'Deposit' feature")
        print("4. Your trading will work perfectly!")
    else:
        print("\n❌ Transfer failed. Please check your setup.")

if __name__ == "__main__":
    main() 