#!/usr/bin/env python3
"""
Check Both Wallet Addresses
This script checks USDC balances in both wallet addresses
"""

import os
from dotenv import load_dotenv
from web3 import Web3

# Load environment variables
load_dotenv()

def check_both_wallets():
    """Check USDC balances in both wallet addresses"""
    print("=" * 60)
    print("CHECKING BOTH WALLET ADDRESSES")
    print("=" * 60)
    
    # Setup Web3
    w3 = Web3(Web3.HTTPProvider("https://polygon-rpc.com"))
    if not w3.is_connected():
        print("❌ Failed to connect to Polygon network")
        return
    
    # Wallet addresses
    wallet1 = "0xb3A635E05d1a159b0d2658d3F0e7D59cd4643633"  # From private key
    wallet2 = "0x3E1B662bB2FD32D7eb6c57221296205C9D48D012"  # Polymarket wallet
    
    # USDC contract
    usdc_contract = "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359"
    
    # USDC ABI
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
    
    usdc = w3.eth.contract(address=usdc_contract, abi=usdc_abi)
    
    print("💰 WALLET BALANCE COMPARISON:")
    print()
    
    # Check Wallet 1 (Private Key Wallet)
    balance1 = usdc.functions.balanceOf(wallet1).call()
    balance1_usdc = balance1 / 10**6
    print(f"WALLET 1 (Private Key): {wallet1}")
    print(f"   USDC Balance: ${balance1_usdc:.6f}")
    print(f"   This is the wallet used by your trading bot")
    print()
    
    # Check Wallet 2 (Polymarket Wallet)
    balance2 = usdc.functions.balanceOf(wallet2).call()
    balance2_usdc = balance2 / 10**6
    print(f"WALLET 2 (Polymarket): {wallet2}")
    print(f"   USDC Balance: ${balance2_usdc:.6f}")
    print(f"   This is the wallet you're checking on Polymarket")
    print()
    
    print("🔍 ANALYSIS:")
    if balance1_usdc > 0:
        print(f"   ✅ Wallet 1 has ${balance1_usdc:.2f} USDC")
    else:
        print("   ❌ Wallet 1 has no USDC")
    
    if balance2_usdc > 0:
        print(f"   ✅ Wallet 2 has ${balance2_usdc:.2f} USDC")
    else:
        print("   ❌ Wallet 2 has no USDC")
    
    print()
    print("🎯 THE ISSUE:")
    print("   Your trading bot is using WALLET 1, but you're checking WALLET 2")
    print("   on Polymarket. These are DIFFERENT wallets!")
    print()
    
    print("🔧 SOLUTIONS:")
    print("   1. Connect WALLET 1 to Polymarket:")
    print(f"      - Import this private key to MetaMask: {wallet1}")
    print("      - Connect this wallet to polymarket.com")
    print("      - Your funds will appear there")
    print()
    print("   2. OR transfer funds from WALLET 1 to WALLET 2:")
    print("      - Send USDC from the private key wallet to your Polymarket wallet")
    print("      - Then use Polymarket normally")
    print()
    print("   3. OR update your bot to use WALLET 2:")
    print("      - Export private key from WALLET 2")
    print("      - Update your .env file with the new private key")
    
    return balance1_usdc, balance2_usdc

def main():
    """Main function"""
    balance1, balance2 = check_both_wallets()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"💰 Private Key Wallet: ${balance1:.2f} USDC")
    print(f"💰 Polymarket Wallet: ${balance2:.2f} USDC")
    print("🔑 You need to connect the correct wallet to see your funds!")

if __name__ == "__main__":
    main() 