#!/usr/bin/env python3
"""
email_search.py – Search ALL emails for year plan
"""

import imaplib
import email
import json
from pathlib import Path

CREDENTIALS_FILE = Path.home() / ".openclaw" / "credentials" / "gmail-app-password.json"

def search_all_emails():
    with open(CREDENTIALS_FILE, 'r') as f:
        creds = json.load(f)
    
    mail = imaplib.IMAP4_SSL(creds["imap_server"], creds["imap_port"])
    password = creds["app_password"].replace(" ", "")
    mail.login(creds["email"], password)
    mail.select('inbox')
    
    # Search ALL emails
    status, messages = mail.search(None, 'ALL')
    
    if status == 'OK' and messages[0]:
        msg_ids = messages[0].split()
        print(f"📧 Total emails: {len(msg_ids)}\n")
        
        # Check last 20 emails
        for msg_id in msg_ids[-20:]:
            status, msg_data = mail.fetch(msg_id, '(RFC822)')
            if status == 'OK':
                raw_email = msg_data[0][1]
                email_msg = email.message_from_bytes(raw_email)
                
                subject = email_msg['Subject'] or "(No subject)"
                sender = email_msg['From']
                
                # Look for keywords
                if any(word in subject.lower() for word in ['plan', 'year', '3', '5', '10', 'strategic']):
                    print(f"🎯 MATCH:")
                    print(f"   From: {sender}")
                    print(f"   Subject: {subject}")
                    print()
                    
                    # Get body
                    body = ""
                    if email_msg.is_multipart():
                        for part in email_msg.walk():
                            if part.get_content_type() == "text/plain":
                                try:
                                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                                    break
                                except:
                                    pass
                    else:
                        try:
                            body = email_msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                        except:
                            pass
                    
                    if body:
                        print(f"   Content:\n{body}")
                        print("\n" + "="*60 + "\n")
    
    mail.logout()

if __name__ == "__main__":
    search_all_emails()
