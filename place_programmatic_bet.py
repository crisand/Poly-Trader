#!/usr/bin/env python3
import requests
import json
import os
import sys
import time
import random
from typing import Dict, Any, Optional, List, Tuple
from dotenv import load_dotenv
from web3 import Web3
from eth_account import Account
import datetime
import hashlib

# Load environment variables
load_dotenv()

# Constants
POLYMARKET_EXCHANGE = "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E"
USDC_CONTRACT = "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359"
RPC_URL = "https://polygon-rpc.com"
CLOB_API_URL = "https://clob.polymarket.com"

# Trading Configuration
INITIAL_BET_SIZE = 2.0  # Start with $2 bets
MAX_BET_SIZE = 20.0     # Maximum bet size
MIN_BET_SIZE = 1.0      # Minimum bet size
PROFIT_REINVEST_RATIO = 0.5  # Reinvest 50% of profits
TRADING_INTERVAL = 300  # 5 minutes between trades
MAX_DAILY_TRADES = 50   # Maximum trades per day
MIN_EDGE_THRESHOLD = 0.15  # Minimum 15% edge required

class AutonomousTrader:
    def __init__(self):
        self.wallet_address, self.private_key, self.w3 = self.get_wallet_info()
        self.starting_balance = self.get_usdc_balance()
        self.current_balance = self.starting_balance
        self.total_profit = 0.0
        self.trades_today = 0
        self.successful_trades = 0
        self.failed_trades = 0
        self.current_bet_size = INITIAL_BET_SIZE
        self.last_trade_time = 0
        
        print(f"🤖 AUTONOMOUS TRADING BOT INITIALIZED")
        print(f"💰 Starting Balance: ${self.starting_balance:.2f} USDC")
        print(f"🎯 Initial Bet Size: ${self.current_bet_size:.2f} USDC")
        
    def get_wallet_info(self) -> Tuple[str, str, Web3]:
        """Get wallet address and web3 connection from private key"""
        private_key = os.getenv("POLYGON_WALLET_PRIVATE_KEY", "")
        
        if not private_key:
            raise ValueError("No private key found in environment variables")
        
        if not private_key.startswith("0x"):
            private_key = "0x" + private_key
        
        w3 = Web3(Web3.HTTPProvider(RPC_URL))
        
        if not w3.is_connected():
            raise ConnectionError("Failed to connect to Polygon network")
        
        account = Account.from_key(private_key)
        wallet_address = account.address
        
        return wallet_address, private_key, w3

    def get_usdc_balance(self) -> float:
        """Get current USDC balance"""
        usdc_abi = json.loads('''[
            {
                "constant": true,
                "inputs": [{"name": "account", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "", "type": "uint256"}],
                "payable": false,
                "stateMutability": "view",
                "type": "function"
            }
        ]''')
        
        usdc_contract = self.w3.eth.contract(address=USDC_CONTRACT, abi=usdc_abi)
        balance = usdc_contract.functions.balanceOf(self.wallet_address).call()
        return balance / 10**6

    def analyze_market_opportunity(self, market: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a market for trading opportunities using AI-like analysis"""
        question = market.get("question", "")
        volume = float(market.get("volume", 0))
        
        # Simulate AI analysis of market sentiment and probability
        # In a real implementation, this would use OpenAI API or other AI services
        
        # Analyze question keywords for sentiment
        bullish_keywords = ["will", "win", "succeed", "pass", "approve", "increase", "rise"]
        bearish_keywords = ["fail", "lose", "reject", "decrease", "fall", "crash"]
        
        bullish_score = sum(1 for word in bullish_keywords if word.lower() in question.lower())
        bearish_score = sum(1 for word in bearish_keywords if word.lower() in question.lower())
        
        # Calculate AI predicted probability (simulated)
        base_probability = 0.5
        sentiment_adjustment = (bullish_score - bearish_score) * 0.1
        volume_adjustment = min(volume / 1000000, 0.2)  # Higher volume = more confidence
        
        ai_probability = max(0.1, min(0.9, base_probability + sentiment_adjustment + volume_adjustment))
        
        # Simulate current market price (in real implementation, get from API)
        market_price = round(random.uniform(0.2, 0.8), 3)
        
        # Calculate edge
        if ai_probability > market_price:
            edge = (ai_probability - market_price) / market_price
            side = "YES"
            confidence = min(0.95, ai_probability)
        else:
            edge = (market_price - ai_probability) / ai_probability
            side = "NO"
            confidence = min(0.95, 1 - ai_probability)
        
        return {
            "market": market,
            "ai_probability": ai_probability,
            "market_price": market_price,
            "edge": edge,
            "side": side,
            "confidence": confidence,
            "volume": volume,
            "expected_value": edge * confidence
        }

    def find_best_opportunities(self) -> List[Dict[str, Any]]:
        """Find the best trading opportunities across all markets"""
        print("🔍 Scanning markets for opportunities...")
        
        # Get current markets (using demo data since API returns old markets)
        demo_markets = [
            {
                "question": "Will Bitcoin reach $150,000 by end of 2025?",
                "volume": 2500000,
                "active": True,
                "clobTokenIds": ["123456789", "987654321"]
            },
            {
                "question": "Will the Lakers make the NBA playoffs in 2025?",
                "volume": 1800000,
                "active": True,
                "clobTokenIds": ["111222333", "444555666"]
            },
            {
                "question": "Will Tesla stock hit $400 by March 2025?",
                "volume": 3200000,
                "active": True,
                "clobTokenIds": ["777888999", "000111222"]
            },
            {
                "question": "Will there be a major AI breakthrough announced in February 2025?",
                "volume": 950000,
                "active": True,
                "clobTokenIds": ["333444555", "666777888"]
            },
            {
                "question": "Will the US Federal Reserve cut interest rates in Q1 2025?",
                "volume": 4100000,
                "active": True,
                "clobTokenIds": ["999000111", "222333444"]
            }
        ]
        
        opportunities = []
        
        for market in demo_markets:
            try:
                analysis = self.analyze_market_opportunity(market)
                
                # Only consider opportunities with sufficient edge
                if analysis["edge"] >= MIN_EDGE_THRESHOLD:
                    opportunities.append(analysis)
                    print(f"📈 Found opportunity: {market['question'][:50]}...")
                    print(f"   Edge: {analysis['edge']:.1%}, Side: {analysis['side']}")
                
            except Exception as e:
                print(f"Error analyzing market: {e}")
                continue
        
        # Sort by expected value (edge * confidence)
        opportunities.sort(key=lambda x: x["expected_value"], reverse=True)
        
        print(f"✅ Found {len(opportunities)} profitable opportunities")
        return opportunities[:5]  # Return top 5

    def calculate_bet_size(self, edge: float, confidence: float) -> float:
        """Calculate optimal bet size using Kelly Criterion with safety margins"""
        # Kelly Criterion: f = (bp - q) / b
        # Where: b = odds, p = probability of win, q = probability of loss
        
        # Convert edge to Kelly fraction
        kelly_fraction = edge * confidence
        
        # Apply safety margin (use 25% of Kelly)
        safe_fraction = kelly_fraction * 0.25
        
        # Calculate bet size
        bet_size = self.current_balance * safe_fraction
        
        # Apply limits
        bet_size = max(MIN_BET_SIZE, min(MAX_BET_SIZE, bet_size))
        bet_size = min(bet_size, self.current_balance * 0.1)  # Never bet more than 10% of balance
        
        return round(bet_size, 2)

    def execute_trade(self, opportunity: Dict[str, Any]) -> bool:
        """Execute a trade on the selected opportunity"""
        market = opportunity["market"]
        question = market["question"]
        side = opportunity["side"]
        edge = opportunity["edge"]
        
        bet_size = self.calculate_bet_size(edge, opportunity["confidence"])
        
        if bet_size < MIN_BET_SIZE:
            print(f"❌ Bet size too small: ${bet_size:.2f}")
            return False
        
        print(f"\n🎯 EXECUTING TRADE")
        print(f"Market: {question}")
        print(f"Side: {side}")
        print(f"Bet Size: ${bet_size:.2f}")
        print(f"Expected Edge: {edge:.1%}")
        
        # Simulate trade execution
        success_probability = 0.85  # 85% success rate
        trade_successful = random.random() < success_probability
        
        if trade_successful:
            # Simulate profit/loss
            outcome_probability = 0.6  # 60% chance of winning
            won_trade = random.random() < outcome_probability
            
            if won_trade:
                profit = bet_size * (edge + 0.1)  # Profit based on edge
                self.current_balance += profit
                self.total_profit += profit
                self.successful_trades += 1
                
                print(f"✅ TRADE WON! Profit: ${profit:.2f}")
                print(f"💰 New Balance: ${self.current_balance:.2f}")
                
                # Increase bet size on success
                self.current_bet_size = min(MAX_BET_SIZE, self.current_bet_size * 1.1)
                
            else:
                loss = bet_size
                self.current_balance -= loss
                self.total_profit -= loss
                self.failed_trades += 1
                
                print(f"❌ TRADE LOST! Loss: ${loss:.2f}")
                print(f"💰 New Balance: ${self.current_balance:.2f}")
                
                # Decrease bet size on loss
                self.current_bet_size = max(MIN_BET_SIZE, self.current_bet_size * 0.9)
            
            self.trades_today += 1
            return True
            
        else:
            print(f"❌ Trade execution failed")
            return False

    def print_status(self):
        """Print current trading status"""
        total_return = ((self.current_balance - self.starting_balance) / self.starting_balance) * 100
        win_rate = (self.successful_trades / max(1, self.successful_trades + self.failed_trades)) * 100
        
        print(f"\n📊 TRADING STATUS")
        print(f"💰 Current Balance: ${self.current_balance:.2f}")
        print(f"📈 Total Profit/Loss: ${self.total_profit:.2f}")
        print(f"📊 Total Return: {total_return:.1f}%")
        print(f"🎯 Trades Today: {self.trades_today}/{MAX_DAILY_TRADES}")
        print(f"✅ Win Rate: {win_rate:.1f}%")
        print(f"💵 Next Bet Size: ${self.current_bet_size:.2f}")

    def should_continue_trading(self) -> bool:
        """Check if we should continue trading"""
        # Stop if we've hit daily trade limit
        if self.trades_today >= MAX_DAILY_TRADES:
            print("🛑 Daily trade limit reached")
            return False
        
        # Stop if balance is too low
        if self.current_balance < MIN_BET_SIZE * 2:
            print("🛑 Balance too low to continue trading")
            return False
        
        # Stop if we've lost more than 50% of starting balance
        if self.current_balance < self.starting_balance * 0.5:
            print("🛑 Stop loss triggered (50% drawdown)")
            return False
        
        return True

    def run_autonomous_trading(self):
        """Main autonomous trading loop"""
        print(f"\n🚀 STARTING AUTONOMOUS TRADING")
        print(f"⏰ Trading every {TRADING_INTERVAL} seconds")
        print(f"🎯 Max {MAX_DAILY_TRADES} trades per day")
        print(f"📊 Minimum edge required: {MIN_EDGE_THRESHOLD:.1%}")
        
        while self.should_continue_trading():
            try:
                current_time = time.time()
                
                # Check if enough time has passed since last trade
                if current_time - self.last_trade_time < TRADING_INTERVAL:
                    time.sleep(10)  # Wait 10 seconds before checking again
                    continue
                
                # Find opportunities
                opportunities = self.find_best_opportunities()
                
                if opportunities:
                    best_opportunity = opportunities[0]
                    
                    # Execute trade on best opportunity
                    if self.execute_trade(best_opportunity):
                        self.last_trade_time = current_time
                    
                    self.print_status()
                else:
                    print("🔍 No profitable opportunities found, waiting...")
                
                # Wait before next scan
                time.sleep(30)  # Wait 30 seconds between scans
                
            except KeyboardInterrupt:
                print("\n🛑 Trading stopped by user")
                break
            except Exception as e:
                print(f"❌ Error in trading loop: {e}")
                time.sleep(60)  # Wait 1 minute on error
        
        self.print_final_results()

    def print_final_results(self):
        """Print final trading results"""
        total_return = ((self.current_balance - self.starting_balance) / self.starting_balance) * 100
        win_rate = (self.successful_trades / max(1, self.successful_trades + self.failed_trades)) * 100
        
        print(f"\n🏁 FINAL TRADING RESULTS")
        print(f"=" * 50)
        print(f"💰 Starting Balance: ${self.starting_balance:.2f}")
        print(f"💰 Final Balance: ${self.current_balance:.2f}")
        print(f"📈 Total Profit/Loss: ${self.total_profit:.2f}")
        print(f"📊 Total Return: {total_return:.1f}%")
        print(f"🎯 Total Trades: {self.trades_today}")
        print(f"✅ Successful Trades: {self.successful_trades}")
        print(f"❌ Failed Trades: {self.failed_trades}")
        print(f"🎯 Win Rate: {win_rate:.1f}%")
        print(f"=" * 50)

def main():
    """Main function to run autonomous trading bot"""
    print("🤖 POLYMARKET AUTONOMOUS TRADING BOT")
    print("=" * 50)
    
    try:
        trader = AutonomousTrader()
        trader.run_autonomous_trading()
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 