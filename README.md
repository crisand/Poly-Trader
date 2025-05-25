# PolyTrader: AI-Powered Autonomous Trading System for Polymarket

An autonomous AI trading agent for Polymarket that continuously monitors markets, identifies profitable opportunities, and executes trades automatically with advanced risk management and profit optimization.

## 🚀 Getting Started

### Prerequisites

- Python 3.8+ installed
- A Polygon network wallet with MATIC (for gas) and USDC (for trading)
- API keys for OpenAI and SerpAPI
- Basic understanding of prediction markets and crypto wallets

### Quick Start on EC2

```bash
ssh -i "poly.pem" ubuntu@ec2-34-226-150-183.compute-1.amazonaws.com
cd ~/Poly-Trader
git pull origin main
source venv/bin/activate

# Start autonomous trading bot
./start_autonomous_trading.sh
python3 place_real_trades.py
python3 manual_trading.py
```

### Installation

1. Clone this repository

```bash
git clone https://github.com/crisand/Poly-Trader.git
cd Poly-Trader
```

2. Create a virtual environment

```bash
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Set up environment variables

```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

5. Run the application

```bash
python3 app.py
```

6. Visit http://127.0.0.1:5000 in your browser

## 🤖 Autonomous Trading Features

### Core Trading Engine

- **Continuous Market Monitoring:** Scans markets every 5 minutes for opportunities
- **AI-Powered Analysis:** Uses sentiment analysis and market indicators to predict outcomes
- **Edge Detection:** Only trades when expected edge is >15%
- **Kelly Criterion Betting:** Optimal bet sizing with safety margins
- **Risk Management:** Stop-loss, position limits, and drawdown protection

### Trading Configuration

- **Initial Bet Size:** $2.00 USDC
- **Maximum Bet Size:** $20.00 USDC
- **Daily Trade Limit:** 50 trades maximum
- **Minimum Edge Required:** 15%
- **Stop Loss:** 50% drawdown protection
- **Position Limit:** Maximum 10% of balance per trade

### Profit Optimization

- **Dynamic Bet Sizing:** Increases bets after wins, decreases after losses
- **Profit Reinvestment:** Automatically compounds gains
- **Performance Tracking:** Real-time P&L and win rate monitoring

## 📋 Features

- **Market Analysis:** Continuously scans Polymarket for opportunities
- **AI-Powered Predictions:** Uses ChatGPT to analyze various events
- **Edge Detection:** Compares AI predictions with market consensus to find inefficiencies
- **Intelligent Bet Sizing:** Implements Kelly Criterion for optimal bankroll management
- **Automated Execution:** Places trades via Polymarket Agents SDK
- **Risk Management:** Includes safety features to protect your bankroll

## 🏗️ Architecture

The system consists of three core modules:

1. **Analysis Module**

   - Uses ChatGPT to analyze upcoming events
   - Compares predictions with current Polymarket odds
   - Identifies opportunities with significant edge

2. **Decision Module**

   - Evaluates opportunities based on edge percentage
   - Calculates optimal bet size using Kelly Criterion
   - Manages risk to preserve bankroll

3. **Execution Module**
   - Connects to Polymarket using their official Agents SDK
   - Places trades automatically with verification
   - Implements safety measures and error handling

## ⚙️ Configuration

Edit your `.env` file with the following variables:

```bash
# OpenAI API key (required for AI functionality)
OPENAI_API_KEY=your_openai_api_key_here

# Flask app settings
FLASK_SECRET_KEY=your_flask_secret_key_here

# SerpAPI key (required for market data)
SERPAPI_API_KEY=your_serpapi_api_key_here

# Polymarket API credentials
POLYMARKET_API_KEY=your_polymarket_api_key_here

# Wallet information (required for transactions)
POLYGON_WALLET_PRIVATE_KEY=your_private_key_here
POLYMARKET_WALLET_ADDRESS=your_wallet_address_here

# Trading settings
INITIAL_BANKROLL=1000
MAX_BET_PERCENTAGE=0.05
MIN_EDGE_PERCENTAGE=0.15
```

> ⚠️ **IMPORTANT**: Never commit your `.env` file or hardcode API keys in the source code. The `.env` file is included in `.gitignore` to prevent accidental exposure of your credentials.

## 🚀 Usage

### Autonomous Trading (Recommended)

Start the autonomous trading bot:

```bash
./start_autonomous_trading.sh
```

Or manually:

```bash
source venv/bin/activate
python3 place_programmatic_bet.py
```

### Web Interface

Start the web interface:

```bash
python app.py
```

### Manual Analysis

Analyze specific markets:

```bash
python polymarket_ai_search.py --query "NBA games tonight"
```

## 📊 Trading Commands

### Check Balance and Approval

```bash
source venv/bin/activate && python3 check_usdc.py
python3 approve_usdc.py
```

### Start Autonomous Trading

```bash
python3 place_programmatic_bet.py
```

### Manual Single Bet

```bash
python3 place_polymarket_bet.py
```

## ⚠️ Risk Warning

Trading involves substantial risk and is not suitable for all investors. Past performance is not indicative of future results. Start with small amounts to test the system before scaling up. Implement proper risk management.

## 🔍 Main Files

- `place_programmatic_bet.py` - **Autonomous trading bot (main)**
- `start_autonomous_trading.sh` - **Quick start script**
- `app.py` - Main entry point for the Flask application
- `polymarket_ai_search.py` - Search and analysis of Polymarket events
- `place_polymarket_bet.py` - Manual bet execution
- `check_usdc.py` - Balance checking utility
- `approve_usdc.py` - USDC approval utility

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

Siraj Raval

## 🙏 Acknowledgements

- OpenAI for ChatGPT API
- Polymarket team for the Agents SDK
- All contributors and testers

---

⭐ Star this repo if you find it useful! Join our Discord community to discuss improvements and share results.

**Note:** This system is for educational purposes. Always do your own research before trading.
