# 🔐 DieselGoose Repository Rules & Security Policy

**Version:** 1.0  
**Last Updated:** 2026-02-19  
**Applies To:** Diesel-Goose/Diesel-Goose Repository

---

## ⚠️ CRITICAL SECURITY NOTICE

**This repository is PUBLIC and OPEN SOURCE.**  
**NO SENSITIVE DATA SHOULD EVER BE COMMITTED HERE.**

DieselGoose operates as a Board Member of Greenhead Labs with access to sensitive business information, API keys, and operational data. This repository contains ONLY public-facing documentation, operational logic, and safe configuration files.

---

## 🚫 NEVER COMMIT TO THIS REPO

The following must **NEVER** be pushed to GitHub under any circumstances:

### Secrets & Credentials
- ❌ API keys (OpenAI, Moonshot, Telegram, Slack, etc.)
- ❌ Wallet private keys or seed phrases
- ❌ Passwords or authentication tokens
- ❌ OAuth credentials
- ❌ Session cookies

### Personal & Private Data
- ❌ Personal identification information
- ❌ Private email addresses (except public contact)
- ❌ Home addresses or phone numbers
- ❌ Private conversation logs
- ❌ Session transcripts containing sensitive data

### Business Sensitive Information
- ❌ Financial account details
- ❌ Unreleased product specifications
- ❌ Customer or user data
- ❌ Internal security procedures
- ❌ Competitive intelligence

### System Files
- ❌ `.env` files
- ❌ `.secrets.md` files
- ❌ Token storage files
- ❌ Local configuration with credentials
- ❌ SSH keys or certificates

---

## ✅ SAFE TO COMMIT

The following are **APPROVED** for this public repository:

### Identity & Documentation
- ✅ `AGENTS.md` — Core operational instructions
- ✅ `IDENTITY.md` — Public persona and role definition
- ✅ `SOUL.md` — Mission and motivation (non-sensitive)
- ✅ `HEARTBEAT.md` — Health monitoring framework
- ✅ `README.md` — Public documentation
- ✅ `RULES.md` — This file

### Templates & Logic
- ✅ Status report templates (without actual data)
- ✅ Operational logic and workflows
- ✅ Architecture documentation
- ✅ Public API integration patterns (without keys)
- ✅ Configuration templates (with placeholders)

### Public Business Info
- ✅ Public contact information
- ✅ General business strategy (non-proprietary)
- ✅ Public metrics and KPIs
- ✅ Marketing materials
- ✅ Public roadmap items

---

## 🏠 LOCAL-ONLY STORAGE

**All sensitive data remains on the local Mac Mini M4 ONLY.**

Until dual SSD backup is established (scheduled for Monday), sensitive information is stored exclusively on local encrypted storage. This includes:

- API credentials and tokens
- Wallet private keys
- Session data
- Business sensitive documents
- Internal analytics

**Local Storage Path:** `/Users/dieselgoose/.openclaw/workspace/`

**Sensitive Files (Local Only):**
- `.secrets.md`
- `.env`
- `.slack_token`
- `.openclaw/`
- `temp-brain/` (if contains sensitive data)

---

## 🔍 PRE-COMMIT CHECKLIST

Before every commit, verify:

- [ ] Does this file contain any API keys or tokens?
- [ ] Does this file contain any passwords?
- [ ] Does this file contain wallet private keys or seeds?
- [ ] Does this file contain personal information?
- [ ] Does this file contain business-sensitive data?
- [ ] Would I be comfortable if this was on the front page of Hacker News?

**If NO to all checks → Safe to commit.**  
**If YES to any check → Keep local only.**

---

## 🛡️ ENFORCEMENT

### Automated Checks
- Pre-commit hooks (recommended) will scan for secrets
- GitHub secret scanning is enabled
- Any detected secrets will trigger immediate revocation

### Manual Review
- All pull requests must be reviewed for sensitive data
- Nathan (Human CEO) has final approval on all changes
- DieselGoose (AI Board Member) self-audits before pushing

### Incident Response
If sensitive data is accidentally committed:
1. Immediately revoke exposed credentials
2. Remove from Git history (force push or history rewrite)
3. Notify Nathan immediately
4. Document incident for security review

---

## 📋 CONTRIBUTING GUIDELINES

### For External Contributors
1. Fork the repository
2. Make changes in your fork
3. Submit Pull Request with clear description
4. Wait for review before merge
5. Never include credentials in PR descriptions

### For DieselGoose (AI)
1. Self-audit all files before commit
2. Use pre-commit checklist
3. When in doubt, keep local
4. Push only identity, logic, and templates
5. Never auto-commit files with `.secret`, `.env`, or `token` in name

---

## 🔄 BACKUP STRATEGY

### Current (Until Monday)
- Local Mac Mini M4: Primary storage (sensitive data)
- GitHub: Public repo only (safe data)
- No sensitive backup (temporary)

### Post-SSD Setup (Monday)
- Mac Mini M4: Primary operations
- Dual SSD: Encrypted backup of sensitive data
- GitHub: Public repo (safe data only)
- Cloud (optional): Encrypted vault for critical secrets

---

## 📞 SECURITY CONTACTS

**Report security issues immediately:**
- **Email:** nathan@greenhead.io
- **Telegram:** @DieselGoose (urgent only)

---

## 📜 AMENDMENTS

This policy may be updated as the business evolves. All changes must be:
1. Documented in this file
2. Communicated to all stakeholders
3. Reviewed for security implications

---

<p align="center">
  <b>Security First. Transparency Always. Secrets Never.</b><br>
  <i>Quack protocol active 🦆⚡️</i>
</p>
