"""
Trading Logger — Audit trail for all operations
"""

import logging
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from logging.handlers import RotatingFileHandler


class TradingLogger:
    """
    Comprehensive logging for trading operations.
    
    Creates two logs:
    1. Application log (chris_dunn.log) — debug/info/warning/error
    2. Trade log (trades.csv) — audit trail of all trades
    """
    
    def __init__(self, config: Dict):
        self.config = config.get('logging', {})
        
        # Setup directories
        self.log_dir = Path('logs')
        self.log_dir.mkdir(exist_ok=True)
        
        # Configure application logger
        self.logger = logging.getLogger('ChrisDunn')
        self.logger.setLevel(self._get_log_level())
        
        # Clear existing handlers
        self.logger.handlers = []
        
        # Console handler
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console.setFormatter(console_formatter)
        self.logger.addHandler(console)
        
        # File handler
        log_file = self.log_dir / self.config.get('file', 'chris_dunn.log')
        max_bytes = self.config.get('max_file_size_mb', 10) * 1024 * 1024
        backup_count = self.config.get('backup_count', 5)
        
        file_handler = RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # Trade log (CSV)
        self.trade_log = self.log_dir / self.config.get('trade_log', 'trades.csv')
        self._init_trade_log()
    
    def _get_log_level(self) -> int:
        """Convert config string to logging level."""
        level = self.config.get('level', 'INFO')
        levels = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR
        }
        return levels.get(level, logging.INFO)
    
    def _init_trade_log(self):
        """Initialize trade log CSV if not exists."""
        if not self.trade_log.exists():
            with open(self.trade_log, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'mode', 'strategy', 'type', 'side',
                    'amount', 'price', 'value_usd', 'tx_hash',
                    'status', 'pnl', 'notes'
                ])
    
    def debug(self, message: str):
        """Log debug message."""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log info message."""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error message."""
        self.logger.error(message)
    
    def log_trade(self, trade: Dict[str, Any]):
        """Log trade to CSV audit trail."""
        try:
            with open(self.trade_log, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.utcnow().isoformat(),
                    trade.get('mode', 'unknown'),
                    trade.get('strategy', 'unknown'),
                    trade.get('type', 'unknown'),
                    trade.get('side', ''),
                    trade.get('amount', 0),
                    trade.get('price', 0),
                    trade.get('value_usd', 0),
                    trade.get('tx_hash', ''),
                    trade.get('status', ''),
                    trade.get('pnl', 0),
                    trade.get('notes', '')
                ])
        except Exception as e:
            self.logger.error(f"Failed to log trade: {e}")
