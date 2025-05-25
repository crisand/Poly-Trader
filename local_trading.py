#!/usr/bin/env python3
"""
Local Polymarket Trading Bot
Optimized to run from personal computers to avoid Cloudflare blocking
"""

import time
import random
from place_real_trades import RealPolymarketTrader

def run_local_trading():
    """Run trading bot with local-friendly settings"""
    print("🏠 Starting LOCAL Polymarket Trading Bot")
    print("💡 Running from personal computer to avoid Cloudflare blocking")
    
    try:
        trader = RealPolymarketTrader()
        
        # Use longer delays for local execution
        trader.TRADING_INTERVAL = 600  # 10 minutes between scans
        
        print("\n🔍 Finding trading opportunities...")
        opportunities = trader.find_real_opportunities()
        
        if opportunities:
            for i, opp in enumerate(opportunities[:3]):  # Limit to top 3
                print(f"\n🎯 Opportunity {i+1}:")
                print(f"   Market: {opp['question'][:60]}...")
                print(f"   Side: {opp['side']}")
                print(f"   Edge: {opp['edge']:.1%}")
                print(f"   Bet Size: ${trader.calculate_bet_size(opp['edge']):.2f}")
                
                # Ask for manual confirmation for each trade
                confirm = input(f"\n💰 Execute this trade? (y/n): ")
                if confirm.lower() == 'y':
                    print("🚀 Executing trade...")
                    success = trader.execute_real_trade(opp)
                    if success:
                        print("✅ Trade executed successfully!")
                        break
                    else:
                        print("❌ Trade failed, trying next opportunity...")
                        time.sleep(30)  # Wait before next attempt
                else:
                    print("⏭️  Skipping this trade...")
        else:
            print("❌ No trading opportunities found")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    run_local_trading()
