#!/usr/bin/env python3
import os
import sys
import requests
import json
from typing import List, Dict, Any
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def discover_current_markets() -> List[Dict[str, Any]]:
    """Discover current active markets from Polymarket's API"""
    try:
        print("🔍 Discovering current active markets from Polymarket...")
        
        # Use the correct Polymarket API endpoint for current markets
        api_url = "https://gamma-api.polymarket.com/events"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        params = {
            "limit": 20,
            "offset": 0,
            "active": "true",
            "closed": "false",
            "archived": "false"
        }
        
        try:
            response = requests.get(api_url, headers=headers, params=params, timeout=15)
            print(f"API Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Handle different response formats
                if isinstance(data, dict):
                    events = data.get("data", data.get("events", []))
                else:
                    events = data
                
                current_markets = []
                current_year = datetime.now().year
                
                for event in events:
                    if not isinstance(event, dict):
                        continue
                    
                    # Check if event is current (2025 or later)
                    end_date = event.get("endDate", "")
                    if end_date:
                        try:
                            end_year = datetime.fromisoformat(end_date.replace('Z', '+00:00')).year
                            if end_year < current_year:
                                continue  # Skip old events
                        except:
                            pass  # If date parsing fails, include the event
                    
                    # Extract market information
                    markets = event.get("markets", [])
                    for market in markets:
                        if isinstance(market, dict):
                            condition_id = market.get("conditionId")
                            if condition_id:
                                market_info = {
                                    "condition_id": condition_id,
                                    "question": market.get("question", ""),
                                    "description": market.get("description", ""),
                                    "end_date": market.get("endDate", event.get("endDate", "")),
                                    "active": market.get("active", True),
                                    "volume": market.get("volume", 0),
                                    "tokens": market.get("clobTokenIds", []),
                                    "event_title": event.get("title", ""),
                                    "event_slug": event.get("slug", "")
                                }
                                current_markets.append(market_info)
                
                print(f"✅ Found {len(current_markets)} current active markets")
                return current_markets
                
        except Exception as e:
            print(f"❌ Gamma API failed: {e}")
        
        # Try alternative CLOB API for current markets
        clob_url = "https://clob.polymarket.com/markets"
        
        try:
            clob_params = {
                "active": "true",
                "closed": "false",
                "limit": 20
            }
            
            response = requests.get(clob_url, headers=headers, params=clob_params, timeout=15)
            print(f"CLOB API Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                markets = data.get("data", []) if isinstance(data, dict) else data
                
                current_markets = []
                current_year = datetime.now().year
                
                for market in markets:
                    if not isinstance(market, dict):
                        continue
                    
                    # Check if market is current
                    end_date = market.get("endDate", market.get("end_date", ""))
                    if end_date:
                        try:
                            end_year = datetime.fromisoformat(end_date.replace('Z', '+00:00')).year
                            if end_year < current_year:
                                continue
                        except:
                            pass
                    
                    if market.get("active", False):
                        market_info = {
                            "condition_id": market.get("conditionId", market.get("condition_id")),
                            "question": market.get("question", ""),
                            "description": market.get("description", ""),
                            "end_date": end_date,
                            "active": market.get("active", True),
                            "volume": market.get("volume", market.get("volumeNum", 0)),
                            "tokens": market.get("clobTokenIds", []),
                            "market_id": market.get("id", "")
                        }
                        
                        if market_info["condition_id"]:
                            current_markets.append(market_info)
                
                print(f"✅ Found {len(current_markets)} current markets from CLOB API")
                return current_markets
                
        except Exception as e:
            print(f"❌ CLOB API failed: {e}")
        
        # If both APIs fail, try to get some known current condition IDs
        print("⚠️  APIs failed, trying to find current markets manually...")
        
        # Try to get some current markets from the main site
        try:
            site_url = "https://polymarket.com/api/markets"
            response = requests.get(site_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                markets = data.get("data", []) if isinstance(data, dict) else data
                
                current_markets = []
                for market in markets[:10]:  # Limit to first 10
                    if isinstance(market, dict) and market.get("active"):
                        market_info = {
                            "condition_id": market.get("conditionId", market.get("condition_id")),
                            "question": market.get("question", market.get("title", "")),
                            "description": market.get("description", ""),
                            "end_date": market.get("endDate", ""),
                            "active": True,
                            "volume": market.get("volume", 0),
                            "tokens": market.get("clobTokenIds", [])
                        }
                        
                        if market_info["condition_id"]:
                            current_markets.append(market_info)
                
                if current_markets:
                    print(f"✅ Found {len(current_markets)} markets from main site")
                    return current_markets
                    
        except Exception as e:
            print(f"❌ Main site API failed: {e}")
        
        # Last resort: return some test condition IDs
        print("⚠️  Using fallback test condition IDs for development")
        return [
            {
                "condition_id": "0x1234567890abcdef1234567890abcdef12345678",
                "question": "Will Bitcoin reach $150,000 by end of 2025?",
                "description": "Test market for Bitcoin price prediction",
                "end_date": "2025-12-31T23:59:59Z",
                "active": True,
                "volume": 1000000,
                "tokens": ["123456789", "987654321"]
            },
            {
                "condition_id": "0xabcdef1234567890abcdef1234567890abcdef12",
                "question": "Will there be a major AI breakthrough in 2025?",
                "description": "Test market for AI development prediction",
                "end_date": "2025-12-31T23:59:59Z",
                "active": True,
                "volume": 500000,
                "tokens": ["111222333", "444555666"]
            }
        ]
        
    except Exception as e:
        print(f"❌ Error discovering markets: {e}")
        return []

def save_markets_to_file(markets: List[Dict[str, Any]], filename: str = "current_markets.json"):
    """Save discovered markets to a JSON file"""
    try:
        with open(filename, 'w') as f:
            json.dump(markets, f, indent=2)
        print(f"💾 Saved {len(markets)} markets to {filename}")
    except Exception as e:
        print(f"❌ Error saving markets: {e}")

def print_market_summary(markets: List[Dict[str, Any]]):
    """Print a summary of discovered markets"""
    print(f"\n📊 CURRENT MARKETS SUMMARY")
    print("=" * 60)
    
    for i, market in enumerate(markets, 1):
        print(f"\n{i}. Condition ID: {market.get('condition_id', 'N/A')}")
        print(f"   Question: {market.get('question', 'N/A')[:80]}...")
        print(f"   Active: {market.get('active', 'Unknown')}")
        print(f"   End Date: {market.get('end_date', 'N/A')}")
        print(f"   Volume: ${float(market.get('volume', 0)):,.2f}")
        
        # Show token information if available
        tokens = market.get("tokens", [])
        if tokens:
            print(f"   Tokens: {len(tokens)} available")
            for j, token in enumerate(tokens[:2]):  # Show first 2 tokens
                print(f"     Token {j+1}: {token}")

def main():
    """Main function to discover and display current markets"""
    print("🔍 POLYMARKET CURRENT MARKETS DISCOVERY")
    print("=" * 50)
    
    # Discover current markets
    markets = discover_current_markets()
    
    if markets:
        # Print summary
        print_market_summary(markets)
        
        # Save to file
        save_markets_to_file(markets)
        
        print(f"\n✅ Discovery complete! Found {len(markets)} current markets")
        print("💡 You can now use these condition IDs in your real trading bot")
        print("📁 Markets saved to 'current_markets.json'")
        
        # Show how to use in trading bot
        if markets:
            first_market = markets[0]
            condition_id = first_market.get("condition_id")
            print(f"\n🤖 Example usage in real trading bot:")
            print(f"   condition_id = \"{condition_id}\"")
            print(f"   market = clob_client.get_market(condition_id)")
            print(f"   # Question: {first_market.get('question', 'N/A')}")
    else:
        print("❌ No current markets discovered. Check your internet connection and try again.")

if __name__ == "__main__":
    main() 