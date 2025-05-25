#!/bin/bash

echo "🤖 STARTING POLYMARKET REAL TRADING BOT"
echo "⚠️  WARNING: This will place REAL trades with REAL money!"
echo "=============================================="

# Activate virtual environment
source venv/bin/activate

# Check USDC balance
echo "💰 Checking USDC balance..."
python3 check_usdc.py

# Check USDC approval
echo "🔐 Checking USDC approval..."
python3 approve_usdc.py

# Discover real markets first
echo "🔍 Discovering real markets..."
python3 discover_markets.py

# Start real trading
echo "🚀 Starting REAL trading..."
echo "⚠️  This will use REAL money - be careful!"
python3 place_real_trades.py 