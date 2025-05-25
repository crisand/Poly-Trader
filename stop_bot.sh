#!/bin/bash

# PolyTrader Bot Stopper Script
# Stops the running trading bot

echo "🛑 POLYMARKET TRADING BOT STOPPER"
echo "================================="

# Check if bot.pid file exists
if [ -f "bot.pid" ]; then
    BOT_PID=$(cat bot.pid)
    echo "🔍 Found bot process ID: $BOT_PID"
    
    # Check if process is still running
    if ps -p $BOT_PID > /dev/null; then
        echo "🛑 Stopping trading bot (PID: $BOT_PID)..."
        kill $BOT_PID
        
        # Wait a moment and check if it stopped
        sleep 2
        if ps -p $BOT_PID > /dev/null; then
            echo "⚠️  Bot didn't stop gracefully, forcing termination..."
            kill -9 $BOT_PID
        fi
        
        echo "✅ Trading bot stopped successfully!"
        rm bot.pid
    else
        echo "⚠️  Bot process not found (may have already stopped)"
        rm bot.pid
    fi
else
    echo "🔍 No bot.pid file found, searching for running processes..."
    
    # Try to find and kill any running real_auto_trader.py processes
    PIDS=$(pgrep -f "real_auto_trader.py")
    
    if [ -n "$PIDS" ]; then
        echo "🛑 Found running bot processes: $PIDS"
        echo "🛑 Stopping all trading bot processes..."
        pkill -f "real_auto_trader.py"
        echo "✅ All trading bot processes stopped!"
    else
        echo "ℹ️  No running trading bot processes found"
    fi
fi

echo ""
echo "📊 Final status check:"
REMAINING=$(pgrep -f "real_auto_trader.py" | wc -l)
if [ $REMAINING -eq 0 ]; then
    echo "✅ No trading bot processes running"
else
    echo "⚠️  $REMAINING trading bot processes still running"
    echo "🔍 Use 'ps aux | grep real_auto_trader' to check manually"
fi 