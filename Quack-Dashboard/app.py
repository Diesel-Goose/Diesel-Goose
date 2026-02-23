# Greenhead Labs Dashboard
# A secure financial dashboard for company performance monitoring
# Deployable to Replit or local Mac Mini

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from functools import wraps
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import hashlib
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)  # Secure random secret

# Configuration
DASHBOARD_DIR = Path(__file__).parent
DATA_DIR = DASHBOARD_DIR / "data"
CHRIS_DUNN_LOGS = Path("/Users/dieselgoose/.openclaw/workspace/GreenheadLabs/EMPLOYEES/CFO/SPECIALIST-CFO-03/logs")

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

# Admin credentials (hashed for security)
# Default: username: admin, password: greenhead2025
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = hashlib.sha256("greenhead2025".encode()).hexdigest()

def login_required(f):
    """Decorator to require login for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page with username/password authentication."""
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        # Hash provided password and compare
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        if username == ADMIN_USERNAME and password_hash == ADMIN_PASSWORD_HASH:
            session['logged_in'] = True
            session['username'] = username
            session['login_time'] = datetime.now().isoformat()
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid credentials. Please try again.'
    
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    """Logout and clear session."""
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    """Main dashboard with overview of all metrics."""
    return render_template('dashboard.html', 
                         current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

@app.route('/api/overview')
@login_required
def api_overview():
    """API endpoint for dashboard overview data."""
    return jsonify({
        'company_name': 'Greenhead Labs',
        'last_updated': datetime.now().isoformat(),
        'status': 'operational',
        'active_systems': get_active_systems(),
        'chris_dunn': get_chris_dunn_stats(),
        'financial_summary': get_financial_summary()
    })

@app.route('/api/chris-dunn')
@login_required
def api_chris_dunn():
    """API endpoint for Chris Dunn trading data."""
    return jsonify(get_chris_dunn_stats())

@app.route('/chris-dunn')
@login_required
def chris_dunn_page():
    """Dedicated Chris Dunn trading dashboard."""
    return render_template('chris_dunn.html')

@app.route('/financials')
@login_required
def financials_page():
    """Financial overview page."""
    return render_template('financials.html')

@app.route('/cash-flow')
@login_required
def cash_flow_page():
    """Cash flow dashboard."""
    return render_template('cash_flow.html')

@app.route('/pnl')
@login_required
def pnl_page():
    """Profit & Loss dashboard."""
    return render_template('pnl.html')

@app.route('/crypto-wallets')
@login_required
def crypto_wallets_page():
    """Crypto wallet tracking dashboard."""
    return render_template('crypto_wallets.html')

@app.route('/diesel-goose')
@login_required
def diesel_goose_page():
    """Diesel-Goose system stats dashboard."""
    return render_template('diesel_goose.html')

# Data Functions
def get_active_systems():
    """Check status of all Greenhead Labs systems."""
    systems = []
    
    # Check Chris Dunn
    import subprocess
    try:
        result = subprocess.run(['pgrep', '-f', 'continuous_runner.py'], 
                              capture_output=True, text=True)
        chris_status = 'online' if result.returncode == 0 else 'offline'
    except:
        chris_status = 'unknown'
    
    systems.append({
        'name': 'Chris Dunn Trading',
        'status': chris_status,
        'type': 'trading_bot'
    })
    
    # Check Self-Monitor
    try:
        result = subprocess.run(['pgrep', '-f', 'self_monitor.sh'], 
                              capture_output=True, text=True)
        monitor_status = 'online' if result.returncode == 0 else 'offline'
    except:
        monitor_status = 'unknown'
    
    systems.append({
        'name': 'Self-Monitor',
        'status': monitor_status,
        'type': 'monitoring'
    })
    
    # Check Simple Reporter
    try:
        result = subprocess.run(['pgrep', '-f', 'simple_reporter.py'], 
                              capture_output=True, text=True)
        reporter_status = 'online' if result.returncode == 0 else 'offline'
    except:
        reporter_status = 'unknown'
    
    systems.append({
        'name': 'Chris Dunn Reporter',
        'status': reporter_status,
        'type': 'reporting'
    })
    
    return systems

def get_chris_dunn_stats():
    """Fetch Chris Dunn trading statistics from logs."""
    stats = {
        'total_trades': 0,
        'win_rate': 0,
        'total_pnl_xrp': 0,
        'total_pnl_usd': 0,
        'xrp_price': 1.35,
        'latest_strategy': 'market_maker',
        'status': 'unknown'
    }
    
    try:
        trades_log = CHRIS_DUNN_LOGS / "trades.log"
        
        if trades_log.exists():
            trades = []
            with open(trades_log, 'r') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) >= 6:
                        try:
                            trades.append({
                                'pnl': float(parts[5]),
                                'strategy': parts[1]
                            })
                        except:
                            continue
            
            if trades:
                total = len(trades)
                wins = len([t for t in trades if t['pnl'] > 0])
                pnl = sum(t['pnl'] for t in trades)
                
                # Get live XRP price
                try:
                    import requests
                    response = requests.get(
                        "https://api.coingecko.com/api/v3/simple/price?ids=ripple&vs_currencies=usd",
                        timeout=3
                    )
                    if response.status_code == 200:
                        xrp_price = response.json().get('ripple', {}).get('usd', 1.35)
                    else:
                        xrp_price = 1.35
                except:
                    xrp_price = 1.35
                
                stats = {
                    'total_trades': total,
                    'win_rate': round((wins / total * 100), 1) if total > 0 else 0,
                    'total_pnl_xrp': round(pnl, 2),
                    'total_pnl_usd': round(pnl * xrp_price, 2),
                    'xrp_price': xrp_price,
                    'latest_strategy': trades[-1]['strategy'] if trades else 'market_maker',
                    'status': 'trading',
                    'winning_trades': wins,
                    'losing_trades': total - wins
                }
    except Exception as e:
        stats['error'] = str(e)
    
    return stats

def get_financial_summary():
    """Get Greenhead Labs financial summary."""
    # Placeholder for now - will integrate with actual financial data
    return {
        'total_assets': 0,
        'total_liabilities': 0,
        'equity': 0,
        'cash_on_hand': 0,
        'monthly_burn': 0,
        'runway_months': 0
    }

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # For local development
    app.run(host='0.0.0.0', port=5000, debug=True)
