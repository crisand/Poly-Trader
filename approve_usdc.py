#!/usr/bin/env python3
import requests
import json
import os
from dotenv import load_dotenv
from web3 import Web3
from eth_account import Account

# Load environment variables
load_dotenv()

def approve_usdc_spending():
    """Approve the Polymarket Exchange contract to spend USDC"""
    
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
    
    # Connect to Polygon network
    rpc_url = "https://polygon-rpc.com"
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    
    if not w3.is_connected():
        print("Failed to connect to Polygon network")
        return
    
    print(f"Connected to Polygon network. Chain ID: {w3.eth.chain_id}")
    
    # Define contract addresses
    usdc_contract = "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359"  # USDC on Polygon
    polymarket_exchange = "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E"  # Polymarket Exchange
    
    # Check USDC balance first
    try:
        # USDC contract ABI (just the balanceOf function)
        usdc_abi = json.loads('''[
            {
                "constant": true,
                "inputs": [{"name": "account", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "", "type": "uint256"}],
                "payable": false,
                "stateMutability": "view",
                "type": "function"
            },
            {
                "constant": false,
                "inputs": [
                    {"name": "spender", "type": "address"},
                    {"name": "amount", "type": "uint256"}
                ],
                "name": "approve",
                "outputs": [{"name": "", "type": "bool"}],
                "payable": false,
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "constant": true,
                "inputs": [
                    {"name": "owner", "type": "address"},
                    {"name": "spender", "type": "address"}
                ],
                "name": "allowance",
                "outputs": [{"name": "", "type": "uint256"}],
                "payable": false,
                "stateMutability": "view",
                "type": "function"
            }
        ]''')
        
        # Create contract instance
        usdc_contract = w3.eth.contract(address=usdc_contract, abi=usdc_abi)
        
        # Check USDC balance
        balance = usdc_contract.functions.balanceOf(wallet_address).call()
        balance_usdc = balance / 10**6  # USDC has 6 decimals
        
        print(f"USDC balance: {balance_usdc} USDC")
        
        # Check current allowance
        current_allowance = usdc_contract.functions.allowance(
            wallet_address, 
            polymarket_exchange
        ).call()
        current_allowance_usdc = current_allowance / 10**6
        
        print(f"Current Polymarket allowance: {current_allowance_usdc} USDC")
        
        if balance == 0:
            print("\nYou don't have any USDC in your wallet yet.")
            print("Please wait for your withdrawal to process or check the transaction status.")
            return
        
        if current_allowance > 0 and current_allowance >= balance:
            print("\nYou already have sufficient allowance for your USDC balance.")
            print("You should be able to place bets now!")
            return
        
        # Ask for confirmation before approving
        print("\nDo you want to approve Polymarket to spend your USDC? (y/n)")
        confirm = input("> ").strip().lower()
        
        if confirm != 'y':
            print("Approval cancelled")
            return
        
        # Amount to approve (max uint256 value to never need to approve again)
        max_uint256 = 2**256 - 1
        
        # Build approval transaction
        approve_txn = usdc_contract.functions.approve(
            polymarket_exchange,
            max_uint256
        ).build_transaction({
            'from': wallet_address,
            'gas': 100000,  # Gas limit
            'gasPrice': w3.to_wei('50', 'gwei'),  # Gas price in gwei
            'nonce': w3.eth.get_transaction_count(wallet_address),
        })
        
        # Sign and send transaction
        signed_txn = w3.eth.account.sign_transaction(approve_txn, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        print(f"Approval transaction sent! Transaction hash: {tx_hash.hex()}")
        print(f"View on PolygonScan: https://polygonscan.com/tx/{tx_hash.hex()}")
        
        # Wait for transaction to be mined
        print("\nWaiting for transaction to be confirmed...")
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if tx_receipt['status'] == 1:
            print("✅ Transaction confirmed! You can now place bets on Polymarket.")
        else:
            print("❌ Transaction failed. Please check PolygonScan for details.")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    print("=" * 60)
    print("POLYMARKET USDC APPROVAL TOOL")
    print("=" * 60)
    approve_usdc_spending() 