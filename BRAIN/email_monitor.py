#!/usr/bin/env python3
"""
Email Monitor for Chairman Inbox
Checks dieselgoose.ai@gmail.com for emails from nathan@greenhead.io
"""

import imaplib
import email
import os
import json
from datetime import datetime

# Configuration
IMAP_SERVER = "imap.gmail.com"
EMAIL_ACCOUNT = "dieselgoose.ai@gmail.com"
EMAIL_PASSWORD = os.environ.get("DG_EMAIL_PASSWORD", "")
SENDER_FILTER = "nathan@greenhead.io"
STATE_FILE = os.path.expanduser("~/.email_monitor_state.json")

def load_state():
    """Load last checked UID from state file"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except:
            return {"last_uid": 0}
    return {"last_uid": 0}

def save_state(state):
    """Save state to file"""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def check_emails():
    """Check for new emails from specified sender"""
    print(f"🦆 Checking {EMAIL_ACCOUNT} for emails from {SENDER_FILTER}...")
    
    if not EMAIL_PASSWORD:
        print("⚠️  Email password not configured (DG_EMAIL_PASSWORD env var)")
        return []
    
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        mail.select('inbox')
        
        # Search for emails from sender
        status, messages = mail.search(None, f'FROM "{SENDER_FILTER}"')
        
        if status != 'OK' or not messages[0]:
            print("📭 No new emails")
            mail.logout()
            return []
        
        email_ids = messages[0].split()
        state = load_state()
        last_uid = state.get("last_uid", 0)
        new_emails = []
        
        for e_id in email_ids:
            uid = int(e_id)
            if uid > last_uid:
                status, msg_data = mail.fetch(e_id, '(RFC822)')
                if status == 'OK':
                    raw_email = msg_data[0][1]
                    email_message = email.message_from_bytes(raw_email)
                    subject = email_message['Subject']
                    from_addr = email_message['From']
                    date = email_message['Date']
                    new_emails.append({
                        'uid': uid,
                        'subject': subject,
                        'from': from_addr,
                        'date': date
                    })
                    if uid > last_uid:
                        last_uid = uid
        
        mail.logout()
        
        # Save updated state
        state["last_uid"] = last_uid
        save_state(state)
        
        if new_emails:
            print(f"📬 Found {len(new_emails)} new email(s):")
            for e in new_emails:
                print(f"   - {e['subject']}")
        else:
            print("📭 No new emails")
        
        return new_emails
        
    except Exception as e:
        print(f"❌ Error checking emails: {e}")
        return []

if __name__ == "__main__":
    new_emails = check_emails()
    
    # Output results for Telegram notification
    if new_emails:
        print("\n🔔 NEW_EMAILS_FOUND")
        for e in new_emails:
            print(f"SUBJECT:{e['subject']}")
