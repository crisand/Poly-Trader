#!/usr/bin/env python3
from place_real_trades import RealPolymarketTrader
import sys

def test_real_trade():
    try:
        print("🤖 Testing REAL trade execution...")
        trader = RealPolymarketTrader()
        
        print('\n🔍 Finding tradeable opportunities...')
        opportunities = trader.find_real_opportunities()
        
        if opportunities:
            best_opportunity = opportunities[0]
            print(f'\n🎯 Best opportunity found:')
            print(f'   Market: {best_opportunity["question"][:60]}...')
            print(f'   Side: {best_opportunity["side"]}')
            print(f'   Edge: {best_opportunity["edge"]:.1%}')
            print(f'   Current Price: ${best_opportunity["current_price"]:.3f}')
            print(f'   Token ID: {best_opportunity["token_id"]}')
            
            # Ask for confirmation before placing real trade
            print(f'\n⚠️  This will place a REAL trade with REAL money!')
            confirm = input('Type "YES" to place the trade: ')
            
            if confirm == "YES":
                print('\n🚀 Executing REAL trade...')
                success = trader.execute_real_trade(best_opportunity)
                
                if success:
                    print('✅ REAL TRADE EXECUTED SUCCESSFULLY!')
                else:
                    print('❌ Trade execution failed')
            else:
                print('❌ Trade cancelled by user')
        else:
            print('❌ No trading opportunities found')
            
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_real_trade() 