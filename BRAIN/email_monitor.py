#!/usr/bin/env python3
"""
email_monitor.py – Diesel-Goose Gmail Monitor
Checks dieselgoose.ai@gmail.com for new emails from Chairman
Sends Telegram notification when new email arrives.

Author: Diesel Goose – Founder / Chairman
Version: 1.0 – IMAP-based email monitoring
"""

import imaplib
import email
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Optional

# Telegram notification via OpenClaw message tool
sys.path.insert(0, str(Path(__file__).parent.parent))

# Constants
CREDENTIALS_FILE = Path.home() / ".openclaw" / "credentials" / "gmail-app-password.json"
MEMORY_FILE = Path(__file__).parent.parent / "MEMORY" / "memory_store" / "email_state.json"
CHAIRMAN_EMAIL = "nathan@greenhead.io"
TELEGRAM_TARGET = "7491205261"

class EmailMonitor:
    """Monitors Gmail inbox for Chairman emails."""
    
    def __init__(self):
        self.credentials = self._load_credentials()
        self.last_check = self._load_state()
    
    def _load_credentials(self) -> Dict:
        """Load Gmail credentials."""
        with open(CREDENTIALS_FILE, 'r') as f:
            return json.load(f)
    
    def _load_state(self) -> datetime:
        """Load last checked timestamp."""
        if MEMORY_FILE.exists():
            with open(MEMORY_FILE, 'r') as f:
                data = json.load(f)
                return datetime.fromisoformat(data.get("last_check", "1970-01-01T00:00:00"))
        return datetime(1970, 1, 1, tzinfo=timezone.utc)
    
    def _save_state(self):
        """Save last checked timestamp."""
        MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(MEMORY_FILE, 'w') as f:
            json.dump({
                "last_check": datetime.now(timezone.utc).isoformat(),
                "email": self.credentials["email"]
            }, f)
    
    def check_emails(self) -> List[Dict]:
        """
        Check Gmail for new emails from Chairman.
        
        Returns:
            List of new email dicts with subject, sender, date
        """
        new_emails = []
        
        try:
            # Connect to Gmail IMAP
            mail = imaplib.IMAP4_SSL(
                self.credentials["imap_server"],
                self.credentials["imap_port"]
            )
            
            # Login
            password = self.credentials["app_password"].replace(" ", "")
            mail.login(self.credentials["email"], password)
            
            # Select inbox
            mail.select('inbox')
            
            # Search for emails from Chairman (unseen)
            status, messages = mail.search(None, f'FROM "{CHAIRMAN_EMAIL}"', 'UNSEEN')
            
            if status == 'OK' and messages[0]:
                msg_ids = messages[0].split()
                
                for msg_id in msg_ids:
                    status, msg_data = mail.fetch(msg_id, '(RFC822)')
                    
                    if status == 'OK':
                        raw_email = msg_data[0][1]
                        email_message = email.message_from_bytes(raw_email)
                        
                        # Extract info
                        subject = email_message['Subject'] or "(No subject)"
                        sender = email_message['From']
                        date_str = email_message['Date']
                        
                        new_emails.append({
                            "id": msg_id.decode(),
                            "subject": subject,
                            "sender": sender,
                            "date": date_str
                        })
                        
                        # Mark as seen (optional - uncomment if you want to mark read)
                        # mail.store(msg_id, '+FLAGS', '\\Seen')
            
            mail.logout()
            
        except Exception as e:
            print(f"❌ Email check failed: {e}")
            return []
        
        return new_emails
    
    def send_telegram_notification(self, emails: List[Dict]):
        """Send Telegram notification for new emails."""
        if not emails:
            return
        
        count = len(emails)
        
        if count == 1:
            msg = f"🦆📧 New email from Chairman\n\nSubject: {emails[0]['subject']}\nFrom: {emails[0]['sender']}"
        else:
            msg = f"🦆📧 {count} new emails from Chairman\n"
            for i, email in enumerate(emails[:3], 1):
                msg += f"\n{i}. {email['subject']}"
            if count > 3:
                msg += f"\n...and {count - 3} more"
        
        # Check if running under OpenClaw (has message tool available)
        try:
            # Try importing OpenClaw's message tool
            from openclaw.tools import message
            message(action="send", target=TELEGRAM_TARGET, message=msg)
            print(f"✅ Telegram notification sent via OpenClaw")
        except ImportError:
            # Fallback: log notification for manual delivery
            print(f"📢 NOTIFICATION (send manually):")
            print(f"   Target: {TELEGRAM_TARGET}")
            print(f"   Message: {msg[:100]}...")
    
    def run(self):
        """Main monitoring loop."""
        print(f"🦆 Checking {self.credentials['email']} for emails from {CHAIRMAN_EMAIL}...")
        
        new_emails = self.check_emails()
        
        if new_emails:
            print(f"✅ Found {len(new_emails)} new email(s)")
            self.send_telegram_notification(new_emails)
        else:
            print("📭 No new emails")
        
        self._save_state()
        
        return len(new_emails)


def main():
    """Entry point."""
    if not CREDENTIALS_FILE.exists():
        print(f"❌ Credentials not found: {CREDENTIALS_FILE}")
        sys.exit(1)
    
    monitor = EmailMonitor()
    count = monitor.run()
    sys.exit(0 if count >= 0 else 1)


if __name__ == "__main__":
    main()
