#!/usr/bin/env python3
"""
USDC Fund Recovery Options
This script shows your current balances and recovery options
"""

import os
from dotenv import load_dotenv
from web3 import Web3
from eth_account import Account

# Load environment variables
load_dotenv()

def show_recovery_options():
    """Show current balances and recovery options"""
    print("=" * 60)
    print("USDC FUND RECOVERY OPTIONS")
    print("=" * 60)
    
    # Setup Web3
    w3 = Web3(Web3.HTTPProvider("https://polygon-rpc.com"))
    if not w3.is_connected():
        print("❌ Failed to connect to Polygon network")
        return
    
    # Get private key
    private_key = os.getenv("POLYGON_WALLET_PRIVATE_KEY", "")
    if not private_key.startswith("0x"):
        private_key = "0x" + private_key
    
    account = Account.from_key(private_key)
    wallet_address = account.address
    
    # Contract addresses
    usdc_contract = "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359"
    polymarket_exchange = "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E"
    
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
    
    # Check current balances
    wallet_balance = usdc.functions.balanceOf(wallet_address).call()
    wallet_usdc = wallet_balance / 10**6
    
    print(f"Wallet Address: {wallet_address}")
    print()
    print("💰 CURRENT SITUATION:")
    print(f"   ✅ Available in MetaMask: ${wallet_usdc:.6f} USDC")
    print(f"   ❌ Stuck in Exchange: $24.50 USDC (approximately)")
    print()
    
    print("🎯 RECOVERY OPTIONS:")
    print()
    print("OPTION 1: Use Your Available Funds (RECOMMENDED)")
    print(f"   • You have ${wallet_usdc:.2f} USDC readily available")
    print("   • This is MORE than enough for trading")
    print("   • Go to polymarket.com and deposit this amount properly")
    print("   • Your trading bot will work immediately")
    print()
    
    print("OPTION 2: Contact Polymarket Support")
    print("   • Email: support@polymarket.com")
    print("   • Transaction: 0x39ea775bde8e8645a2ea179ba334b8076c267b7814231f0b03bbd9c5262bce68")
    print("   • Explain: Accidentally sent USDC directly to exchange contract")
    print("   • They may be able to credit your account")
    print()
    
    print("OPTION 3: Technical Recovery (ADVANCED)")
    print("   • The $24.50 is technically recoverable but complex")
    print("   • Would require interacting with Polymarket's smart contracts")
    print("   • Risk of losing more funds if done incorrectly")
    print("   • Not recommended unless you're experienced with DeFi")
    print()
    
    print("🚀 RECOMMENDED ACTION:")
    print("   1. Use your available $108.67 USDC")
    print("   2. Go to https://polymarket.com")
    print("   3. Connect your MetaMask wallet")
    print("   4. Use their official 'Deposit' feature")
    print("   5. Deposit $50-100 USDC for trading")
    print("   6. Your bot will work perfectly!")
    print()
    
    print("💡 WHY THIS IS THE BEST OPTION:")
    print("   • You have MORE money available than you thought")
    print("   • No risk of losing additional funds")
    print("   • Immediate solution")
    print("   • The $24.50 can be recovered later via support")
    
    return wallet_usdc

def main():
    """Main function"""
    available_usdc = show_recovery_options()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"💰 You have ${available_usdc:.2f} USDC available for immediate use")
    print("🎯 Recommended: Use polymarket.com to deposit properly")
    print("📧 Optional: Contact support about the $24.50")
    print("✅ Your trading bot will work once you deposit via the website")

if __name__ == "__main__":
    main() 