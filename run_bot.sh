#!/bin/bash

# PolyTrader Bot Runner Script
# Runs the trading bot in the background with proper logging

echo "🤖 POLYMARKET TRADING BOT LAUNCHER"
echo "=================================="

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Virtual environment not activated"
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
fi

# Check environment setup
echo "🔍 Checking environment setup..."
python3 setup_env.py

if [ $? -ne 0 ]; then
    echo "❌ Environment setup incomplete"
    echo "📝 Please configure your .env file first"
    exit 1
fi

echo ""
echo "🚀 Starting trading bot in background..."
echo "📁 Output will be logged to: output.log"
echo "📁 Errors will be logged to: error.log"
echo ""

# Run the bot in background with logging
nohup python3 real_auto_trader.py > output.log 2> error.log &

# Get the process ID
BOT_PID=$!

echo "✅ Trading bot started successfully!"
echo "🆔 Process ID: $BOT_PID"
echo ""
echo "📊 To monitor the bot:"
echo "   tail -f output.log    # View live output"
echo "   tail -f error.log     # View errors"
echo ""
echo "🛑 To stop the bot:"
echo "   kill $BOT_PID"
echo "   # or use: pkill -f real_auto_trader.py"
echo ""
echo "📈 Bot is now running autonomously!"

# Save PID to file for easy stopping
echo $BOT_PID > bot.pid
echo "💾 Process ID saved to bot.pid" 