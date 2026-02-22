# Duck-Pond System Documentation

**Repository:** Diesel-Goose/Duck-Pond  
**Purpose:** Core operational system for Greenhead Labs  
**Last Updated:** 2026-02-22

---

## System Architecture

```
Duck-Pond/
├── System/           # Core operational scripts
├── KB/              # Knowledge base
├── Journal/         # Daily journals
├── Projects/        # Active projects
└── .credentials/    # Local secrets (git-ignored)
```

---

## Core Scripts Reference

### 1. telegram_heartbeat.py
**Purpose:** Send automated status updates to Telegram and log to HEARTBEAT.md

**Usage:**
```bash
python3 telegram_heartbeat.py
```

**What it does:**
- Reads current status from HEARTBEAT.md
- Sends formatted message to Telegram
- Appends entry to workspace HEARTBEAT.md
- Triggers GitHub sync

**Dependencies:** requests

---

### 2. email_monitor.py
**Purpose:** Monitor Gmail inbox for Chairman directives

**Usage:**
```bash
python3 email_monitor.py
```

**What it does:**
- Connects to Gmail IMAP
- Scans for whitelisted sender emails
- Extracts action items from messages
- Logs to email_log.json

**Credentials:** Loads from `.credentials/credentials.json`

**Configuration:**
```json
{
  "gmail": {
    "email": "nathan@greenhead.io",
    "app_password": "xxxx xxxx xxxx xxxx"
  }
}
```

---

### 3. generate-morning-journal.py
**Purpose:** Generate daily morning journal entry

**Usage:**
```bash
python3 generate-morning-journal.py
```

**What it does:**
- Reads yesterday's journal
- Generates new entry with date
- Saves to Journal/ folder

---

### 4. duck-pond.sh
**Purpose:** Main Duck-Pond CLI interface

**Usage:**
```bash
./duck-pond.sh [command]
```

**Commands:**
- `vault` — Access encrypted vault
- `search` — Search knowledge base
- `journal` — Journal operations
- `status` — System status

**Features:**
- Interactive fzf menus
- GPG encryption for sensitive data
- Knowledge base indexing

---

### 5. mercury_client.py
**Purpose:** Mercury Banking API integration

**Usage:**
```python
from mercury_client import MercuryClient
client = MercuryClient()
accounts = client.get_accounts()
```

**Capabilities:**
- List accounts and balances
- View transactions
- Initiate transfers (requires approval)

**Credentials:** Loads from `.credentials/credentials.json`

---

### 6. xaman_client.py
**Purpose:** Xaman (XRP) Wallet API integration

**Usage:**
```python
from xaman_client import XamanClient
client = XamanClient()
```

**Capabilities:**
- Check XRP balance
- View transaction history
- Sign transactions (requires manual approval)

**Credentials:** Loads from `.credentials/credentials.json`

---

### 7. brave_search.py
**Purpose:** Brave Search API wrapper

**Usage:**
```python
from brave_search import BraveSearch
search = BraveSearch()
results = search.web_search("query")
```

**Capabilities:**
- Web search
- News search
- Rate-limited to save costs

**Credentials:** Loads from `.credentials/credentials.json`

---

### 8. vault_core.py
**Purpose:** Encrypted vault management

**Usage:**
```bash
python3 vault_core.py [command]
```

**Features:**
- AES-256-GCM encryption
- Key derivation from master password
- Secure file storage

**Storage:** `.vault/` directory

---

### 9. llm_wrapper.py
**Purpose:** OpenAI API wrapper with cost tracking

**Usage:**
```python
from llm_wrapper import LLMWrapper
llm = LLMWrapper()
response = llm.generate("prompt")
```

**Features:**
- Token counting
- Cost tracking
- Rate limiting

**Credentials:** Uses `OPENAI_API_KEY` environment variable

---

## Credential Management

### File Structure
```
.credentials/
└── credentials.json
```

### Format
```json
{
  "brave_search": {
    "api_key": "..."
  },
  "mercury": {
    "api_key": "..."
  },
  "xaman": {
    "api_key": "...",
    "api_secret": "..."
  },
  "gmail": {
    "email": "...",
    "app_password": "..."
  }
}
```

### Security
- File is git-ignored
- Permissions: 600 (owner only)
- Directory: 700 (owner only)

---

## Operational Runbooks

### Daily Operations

**Morning Startup:**
```bash
# Check system status
./duck-pond.sh status

# Generate morning journal
python3 generate-morning-journal.py

# Start heartbeat monitor
cd ~/.openclaw/workspace && ./persistent_heartbeat.sh start
```

**Throughout Day:**
```bash
# Check monitor status
./persistent_heartbeat.sh status

# View recent logs
tail -f ~/.openclaw/logs/monitor.log
```

**Evening Shutdown:**
```bash
# Stop monitor (if needed)
./persistent_heartbeat.sh stop

# Sync everything
git add -A && git commit -m "Daily sync" && git push
```

### Adding New Credentials

1. Edit `.credentials/credentials.json`
2. Verify permissions: `chmod 600 .credentials/credentials.json`
3. Test the service
4. NEVER commit to git

### Troubleshooting

**Heartbeat not sending:**
```bash
# Check screen session
screen -ls

# Restart monitor
./persistent_heartbeat.sh restart

# Check logs
tail ~/.openclaw/logs/monitor.log
```

**Email monitor not working:**
```bash
# Test credentials
python3 -c "import json; print(json.load(open('.credentials/credentials.json'))['gmail'])"

# Check email_alerts_errors.log
cat ~/.openclaw/logs/email_alerts_errors.log
```

**Vault locked:**
```bash
# Unlock vault
python3 vault_core.py unlock
```

---

## Integration Points

### GitHub
- Workspace repo: Diesel-Goose/Diesel-Goose
- Duck-Pond repo: Diesel-Goose/Duck-Pond

### APIs
- Telegram (bot notifications)
- Mercury (banking)
- Xaman (XRP wallet)
- Brave Search
- OpenAI
- Gmail (IMAP)

### Local Services
- macOS LaunchAgent (deprecated, use screen/tmux)
- Screen session (persistent heartbeat)

---

## Maintenance Schedule

| Task | Frequency | Command |
|------|-----------|---------|
| Security audit | Weekly | `./self_monitor.sh check` |
| Credential rotation | Quarterly | Manual |
| Log cleanup | Monthly | `find ~/.openclaw/logs -name "*.log" -mtime +30 -delete` |
| Full backup | Weekly | `git push` |

---

*Documentation maintained by DieselGoose Agent*
