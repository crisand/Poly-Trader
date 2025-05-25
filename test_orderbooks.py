#!/usr/bin/env python3
from place_real_trades import RealPolymarketTrader
import sys

def test_tradeable_markets():
    try:
        print("🤖 Testing Polymarket orderbook validation...")
        trader = RealPolymarketTrader()
        
        print('\n🔍 Testing market discovery with orderbook validation...')
        markets = trader.get_real_markets()
        print(f'\n📊 Found {len(markets)} tradeable markets')
        
        if markets:
            print('\n🎯 Testing market analysis...')
            for i, market in enumerate(markets[:3]):
                print(f'\nTesting market {i+1}: {market.get("question", "Unknown")[:60]}...')
                analysis = trader.analyze_real_market(market)
                if analysis:
                    print(f'✅ Found trading opportunity!')
                    print(f'   Side: {analysis["side"]}')
                    print(f'   Edge: {analysis["edge"]:.1%}')
                    print(f'   Token ID: {analysis["token_id"]}')
                    break
                else:
                    print('⚠️  No opportunity found')
        else:
            print('❌ No tradeable markets found')
            
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tradeable_markets() 