#!/usr/bin/env python3
"""
Environment Setup Helper for Polymarket Trading Bot

This script helps you set up the required environment variables
for the Polymarket trading bot to work properly.
"""

import os
from dotenv import load_dotenv

def check_environment():
    """Check current environment configuration"""
    load_dotenv()
    
    print("🔍 POLYMARKET TRADING BOT - ENVIRONMENT CHECK")
    print("=" * 60)
    
    required_vars = {
        "POLYGON_WALLET_PRIVATE_KEY": "Your Polygon wallet private key (64 hex characters)",
        "POLYMARKET_WALLET_ADDRESS": "Your wallet address (optional, derived from private key)",
        "OPENAI_API_KEY": "OpenAI API key for market analysis",
        "SERPAPI_API_KEY": "SerpAPI key for market data (optional)",
        "POLYMARKET_API_KEY": "Polymarket API key (optional)",
    }
    
    missing_vars = []
    invalid_vars = []
    
    for var_name, description in required_vars.items():
        value = os.getenv(var_name, "")
        
        if not value:
            missing_vars.append(var_name)
            print(f"❌ {var_name}: Not set")
        elif var_name == "POLYGON_WALLET_PRIVATE_KEY":
            if len(value) != 64 and len(value) != 66:  # 64 chars or 66 with 0x prefix
                invalid_vars.append(var_name)
                print(f"⚠️  {var_name}: Invalid format (should be 64 hex characters)")
            elif value.startswith("your_") or "placeholder" in value.lower():
                invalid_vars.append(var_name)
                print(f"⚠️  {var_name}: Still using placeholder value")
            else:
                print(f"✅ {var_name}: Configured")
        else:
            if value.startswith("your_") or "placeholder" in value.lower():
                invalid_vars.append(var_name)
                print(f"⚠️  {var_name}: Still using placeholder value")
            else:
                print(f"✅ {var_name}: Configured")
    
    print("\n" + "=" * 60)
    
    if missing_vars or invalid_vars:
        print("❌ CONFIGURATION ISSUES FOUND")
        print("\nTo fix these issues:")
        print("1. Create a .env file in the project root directory")
        print("2. Add the following variables with your actual values:")
        print()
        
        for var_name, description in required_vars.items():
            if var_name in missing_vars or var_name in invalid_vars:
                print(f"{var_name}=your_actual_value_here  # {description}")
        
        print("\n📝 IMPORTANT NOTES:")
        print("- Your private key should be 64 hexadecimal characters (no 0x prefix needed)")
        print("- Never share your private key or commit it to version control")
        print("- You can get your private key from MetaMask or your wallet app")
        print("- Make sure your wallet has MATIC for gas and USDC for trading")
        
        return False
    else:
        print("✅ ALL ENVIRONMENT VARIABLES CONFIGURED CORRECTLY")
        print("\n🚀 You can now run the trading bot:")
        print("   python3 real_auto_trader.py")
        return True

def create_env_template():
    """Create a .env template file"""
    template = """# Polymarket Trading Bot Environment Variables
# Copy this file to .env and fill in your actual values

# REQUIRED: Your Polygon wallet private key (64 hex characters, no 0x prefix)
POLYGON_WALLET_PRIVATE_KEY=your_64_character_hex_private_key_here

# OPTIONAL: Your wallet address (will be derived from private key if not provided)
POLYMARKET_WALLET_ADDRESS=your_wallet_address_here

# REQUIRED: OpenAI API key for market analysis
OPENAI_API_KEY=your_openai_api_key_here

# OPTIONAL: SerpAPI key for enhanced market data
SERPAPI_API_KEY=your_serpapi_api_key_here

# OPTIONAL: Polymarket API credentials (for advanced features)
POLYMARKET_API_KEY=your_polymarket_api_key_here
POLYMARKET_API_SECRET=your_polymarket_api_secret_here
POLYMARKET_API_PASSPHRASE=your_polymarket_api_passphrase_here

# Flask settings (for web interface)
FLASK_SECRET_KEY=your_flask_secret_key_here

# Trading settings (optional, defaults will be used)
INITIAL_BANKROLL=1000
MAX_BET_PERCENTAGE=0.05
MIN_EDGE_PERCENTAGE=0.15
"""
    
    if not os.path.exists(".env"):
        with open(".env.template", "w") as f:
            f.write(template)
        print("📝 Created .env.template file")
        print("   Copy this to .env and fill in your actual values")
    else:
        print("📝 .env file already exists")

if __name__ == "__main__":
    print("🔧 POLYMARKET TRADING BOT SETUP")
    print("=" * 40)
    
    if not check_environment():
        print("\n" + "=" * 40)
        create_env_template()
        print("\n💡 Next steps:")
        print("1. Copy .env.template to .env")
        print("2. Edit .env with your actual credentials")
        print("3. Run this script again to verify setup")
        print("4. Start trading with: python3 real_auto_trader.py")
    else:
        print("\n🎉 Setup complete! Ready to trade.") 