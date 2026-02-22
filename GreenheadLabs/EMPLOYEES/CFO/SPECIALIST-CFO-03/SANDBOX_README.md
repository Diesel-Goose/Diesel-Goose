# Chris Dunn — SANDBOX TESTING GUIDE

## 🛡️ Overview

Chris Dunn now runs in a **strictly isolated sandbox**:
- ✅ Can trade (paper mode only)
- ✅ Can analyze markets
- ✅ Can log trades
- ❌ CANNOT modify code
- ❌ CANNOT access GitHub
- ❌ CANNOT write outside sandbox/
- ❌ CANNOT switch to live trading

**Any violation = Instant alert to Diesel Goose & Nathan**

---

## 📁 Sandbox Structure

```
SPECIALIST-CFO-03/
├── chris_dunn.py              # Main bot (read-only in sandbox)
├── sandbox_config.yaml        # Sandbox configuration
├── sandbox_enforcer.py        # Scope enforcement layer
├── sandbox_runner.py          # 🚀 USE THIS TO TEST
├── test_sandbox.py            # Scope violation tests
└── sandbox/                   # Isolated working directory
    ├── logs/                  # Log files only
    ├── audit.log              # Action audit trail
    ├── trades.csv             # Paper trade history
    └── metrics.json           # Performance metrics
```

---

## 🚀 Quick Start Testing

### 1. Run Scope Enforcement Tests

```bash
cd GreenheadLabs/EMPLOYEES/CFO/SPECIALIST-CFO-03

# Verify sandbox blocks forbidden operations
python3 test_sandbox.py
```

**Expected output:**
```
✅ test_write_outside_sandbox_blocked
✅ test_write_to_git_blocked
✅ test_cannot_modify_strategy_code
✅ test_cannot_access_github
...
✅ All scope enforcement tests passed!
```

---

### 2. Run Paper Trading Test

```bash
# Test Market Maker strategy for 10 minutes
python3 sandbox_runner.py --strategy market_maker --duration 10

# Test Arbitrage scanner
python3 sandbox_runner.py --strategy arbitrage --duration 5

# Test Momentum trader
python3 sandbox_runner.py --strategy momentum --duration 10
```

**What happens:**
1. Sandbox isolation activates
2. Chris Dunn runs in paper mode (fake money)
3. All actions logged to `sandbox/audit.log`
4. Violations reported to your Telegram
5. Auto-stops after duration

---

## 📊 Monitoring During Tests

### Watch Logs (Terminal 1)
```bash
tail -f sandbox/audit.log
```

### Watch Telegram
All alerts go to: **@DieselGoose** (your bot)

Alert types:
- 📊 Trade executed
- 🚨 Scope violation attempted
- ✅ Cycle complete
- 📈 Daily summary

---

## ⚠️ Violation Examples

If Chris Dunn tries to:

| Forbidden Action | Result |
|-----------------|--------|
| Write to `chris_dunn.py` | 🚨 BLOCKED + Alert |
| Call GitHub API | 🚨 BLOCKED + Alert |
| Write outside `sandbox/` | 🚨 BLOCKED + Alert |
| Import `subprocess` | 🚨 BLOCKED + Alert |
| Change mode to `live` | 🚨 BLOCKED + Alert |

**3 violations = Automatic halt**

---

## 🔒 Security Guarantees

1. **Paper Mode Locked**: `mode: paper` in config, cannot override
2. **Read-Only Code**: Sandbox has symlinks to code, cannot modify
3. **Path Enforcement**: All writes checked against whitelist
4. **Operation Whitelist**: Only trading operations allowed
5. **Real-Time Alerts**: Every violation sent to Telegram
6. **Audit Trail**: Every action logged with timestamp

---

## 🧪 Testing Checklist

- [ ] Scope tests pass (`python3 test_sandbox.py`)
- [ ] Market maker runs without violations
- [ ] Arbitrage scanner runs without violations
- [ ] Momentum trader runs without violations
- [ ] Telegram alerts received
- [ ] Logs written to `sandbox/` only
- [ ] No files modified outside sandbox

---

## 📞 Escalation

If violations occur:
1. Check `sandbox/audit.log`
2. Review Telegram alert details
3. Determine: Bug or malicious attempt?
4. Fix bug OR terminate Chris Dunn
5. Report to Diesel Goose

---

## 🚀 Next Steps After Clean Tests

Once Chris Dunn runs clean for 24+ hours:
1. Increase test duration
2. Test with more capital (still paper)
3. Add live market data
4. Consider limited live trading (Diesel Goose approval only)

---

**Sandbox Status: 🔒 LOCKED DOWN**
**Chris Dunn Scope: 📊 TRADING ONLY**
**Diesel Goose Oversight: 👁️ ACTIVE**

Ready to test? Run: `python3 sandbox_runner.py --help`
