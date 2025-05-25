#!/usr/bin/env python3
import os
import sys
import time
import random
import json
from typing import Dict, Any, Optional, List, Tuple
from dotenv import load_dotenv
from web3 import Web3
from eth_account import Account
import datetime

# Import Polymarket official client
try:
    from py_clob_client.client import ClobClient
    from py_clob_client.constants import POLYGON
    from py_clob_client.order_builder.constants import BUY, SELL
except ImportError:
    print("❌ Polymarket client not installed. Run: pip install py-clob-client")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Constants
USDC_CONTRACT = "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359"
RPC_URL = "https://polygon-rpc.com"

# Trading Configuration
INITIAL_BET_SIZE = 2.0
MAX_BET_SIZE = 20.0
MIN_BET_SIZE = 1.0
TRADING_INTERVAL = 300
MAX_DAILY_TRADES = 50
MIN_EDGE_THRESHOLD = 0.15

class RealPolymarketTrader:
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
        
        # Initialize Polymarket client
        self.clob_client = None
        self.initialize_polymarket_client()
        
        print(f"🤖 REAL POLYMARKET TRADING BOT INITIALIZED")
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
        
        usdc_contract = self.w3.eth.contract(address=USDC_CONTRACT, abi=usdc_abi)
        balance = usdc_contract.functions.balanceOf(self.wallet_address).call()
        return balance / 10**6

    def initialize_polymarket_client(self):
        """Initialize the Polymarket CLOB client"""
        try:
            print("🔗 Initializing Polymarket client...")
            
            # Create client with private key
            self.clob_client = ClobClient(
                host="https://clob.polymarket.com",
                chain_id=POLYGON,
                key=self.private_key
            )
            
            # Set up API credentials (this will create them if they don't exist)
            try:
                api_creds = self.clob_client.create_or_derive_api_creds()
                self.clob_client.set_api_creds(api_creds)
                print("✅ API credentials set up successfully")
            except Exception as e:
                print(f"⚠️  Warning: Could not set up API credentials: {e}")
                print("📝 Note: You may need to manually create API credentials")
            
            print("✅ Polymarket client initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize Polymarket client: {e}")
            print("📝 Note: Make sure you have the correct private key and network access")
            self.clob_client = None

    def get_real_markets(self) -> List[Dict[str, Any]]:
        """Get real markets from Polymarket"""
        if not self.clob_client:
            print("❌ Polymarket client not available")
            return []
        
        try:
            print("🔍 Loading real markets from discovered markets file...")
            
            # Load discovered markets from file
            try:
                with open("current_markets.json", "r") as f:
                    discovered_markets = json.load(f)
                
                print(f"✅ Loaded {len(discovered_markets)} markets from file")
                
                # Filter for high-volume, active markets with orderbooks
                filtered_markets = []
                print("🔍 Checking markets for active orderbooks...")
                
                for i, market in enumerate(discovered_markets[:30]):  # Check top 30 markets
                    if market.get("active", False) and float(market.get("volume", 0)) > 100000:  # $100K+ volume
                        # Parse tokens from JSON string
                        tokens_str = market.get("tokens", "[]")
                        try:
                            if isinstance(tokens_str, str):
                                tokens = json.loads(tokens_str)
                            else:
                                tokens = tokens_str
                        except:
                            tokens = []
                        
                        if len(tokens) >= 2:
                            # Check if at least one token has an orderbook
                            yes_token_id = tokens[0]
                            if self.validate_market_orderbook(yes_token_id):
                                # Update the market with parsed tokens
                                market["tokens"] = tokens
                                filtered_markets.append(market)
                                print(f"✅ Market {i+1}: {market.get('question', 'Unknown')[:50]}... - Has orderbook")
                            else:
                                print(f"⚠️  Market {i+1}: {market.get('question', 'Unknown')[:50]}... - No orderbook")
                        else:
                            print(f"⚠️  Market {i+1}: {market.get('question', 'Unknown')[:50]}... - No tokens")
                    
                    # Don't check too many at once to avoid rate limits
                    if i > 0 and i % 5 == 0:
                        print(f"📊 Checked {i+1} markets so far...")
                        time.sleep(1)  # Brief pause to avoid rate limits
                
                print(f"✅ Found {len(filtered_markets)} markets with active orderbooks")
                return filtered_markets
                
            except FileNotFoundError:
                print("❌ Current markets file not found. Run discover_markets.py first.")
                return []
            
        except Exception as e:
            print(f"❌ Error loading real markets: {e}")
            return []

    def analyze_real_market(self, market: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze a real market for trading opportunities"""
        try:
            condition_id = market.get("condition_id")
            question = market.get("question", "")
            volume = float(market.get("volume", 0))
            
            if not condition_id or not question:
                return None
            
            print(f"🔍 Analyzing market: {question[:50]}...")
            
            # Get token IDs from the market (should already be parsed)
            tokens = market.get("tokens", [])
            if len(tokens) < 2:
                print(f"❌ Insufficient tokens for market {condition_id}")
                return None
            
            yes_token_id = tokens[0]
            no_token_id = tokens[1]
            
            # Get real current price from the API
            current_price = self.get_market_price(yes_token_id)
            if current_price is None:
                print(f"❌ Could not get current price for {yes_token_id}")
                return None
            
            print(f"📊 Current YES price: ${current_price:.3f}")
            
            # AI analysis of market sentiment
            bullish_keywords = ["will", "win", "succeed", "pass", "approve", "increase", "rise", "championship", "finals"]
            bearish_keywords = ["fail", "lose", "reject", "decrease", "fall", "crash", "relegated", "eliminated"]
            
            bullish_score = sum(1 for word in bullish_keywords if word.lower() in question.lower())
            bearish_score = sum(1 for word in bearish_keywords if word.lower() in question.lower())
            
            # Calculate AI predicted probability
            base_probability = 0.5
            sentiment_adjustment = (bullish_score - bearish_score) * 0.08
            volume_adjustment = min(volume / 10000000, 0.15)  # Higher volume = more confidence
            
            ai_probability = max(0.1, min(0.9, base_probability + sentiment_adjustment + volume_adjustment))
            
            # Calculate edge
            if ai_probability > current_price:
                edge = (ai_probability - current_price) / current_price
                side = "YES"
                token_id = yes_token_id
            else:
                edge = (current_price - ai_probability) / ai_probability
                side = "NO"
                token_id = no_token_id
                # Validate the NO token has a price too
                no_price = self.get_market_price(token_id)
                if no_price is None:
                    print(f"⚠️  No price available for NO token {token_id}")
                    return None
            
            if edge >= MIN_EDGE_THRESHOLD:
                print(f"✅ Found opportunity: {side} with {edge:.1%} edge")
                return {
                    "market": market,
                    "condition_id": condition_id,
                    "token_id": token_id,
                    "side": side,
                    "edge": edge,
                    "current_price": current_price,
                    "ai_probability": ai_probability,
                    "question": question,
                    "volume": volume
                }
            else:
                print(f"⚠️  Edge too small: {edge:.1%} < {MIN_EDGE_THRESHOLD:.1%}")
            
            return None
            
        except Exception as e:
            print(f"❌ Error analyzing market: {e}")
            return None

    def execute_real_trade(self, opportunity: Dict[str, Any]) -> bool:
        """Execute a real trade on Polymarket with Cloudflare protection handling"""
        if not self.clob_client:
            print("❌ Polymarket client not available")
            return False
        
        try:
            market = opportunity["market"]
            token_id = opportunity["token_id"]
            side = opportunity["side"]
            edge = opportunity["edge"]
            question = opportunity["question"]
            
            # Calculate bet size
            bet_size = self.calculate_bet_size(edge)
            
            if bet_size < MIN_BET_SIZE:
                print(f"❌ Bet size too small: ${bet_size:.2f}")
                return False
            
            print(f"\n🎯 EXECUTING REAL TRADE")
            print(f"Market: {question}")
            print(f"Side: {side}")
            print(f"Bet Size: ${bet_size:.2f}")
            print(f"Token ID: {token_id}")
            print(f"Expected Edge: {edge:.1%}")
            
            # Import the correct types
            from py_clob_client.clob_types import MarketOrderArgs, OrderType
            from py_clob_client.order_builder.constants import BUY, SELL
            
            # Determine the correct side for the API
            api_side = BUY if side == "YES" else SELL
            
            # Add delay to avoid rate limiting
            print("⏳ Waiting to avoid rate limits...")
            time.sleep(3)
            
            # Create market order arguments
            order_args = MarketOrderArgs(
                token_id=token_id,
                amount=bet_size,  # Amount in USDC for BUY orders, shares for SELL orders
                side=api_side
            )
            
            # Create the market order
            print("📝 Creating market order...")
            signed_order = self.clob_client.create_market_order(order_args)
            
            # Add another delay before submitting
            time.sleep(2)
            
            # Submit the order as FOK (Fill-Or-Kill)
            print("🚀 Submitting order...")
            response = self.clob_client.post_order(signed_order, OrderType.FOK)
            
            if response and response.get("success"):
                order_id = response.get("orderId")
                print(f"✅ REAL TRADE EXECUTED!")
                print(f"Order ID: {order_id}")
                
                # Update tracking
                self.trades_today += 1
                self.successful_trades += 1
                
                # For real trades, we don't know the outcome immediately
                # You would need to track positions and check later
                print(f"📊 Trade submitted successfully. Monitor position for results.")
                
                return True
            else:
                error_msg = response.get("errorMsg", "Unknown error") if response else "No response"
                print(f"❌ Trade failed: {error_msg}")
                self.failed_trades += 1
                return False
                
        except Exception as e:
            error_str = str(e)
            if "403" in error_str and "Cloudflare" in error_str:
                print(f"🛡️  Blocked by Cloudflare security. This is common for automated trading.")
                print(f"💡 Suggestions:")
                print(f"   1. Try running from a different IP address")
                print(f"   2. Use a VPN or proxy service")
                print(f"   3. Add longer delays between requests")
                print(f"   4. Contact Polymarket support for API access")
            else:
                print(f"❌ Error executing real trade: {e}")
            
            self.failed_trades += 1
            return False

    def calculate_bet_size(self, edge: float) -> float:
        """Calculate optimal bet size using Kelly Criterion"""
        # Kelly Criterion with safety margin
        kelly_fraction = edge * 0.25  # Use 25% of Kelly for safety
        bet_size = self.current_balance * kelly_fraction
        
        # Apply limits
        bet_size = max(MIN_BET_SIZE, min(MAX_BET_SIZE, bet_size))
        bet_size = min(bet_size, self.current_balance * 0.1)  # Max 10% of balance
        
        return round(bet_size, 2)

    def find_real_opportunities(self) -> List[Dict[str, Any]]:
        """Find real trading opportunities"""
        print("🔍 Scanning real markets for opportunities...")
        
        markets = self.get_real_markets()
        opportunities = []
        
        for market in markets:
            analysis = self.analyze_real_market(market)
            if analysis:
                opportunities.append(analysis)
                print(f"📈 Found real opportunity: {analysis['question'][:50]}...")
                print(f"   Edge: {analysis['edge']:.1%}, Side: {analysis['side']}")
        
        # Sort by edge
        opportunities.sort(key=lambda x: x["edge"], reverse=True)
        
        print(f"✅ Found {len(opportunities)} real opportunities")
        return opportunities

    def should_continue_trading(self) -> bool:
        """Check if we should continue trading"""
        if self.trades_today >= MAX_DAILY_TRADES:
            print("🛑 Daily trade limit reached")
            return False
        
        if self.current_balance < MIN_BET_SIZE * 2:
            print("🛑 Balance too low to continue trading")
            return False
        
        if self.current_balance < self.starting_balance * 0.5:
            print("🛑 Stop loss triggered (50% drawdown)")
            return False
        
        return True

    def print_status(self):
        """Print current trading status"""
        total_return = ((self.current_balance - self.starting_balance) / self.starting_balance) * 100
        win_rate = (self.successful_trades / max(1, self.successful_trades + self.failed_trades)) * 100
        
        print(f"\n📊 REAL TRADING STATUS")
        print(f"💰 Current Balance: ${self.current_balance:.2f}")
        print(f"📈 Total Profit/Loss: ${self.total_profit:.2f}")
        print(f"📊 Total Return: {total_return:.1f}%")
        print(f"🎯 Trades Today: {self.trades_today}/{MAX_DAILY_TRADES}")
        print(f"✅ Win Rate: {win_rate:.1f}%")

    def run_real_trading(self):
        """Main real trading loop"""
        print(f"\n🚀 STARTING REAL POLYMARKET TRADING")
        print(f"⚠️  WARNING: This will place REAL trades with REAL money!")
        print(f"⏰ Trading every {TRADING_INTERVAL} seconds")
        print(f"🎯 Max {MAX_DAILY_TRADES} trades per day")
        print(f"📊 Minimum edge required: {MIN_EDGE_THRESHOLD:.1%}")
        
        # Safety confirmation
        confirm = input("\n🔴 Are you sure you want to start REAL trading? (type 'YES' to confirm): ")
        if confirm != "YES":
            print("❌ Real trading cancelled")
            return
        
        while self.should_continue_trading():
            try:
                current_time = time.time()
                
                # Check if enough time has passed since last trade
                if current_time - self.last_trade_time < TRADING_INTERVAL:
                    time.sleep(10)
                    continue
                
                # Find real opportunities
                opportunities = self.find_real_opportunities()
                
                if opportunities:
                    best_opportunity = opportunities[0]
                    
                    # Execute real trade
                    if self.execute_real_trade(best_opportunity):
                        self.last_trade_time = current_time
                    
                    self.print_status()
                else:
                    print("🔍 No profitable opportunities found, waiting...")
                
                # Wait before next scan
                time.sleep(30)
                
            except KeyboardInterrupt:
                print("\n🛑 Real trading stopped by user")
                break
            except Exception as e:
                print(f"❌ Error in real trading loop: {e}")
                time.sleep(60)

    def validate_market_orderbook(self, token_id: str) -> bool:
        """Check if a market has an active orderbook by trying to get price"""
        if not self.clob_client:
            return False
        
        try:
            # Add small delay to avoid rate limiting
            time.sleep(0.5)
            
            # Try to get the last trade price - if this works, the market is tradeable
            price_data = self.clob_client.get_last_trade_price(token_id)
            if price_data and "price" in price_data:
                price = float(price_data["price"])
                # Valid price should be between 0.01 and 0.99
                if 0.01 <= price <= 0.99:
                    return True
            
            return False
            
        except Exception as e:
            # If we can't get price, market is not tradeable
            return False

    def get_market_price(self, token_id: str) -> Optional[float]:
        """Get current market price for a token"""
        if not self.clob_client:
            return None
        
        try:
            # Add small delay to avoid rate limiting
            time.sleep(0.3)
            
            # Try to get the current price
            price_data = self.clob_client.get_last_trade_price(token_id)
            if price_data and "price" in price_data:
                return float(price_data["price"])
            
            return None
            
        except Exception as e:
            return None

def main():
    """Main function to run real trading bot"""
    print("🤖 POLYMARKET REAL TRADING BOT")
    print("=" * 50)
    print("⚠️  WARNING: This bot places REAL trades!")
    print("=" * 50)
    
    try:
        trader = RealPolymarketTrader()
        trader.run_real_trading()
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 