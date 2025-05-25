#!/usr/bin/env python3
"""
EMERGENCY FUND TRACER
This script traces all USDC transactions to find your missing $134 USDC
"""

import os
import requests
from dotenv import load_dotenv
from web3 import Web3

# Load environment variables
load_dotenv()

def emergency_fund_trace():
    """Emergency trace of all USDC movements"""
    print("🚨" * 30)
    print("EMERGENCY FUND TRACER - FINDING YOUR $134 USDC")
    print("🚨" * 30)
    
    # Setup Web3
    w3 = Web3(Web3.HTTPProvider("https://polygon-rpc.com"))
    
    # Wallet addresses
    wallet1 = "0xb3A635E05d1a159b0d2658d3F0e7D59cd4643633"  # Bot wallet
    wallet2 = "0x3E1B662bB2FD32D7eb6c57221296205C9D48D012"  # Polymarket wallet
    
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
    
    print("💰 CURRENT BALANCES:")
    print("-" * 50)
    
    # Check all relevant balances
    balance1 = usdc.functions.balanceOf(wallet1).call() / 10**6
    balance2 = usdc.functions.balanceOf(wallet2).call() / 10**6
    exchange_balance = usdc.functions.balanceOf(polymarket_exchange).call() / 10**6
    
    print(f"Bot Wallet ({wallet1}): ${balance1:.6f} USDC")
    print(f"Polymarket Wallet ({wallet2}): ${balance2:.6f} USDC")
    print(f"Polymarket Exchange Contract: ${exchange_balance:.6f} USDC")
    print()
    
    total_found = balance1 + balance2
    print(f"🔍 TOTAL FOUND IN YOUR WALLETS: ${total_found:.6f} USDC")
    print(f"🚨 MISSING: ${134 - total_found:.6f} USDC")
    print()
    
    # Get recent transactions for both wallets
    print("📋 RECENT TRANSACTIONS:")
    print("-" * 50)
    
    # Known transaction hashes from our operations
    known_txs = [
        "0x39ea775bde8e8645a2ea179ba334b8076c267b7814231f0b03bbd9c5262bce68",  # $24.50 to exchange
        "0xa963abfebe3e7b558dcd4c212b6a0b22bb9ce9a13852646dbcd32623b390ac0d"   # Failed transfer
    ]
    
    for i, tx_hash in enumerate(known_txs, 1):
        print(f"Transaction {i}: {tx_hash}")
        try:
            tx = w3.eth.get_transaction(tx_hash)
            receipt = w3.eth.get_transaction_receipt(tx_hash)
            
            print(f"   From: {tx['from']}")
            print(f"   To: {tx['to']}")
            print(f"   Status: {'✅ Success' if receipt['status'] == 1 else '❌ Failed'}")
            print(f"   Gas Used: {receipt['gasUsed']:,}")
            print(f"   View: https://polygonscan.com/tx/{tx_hash}")
            print()
        except Exception as e:
            print(f"   ❌ Error getting transaction: {e}")
            print()
    
    print("🔍 ANALYSIS:")
    print("-" * 50)
    
    if total_found < 10:
        print("🚨 CRITICAL: Most of your USDC is missing!")
        print("   Possible causes:")
        print("   1. Funds were sent to wrong address")
        print("   2. Multiple transactions we haven't tracked")
        print("   3. Funds are in a different contract")
        print("   4. Network/RPC issues showing wrong balances")
    
    print()
    print("🔧 IMMEDIATE ACTIONS:")
    print("-" * 50)
    print("1. Check PolygonScan for your wallet:")
    print(f"   https://polygonscan.com/address/{wallet1}")
    print(f"   https://polygonscan.com/address/{wallet2}")
    print()
    print("2. Look for ALL recent USDC transactions")
    print("3. Check if funds went to any other addresses")
    print("4. Verify your MetaMask is connected to Polygon network")
    print()
    print("🆘 RECOVERY OPTIONS:")
    print("-" * 50)
    print("1. If funds are in wrong contract - may be recoverable")
    print("2. If sent to wrong address - depends on the address")
    print("3. Contact Polymarket support immediately")
    print("4. Check all transaction history on PolygonScan")
    
    return balance1, balance2, total_found

def check_transaction_history():
    """Check transaction history using PolygonScan API"""
    print("\n📊 CHECKING TRANSACTION HISTORY...")
    print("-" * 50)
    
    wallet1 = "0xb3A635E05d1a159b0d2658d3F0e7D59cd4643633"
    usdc_contract = "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359"
    
    # PolygonScan API (free tier)
    api_url = "https://api.polygonscan.com/api"
    
    try:
        # Get ERC20 token transfers for USDC
        params = {
            "module": "account",
            "action": "tokentx",
            "contractaddress": usdc_contract,
            "address": wallet1,
            "page": 1,
            "offset": 100,
            "sort": "desc"
        }
        
        response = requests.get(api_url, params=params, timeout=10)
        data = response.json()
        
        if data.get("status") == "1" and data.get("result"):
            transactions = data["result"]
            print(f"Found {len(transactions)} USDC transactions:")
            print()
            
            total_out = 0
            total_in = 0
            
            for tx in transactions[:10]:  # Show last 10 transactions
                value = int(tx["value"]) / 10**6
                from_addr = tx["from"].lower()
                to_addr = tx["to"].lower()
                wallet_addr = wallet1.lower()
                
                if from_addr == wallet_addr:
                    direction = "OUT"
                    total_out += value
                    print(f"📤 OUT: ${value:.2f} USDC to {to_addr[:10]}...")
                elif to_addr == wallet_addr:
                    direction = "IN"
                    total_in += value
                    print(f"📥 IN:  ${value:.2f} USDC from {from_addr[:10]}...")
                
                print(f"    Hash: {tx['hash']}")
                print(f"    Time: {tx['timeStamp']}")
                print()
            
            print(f"💰 SUMMARY (last 10 transactions):")
            print(f"   Total IN:  ${total_in:.2f} USDC")
            print(f"   Total OUT: ${total_out:.2f} USDC")
            print(f"   Net:       ${total_in - total_out:.2f} USDC")
            
        else:
            print("❌ Could not fetch transaction history")
            print("Please check manually on PolygonScan:")
            print(f"https://polygonscan.com/address/{wallet1}#tokentxns")
    
    except Exception as e:
        print(f"❌ Error fetching transaction history: {e}")
        print("Please check manually on PolygonScan")

def main():
    """Main emergency function"""
    balance1, balance2, total_found = emergency_fund_trace()
    check_transaction_history()
    
    print("\n" + "🚨" * 30)
    print("EMERGENCY SUMMARY")
    print("🚨" * 30)
    print(f"💰 Expected: $134.00 USDC")
    print(f"💰 Found: ${total_found:.2f} USDC")
    print(f"🚨 Missing: ${134 - total_found:.2f} USDC")
    print()
    print("🆘 NEXT STEPS:")
    print("1. Check PolygonScan links above")
    print("2. Look for any large USDC transfers")
    print("3. Contact Polymarket support if funds went to their contracts")
    print("4. If funds went to unknown address, they may be lost")

if __name__ == "__main__":
    main() 