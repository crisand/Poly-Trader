#!/usr/bin/env python3
"""
Quick test for orderbook validation fix
"""

from real_auto_trader import RealAutoTrader
import time

def test_orderbook_validation():
    print("🧪 Testing orderbook validation fix...")
    
    try:
        trader = RealAutoTrader()
        markets = trader.get_active_markets()
        
        if markets:
            market = markets[0]
            tokens = market.get('tokens', [])
            if tokens:
                print(f"Testing token: {tokens[0][:20]}...")
                result = trader.validate_orderbook_exists(tokens[0])
                print(f"✅ Orderbook validation completed: {result}")
                print("✅ No more 'OrderBookSummary is not iterable' errors!")
            else:
                print("⚠️ No tokens found in market")
        else:
            print("⚠️ No markets found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_orderbook_validation() 