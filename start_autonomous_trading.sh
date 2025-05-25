#!/bin/bash

echo "🤖 STARTING POLYMARKET AUTONOMOUS TRADING BOT"
echo "=============================================="

# Activate virtual environment
source venv/bin/activate

# Check USDC balance
echo "💰 Checking USDC balance..."
python3 check_usdc.py

# Check USDC approval
echo "🔐 Checking USDC approval..."
python3 approve_usdc.py

# Start autonomous trading
echo "🚀 Starting autonomous trading..."
python3 place_programmatic_bet.py 