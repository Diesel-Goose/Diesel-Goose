# 🦆 Quack-Dashboard - Greenhead Labs Financial Dashboard

A secure, real-time financial dashboard for monitoring Greenhead Labs operations,
including Chris Dunn trading performance, crypto wallets, and company financials.

## 🚀 Quick Start

### Local Development (Mac Mini)

```bash
cd Quack-Dashboard
pip install -r requirements.txt
python app.py
```

Then open: http://localhost:5000

### Deploy to Replit

1. Create new Replit project
2. Import from GitHub: `Diesel-Goose/Diesel-Goose`
3. Set run command: `python Quack-Dashboard/app.py`
4. Click Run!

## 🔐 Login Credentials

- **Username:** `admin`
- **Password:** `greenhead2025`

## 📊 Dashboard Features

### Executive Overview
- Real-time system status
- Chris Dunn trading P&L
- KPI cards with live data

### Chris Dunn Trading
- Total trades & win rate
- XRP/USD profit tracking
- Live price feeds ($1.35 XRP)
- Strategy distribution charts
- Trading performance graphs

### Financial Dashboards
- **P&L Statement:** Revenue, expenses, net income
- **Cash Flow:** Operating, investing, financing activities
- **Balance Sheet:** Assets, liabilities, equity
- **Crypto Wallets:** XRP tracking (Xaman integration ready)

### System Monitoring
- Diesel-Goose agent status
- Heartbeat monitoring
- GitHub sync status
- Resource utilization

## 🛠️ Technology Stack

- **Backend:** Python Flask
- **Frontend:** HTML5, CSS3, vanilla JavaScript
- **Charts:** Chart.js
- **Styling:** Custom CSS with dark theme
- **APIs:** CoinGecko (free tier)

## 📁 Project Structure

```
Quack-Dashboard/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .replit               # Replit configuration
├── static/
│   ├── css/
│   │   └── dashboard.css # Main stylesheet
│   └── js/
│       └── dashboard.js  # Real-time updates
└── templates/
    ├── login.html        # Secure login page
    ├── dashboard.html    # Executive overview
    ├── chris_dunn.html   # Trading dashboard
    ├── financials.html   # Financial overview
    ├── pnl.html          # Profit & Loss
    ├── cash_flow.html    # Cash flow statement
    ├── crypto_wallets.html # Wallet tracking
    ├── diesel_goose.html # System monitoring
    ├── 404.html          # Error page
    └── 500.html          # Error page
```

## 🔒 Security Features

- Password hashing (SHA-256)
- Session-based authentication
- Login required for all routes
- Secure secret key generation

## 🔄 Real-Time Updates

- Dashboard refreshes every 30 seconds
- Live XRP price from CoinGecko
- Real trade data from Chris Dunn logs
- System status checks

## 📝 Future Enhancements

- [ ] Xaman wallet integration
- [ ] Bank account connections
- [ ] Automated P&L exports
- [ ] Mobile-responsive improvements
- [ ] Multi-user support
- [ ] Role-based access control

## 🐛 Troubleshooting

**Port already in use:**
```bash
# Kill existing process
pkill -f "python app.py"

# Or use different port
FLASK_RUN_PORT=5001 python app.py
```

**Missing dependencies:**
```bash
pip install -r requirements.txt
```

## 📧 Support

For issues or feature requests, contact:
- Email: nathan@greenhead.io
- Telegram: @DieselGoose

---

**Greenhead Labs** 🦆⚡️
*Built with relentless execution*
