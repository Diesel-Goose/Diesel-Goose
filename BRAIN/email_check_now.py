#!/usr/bin/env python3
"""
email_check_now.py – Immediate inbox check
Checks dieselgoose.ai@gmail.com for ANY new emails
"""

import imaplib
import email
import json
from pathlib import Path

CREDENTIALS_FILE = Path.home() / ".openclaw" / "credentials" / "gmail-app-password.json"

def check_all_emails():
    with open(CREDENTIALS_FILE, 'r') as f:
        creds = json.load(f)
    
    mail = imaplib.IMAP4_SSL(creds["imap_server"], creds["imap_port"])
    password = creds["app_password"].replace(" ", "")
    mail.login(creds["email"], password)
    mail.select('inbox')
    
    # Search ALL unread emails (not just from Chairman)
    status, messages = mail.search(None, 'UNSEEN')
    
    if status == 'OK' and messages[0]:
        msg_ids = messages[0].split()
        print(f"📧 Found {len(msg_ids)} unread email(s):\n")
        
        for msg_id in msg_ids:  # Show all
            status, msg_data = mail.fetch(msg_id, '(RFC822)')
            if status == 'OK':
                raw_email = msg_data[0][1]
                email_msg = email.message_from_bytes(raw_email)
                
                subject = email_msg['Subject'] or "(No subject)"
                sender = email_msg['From']
                date = email_msg['Date']
                
                print(f"From: {sender}")
                print(f"Subject: {subject}")
                print(f"Date: {date}")
                print("-" * 50)
                
                # Try to get body
                if email_msg.is_multipart():
                    for part in email_msg.walk():
                        if part.get_content_type() == "text/plain":
                            try:
                                body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                                print(f"\nBody preview:\n{body[:500]}...")
                                break
                            except:
                                pass
                else:
                    try:
                        body = email_msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                        print(f"\nBody preview:\n{body[:500]}...")
                    except:
                        pass
                
                print("\n" + "=" * 50 + "\n")
    else:
        print("📭 No unread emails found")
    
    mail.logout()

if __name__ == "__main__":
    check_all_emails()
