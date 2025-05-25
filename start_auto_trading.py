#!/usr/bin/env python3
"""
Polymarket Automated Trading Launcher

Starts the most advanced automated trading bot available.
Automatically selects the best trading method based on available dependencies.
"""

import os
import sys
import subprocess
import time

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded .env file")
except ImportError:
    print("⚠️ python-dotenv not available, trying to install...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "python-dotenv"], 
                     check=True, capture_output=True)
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Installed and loaded .env file")
    except:
        print("❌ Could not load .env file")

def check_dependencies():
    """Check which trading bots are available"""
    available_bots = []
    
    # Check for py-clob-client
    try:
        import py_clob_client
        available_bots.append("real_auto_trader")
        print("✅ py-clob-client available - Real trading enabled")
    except ImportError:
        print("⚠️ py-clob-client not available")
    
    # Check for selenium
    try:
        import selenium
        available_bots.append("hybrid_auto_trader")
        print("✅ Selenium available - Browser automation enabled")
    except ImportError:
        print("⚠️ Selenium not available")
    
    # Advanced auto trader is always available
    available_bots.append("advanced_auto_trader")
    print("✅ Advanced simulation trader available")
    
    return available_bots

def install_dependencies():
    """Install required dependencies"""
    print("🔧 Installing required dependencies...")
    
    dependencies = [
        "py-clob-client",
        "selenium",
        "web3",
        "python-dotenv",
        "requests"
    ]
    
    for dep in dependencies:
        try:
            print(f"Installing {dep}...")
            subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                         check=True, capture_output=True)
            print(f"✅ {dep} installed successfully")
        except subprocess.CalledProcessError:
            print(f"⚠️ Failed to install {dep}")

def check_environment():
    """Check if environment is properly configured"""
    required_vars = [
        "POLYGON_WALLET_PRIVATE_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value or value == "your_private_key_here":
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing or invalid environment variables:")
        for var in missing_vars:
            current_value = os.getenv(var, "NOT_SET")
            print(f"   - {var}: {current_value}")
        print("\n📝 Please edit your .env file and set your actual private key")
        print("💡 Replace 'your_private_key_here' with your real private key")
        return False
    
    print("✅ Environment variables configured")
    return True

def select_trading_bot(available_bots):
    """Select the best available trading bot"""
    if "real_auto_trader" in available_bots:
        return "real_auto_trader.py", "Real Automated Trader (py-clob-client)"
    elif "hybrid_auto_trader" in available_bots:
        return "hybrid_auto_trader.py", "Hybrid Automated Trader (Multiple methods)"
    else:
        return "advanced_auto_trader.py", "Advanced Simulation Trader"

def main():
    """Main launcher function"""
    print("🚀 POLYMARKET AUTOMATED TRADING LAUNCHER")
    print("=" * 60)
    print("🤖 Selecting the best automated trading bot...")
    print("💰 Preparing for maximum profit generation")
    print("=" * 60)
    
    # Check environment
    if not check_environment():
        print("\n❌ Environment not properly configured")
        print("Please check your .env file and try again")
        return
    
    # Check dependencies
    print("\n🔍 Checking available trading methods...")
    available_bots = check_dependencies()
    
    # Install missing dependencies
    install_choice = input("\n🔧 Install missing dependencies? (y/n): ")
    if install_choice.lower() == 'y':
        install_dependencies()
        # Re-check after installation
        available_bots = check_dependencies()
    
    # Select best bot
    bot_file, bot_name = select_trading_bot(available_bots)
    
    print(f"\n🎯 Selected: {bot_name}")
    print(f"📁 File: {bot_file}")
    
    # Confirm launch
    print(f"\n⚠️  WARNING: This will start automated trading with real money!")
    print(f"💰 Make sure you understand the risks involved")
    confirm = input("🚀 Start automated trading? (yes/no): ")
    
    if confirm.lower() != 'yes':
        print("❌ Automated trading cancelled")
        return
    
    print(f"\n🚀 LAUNCHING {bot_name.upper()}")
    print("=" * 60)
    print("💡 The bot will now trade automatically")
    print("⏹️  Press Ctrl+C to stop trading")
    print("📊 Monitor the output for trading activity")
    print("=" * 60)
    
    # Launch the selected bot
    try:
        subprocess.run([sys.executable, bot_file])
    except KeyboardInterrupt:
        print("\n🛑 Automated trading stopped by user")
    except Exception as e:
        print(f"\n❌ Error running trading bot: {e}")

if __name__ == "__main__":
    main() 