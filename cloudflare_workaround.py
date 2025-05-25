#!/usr/bin/env python3
"""
Cloudflare Workaround for Polymarket Trading

This script provides solutions for when Cloudflare blocks automated trading requests.
"""

import time
import random
import requests
from typing import Dict, Any

def test_cloudflare_access():
    """Test if we can access Polymarket APIs"""
    print("🔍 Testing Cloudflare access...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache"
    }
    
    test_urls = [
        "https://clob.polymarket.com/",
        "https://gamma-api.polymarket.com/events",
        "https://polymarket.com/api/markets"
    ]
    
    for url in test_urls:
        try:
            print(f"Testing: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 403:
                print("❌ Blocked by Cloudflare")
            elif response.status_code == 200:
                print("✅ Access successful")
            else:
                print(f"⚠️  Unexpected status: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        time.sleep(2)

def suggest_solutions():
    """Suggest solutions for Cloudflare blocking"""
    print("\n🛡️  CLOUDFLARE BLOCKING SOLUTIONS")
    print("=" * 50)
    
    print("\n1. 🌐 Use a VPN or Proxy:")
    print("   - Install a VPN on your EC2 instance")
    print("   - Use residential proxy services")
    print("   - Try different geographic locations")
    
    print("\n2. ⏰ Add More Delays:")
    print("   - Increase delays between API calls")
    print("   - Randomize request timing")
    print("   - Limit requests per minute")
    
    print("\n3. 🔄 Rotate User Agents:")
    print("   - Use different browser user agents")
    print("   - Rotate headers for each request")
    print("   - Mimic real browser behavior")
    
    print("\n4. 📧 Contact Polymarket:")
    print("   - Request API access for trading bots")
    print("   - Explain your use case")
    print("   - Ask for IP whitelisting")
    
    print("\n5. 💻 Run from Local Machine:")
    print("   - Run the bot from your personal computer")
    print("   - Use your home internet connection")
    print("   - Avoid cloud server IPs")
    
    print("\n6. 🔧 Technical Workarounds:")
    print("   - Use browser automation (Selenium)")
    print("   - Implement session management")
    print("   - Use HTTP/2 connections")

def create_local_trading_script():
    """Create a script optimized for local execution"""
    print("\n📝 Creating local trading script...")
    
    script_content = '''#!/usr/bin/env python3
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
        
        print("\\n🔍 Finding trading opportunities...")
        opportunities = trader.find_real_opportunities()
        
        if opportunities:
            for i, opp in enumerate(opportunities[:3]):  # Limit to top 3
                print(f"\\n🎯 Opportunity {i+1}:")
                print(f"   Market: {opp['question'][:60]}...")
                print(f"   Side: {opp['side']}")
                print(f"   Edge: {opp['edge']:.1%}")
                print(f"   Bet Size: ${trader.calculate_bet_size(opp['edge']):.2f}")
                
                # Ask for manual confirmation for each trade
                confirm = input(f"\\n💰 Execute this trade? (y/n): ")
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
'''
    
    with open("local_trading.py", "w") as f:
        f.write(script_content)
    
    print("✅ Created local_trading.py")
    print("💡 Run this script from your personal computer for better success")

def main():
    """Main function"""
    print("🛡️  POLYMARKET CLOUDFLARE WORKAROUND TOOL")
    print("=" * 50)
    
    test_cloudflare_access()
    suggest_solutions()
    create_local_trading_script()
    
    print("\n🎯 RECOMMENDED NEXT STEPS:")
    print("1. Try running 'python3 local_trading.py' from your personal computer")
    print("2. If still blocked, use a VPN and try again")
    print("3. Contact Polymarket support for API access")
    print("4. Consider using browser automation tools")

if __name__ == "__main__":
    main() 