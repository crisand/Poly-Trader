#!/usr/bin/env python3
"""
Manual Polymarket Trading Assistant

Since Cloudflare blocks automated trading, this script finds opportunities
and guides you to place trades manually on the Polymarket website.
"""

import time
import json
from place_real_trades import RealPolymarketTrader

def display_trading_opportunities():
    """Find and display trading opportunities for manual execution"""
    print("🎯 MANUAL POLYMARKET TRADING ASSISTANT")
    print("=" * 60)
    print("💡 This tool finds opportunities and guides you to trade manually")
    print("🌐 You'll place trades through the Polymarket website")
    print("=" * 60)
    
    try:
        # Initialize trader (but won't execute trades)
        trader = RealPolymarketTrader()
        
        print("\n🔍 Scanning for trading opportunities...")
        opportunities = trader.find_real_opportunities()
        
        if not opportunities:
            print("❌ No trading opportunities found at this time")
            print("💡 Try again in a few minutes - markets change constantly")
            return
        
        print(f"\n✅ Found {len(opportunities)} trading opportunities!")
        print("\n" + "=" * 80)
        
        for i, opp in enumerate(opportunities, 1):
            print(f"\n🎯 OPPORTUNITY #{i}")
            print("-" * 50)
            print(f"📊 Market: {opp['question']}")
            print(f"💰 Current Price: ${opp['current_price']:.3f}")
            print(f"🎲 Recommended Side: {opp['side']}")
            print(f"📈 Calculated Edge: {opp['edge']:.1%}")
            print(f"💵 Suggested Bet Size: ${trader.calculate_bet_size(opp['edge']):.2f}")
            print(f"🔗 Token ID: {opp['token_id']}")
            
            # Generate direct link to market
            condition_id = opp['condition_id']
            market_url = f"https://polymarket.com/event/{condition_id}"
            print(f"🌐 Direct Link: {market_url}")
            
            print(f"\n📋 MANUAL TRADING INSTRUCTIONS:")
            print(f"   1. Open: {market_url}")
            print(f"   2. Click '{opp['side']}' button")
            print(f"   3. Enter amount: ${trader.calculate_bet_size(opp['edge']):.2f}")
            print(f"   4. Review and confirm trade")
            print(f"   5. Expected profit if correct: ~{opp['edge']:.1%}")
            
            print("\n" + "=" * 80)
        
        # Show summary
        print(f"\n📊 TRADING SUMMARY")
        print(f"💰 Your Balance: ${trader.current_balance:.2f} USDC")
        print(f"🎯 Total Opportunities: {len(opportunities)}")
        print(f"💵 Total Suggested Investment: ${sum(trader.calculate_bet_size(opp['edge']) for opp in opportunities):.2f}")
        
        # Calculate potential profit
        potential_profit = sum(trader.calculate_bet_size(opp['edge']) * opp['edge'] for opp in opportunities)
        print(f"📈 Potential Profit (if all correct): ${potential_profit:.2f}")
        
        print(f"\n🎯 NEXT STEPS:")
        print(f"1. 🌐 Open Polymarket.com in your browser")
        print(f"2. 🔐 Connect your wallet (same one with ${trader.current_balance:.2f} USDC)")
        print(f"3. 📋 Use the links above to navigate to each market")
        print(f"4. 💰 Place trades manually following the instructions")
        print(f"5. 📊 Monitor your positions for results")
        
        # Ask if user wants to monitor
        print(f"\n⏰ Would you like to monitor for new opportunities?")
        monitor = input("Type 'y' to keep monitoring, or any key to exit: ")
        
        if monitor.lower() == 'y':
            print(f"\n🔄 Monitoring mode activated...")
            print(f"💡 Will check for new opportunities every 10 minutes")
            print(f"⏹️  Press Ctrl+C to stop")
            
            try:
                while True:
                    time.sleep(600)  # Wait 10 minutes
                    print(f"\n🔍 Checking for new opportunities...")
                    new_opportunities = trader.find_real_opportunities()
                    
                    if len(new_opportunities) > len(opportunities):
                        print(f"🆕 Found {len(new_opportunities) - len(opportunities)} new opportunities!")
                        # Show only new ones
                        for opp in new_opportunities[len(opportunities):]:
                            print(f"\n🆕 NEW OPPORTUNITY:")
                            print(f"📊 Market: {opp['question'][:60]}...")
                            print(f"🎲 Side: {opp['side']}")
                            print(f"📈 Edge: {opp['edge']:.1%}")
                            print(f"🌐 Link: https://polymarket.com/event/{opp['condition_id']}")
                        opportunities = new_opportunities
                    else:
                        print(f"📊 No new opportunities (still {len(opportunities)} available)")
                        
            except KeyboardInterrupt:
                print(f"\n⏹️  Monitoring stopped by user")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def create_trading_guide():
    """Create a comprehensive trading guide"""
    print(f"\n📚 CREATING POLYMARKET TRADING GUIDE...")
    
    guide_content = """
# 🎯 Polymarket Manual Trading Guide

## 🚀 Quick Start
1. Open https://polymarket.com
2. Connect your wallet (the one with USDC)
3. Use the opportunities found by this script
4. Place trades manually for each opportunity

## 💰 Wallet Setup
- Ensure you have USDC on Polygon network
- Your current balance: Check with the script
- Approve USDC for trading if needed

## 📊 How to Read Opportunities
- **Market**: The prediction market question
- **Side**: YES or NO (which side to bet on)
- **Edge**: Expected profit percentage
- **Bet Size**: Recommended amount to wager
- **Current Price**: Current market price

## 🎯 Trading Strategy
1. **High Edge First**: Start with highest edge opportunities
2. **Diversify**: Don't put all money in one market
3. **Monitor**: Check positions regularly
4. **Exit Strategy**: Consider taking profits early

## ⚠️ Risk Management
- Never bet more than you can afford to lose
- Start with small amounts to test the system
- Monitor market news that could affect outcomes
- Set stop-losses if positions move against you

## 🔗 Useful Links
- Polymarket: https://polymarket.com
- Your Portfolio: https://polymarket.com/portfolio
- Market Analytics: https://polymarket.com/leaderboard

## 📞 Support
- Polymarket Discord: https://discord.gg/polymarket
- Documentation: https://docs.polymarket.com
"""
    
    with open("trading_guide.md", "w") as f:
        f.write(guide_content)
    
    print("✅ Created trading_guide.md")

def main():
    """Main function"""
    try:
        display_trading_opportunities()
        create_trading_guide()
        
        print(f"\n🎉 MANUAL TRADING SESSION COMPLETE!")
        print(f"📁 Check 'trading_guide.md' for detailed instructions")
        print(f"🔄 Run this script again anytime to find new opportunities")
        
    except KeyboardInterrupt:
        print(f"\n⏹️  Session ended by user")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 