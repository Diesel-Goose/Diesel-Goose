// Greenhead Labs Dashboard - JavaScript for Real-time Updates

document.addEventListener('DOMContentLoaded', function() {
    // Initial data load
    fetchDashboardData();
    
    // Refresh data every 30 seconds
    setInterval(fetchDashboardData, 30000);
    
    // Update timestamp every minute
    setInterval(updateTimestamp, 60000);
});

async function fetchDashboardData() {
    try {
        const response = await fetch('/api/overview');
        if (!response.ok) throw new Error('Failed to fetch data');
        
        const data = await response.json();
        updateDashboard(data);
    } catch (error) {
        console.error('Error fetching dashboard data:', error);
        showError('Failed to update dashboard data');
    }
}

function updateDashboard(data) {
    // Update last updated time
    const lastUpdated = new Date(data.last_updated);
    document.getElementById('last-updated').textContent = lastUpdated.toLocaleString();
    
    // Update Chris Dunn stats
    if (data.chris_dunn) {
        updateChrisDunnStats(data.chris_dunn);
    }
    
    // Update system status
    if (data.active_systems) {
        updateSystemStatus(data.active_systems);
    }
    
    // Update KPI cards
    updateKPICards(data);
}

function updateChrisDunnStats(stats) {
    const pnlElement = document.getElementById('chris-pnl');
    const winrateElement = document.getElementById('chris-winrate');
    
    if (pnlElement) {
        const pnlUsd = stats.total_pnl_usd || 0;
        const sign = pnlUsd >= 0 ? '+' : '';
        pnlElement.textContent = `${sign}$${pnlUsd.toLocaleString()}`;
        pnlElement.className = 'kpi-value ' + (pnlUsd >= 0 ? 'positive' : 'negative');
    }
    
    if (winrateElement) {
        const winRate = stats.win_rate || 0;
        winrateElement.textContent = `${winRate}% win rate`;
    }
    
    // Update detailed stats if present
    const cdTrades = document.getElementById('cd-trades');
    const cdWinrate = document.getElementById('cd-winrate');
    const cdXrp = document.getElementById('cd-xrp');
    const cdUsd = document.getElementById('cd-usd');
    const cdStrategy = document.getElementById('cd-strategy');
    const cdPrice = document.getElementById('cd-price');
    
    if (cdTrades) cdTrades.textContent = (stats.total_trades || 0).toLocaleString();
    if (cdWinrate) cdWinrate.textContent = `${stats.win_rate || 0}%`;
    if (cdXrp) {
        const xrpPnl = stats.total_pnl_xrp || 0;
        const sign = xrpPnl >= 0 ? '+' : '';
        cdXrp.textContent = `${sign}${xrpPnl.toFixed(2)} XRP`;
        cdXrp.style.color = xrpPnl >= 0 ? 'var(--success)' : 'var(--danger)';
    }
    if (cdUsd) {
        const usdPnl = stats.total_pnl_usd || 0;
        const sign = usdPnl >= 0 ? '+' : '';
        cdUsd.textContent = `${sign}$${usdPnl.toFixed(2)}`;
        cdUsd.style.color = usdPnl >= 0 ? 'var(--success)' : 'var(--danger)';
    }
    if (cdStrategy) cdStrategy.textContent = (stats.latest_strategy || 'Unknown').replace('_', ' ').toUpperCase();
    if (cdPrice) cdPrice.textContent = `$${stats.xrp_price || 1.35}`;
}

function updateSystemStatus(systems) {
    const systemList = document.getElementById('system-list');
    const activeCount = document.getElementById('active-systems');
    
    if (!systemList) return;
    
    let onlineCount = 0;
    let html = '';
    
    systems.forEach(system => {
        const isOnline = system.status === 'online';
        if (isOnline) onlineCount++;
        
        html += `
            <li>
                <span>${system.name}</span>
                <span class="system-status ${system.status}">
                    <span class="status-dot ${system.status}"></span>
                    ${isOnline ? 'Online' : 'Offline'}
                </span>
            </li>
        `;
    });
    
    systemList.innerHTML = html;
    
    if (activeCount) {
        activeCount.textContent = `${onlineCount}/${systems.length}`;
    }
}

function updateKPICards(data) {
    // This can be extended as more financial data becomes available
}

function updateTimestamp() {
    const element = document.getElementById('last-updated');
    if (element) {
        element.textContent = new Date().toLocaleString();
    }
}

function showError(message) {
    console.error(message);
    // Could add a toast notification here
}

// Chris Dunn detailed page specific functions
async function fetchChrisDunnDetails() {
    try {
        const response = await fetch('/api/chris-dunn');
        if (!response.ok) throw new Error('Failed to fetch Chris Dunn data');
        
        const data = await response.json();
        updateChrisDunnPage(data);
    } catch (error) {
        console.error('Error fetching Chris Dunn details:', error);
    }
}

function updateChrisDunnPage(data) {
    // This function will be called on the Chris Dunn detail page
    // to populate charts and detailed statistics
    console.log('Chris Dunn data:', data);
}

// Auto-refresh for Chris Dunn page
if (window.location.pathname.includes('chris-dunn')) {
    fetchChrisDunnDetails();
    setInterval(fetchChrisDunnDetails, 30000);
}
