🦆 DIESELGOOSE — GREENHEAD LABS | Chairman
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 [DATE] • 🕐 [TIME CST]

⚡ SYSTEM PULSE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Health      [█████████████░░] 91% 🟢
Budget      [█████░░░░░░░░░░] 60% 🟡  
Motivation  [██████████░░░░░] 62% 🔥
Productivity[████████████░░░] 80% ⚡
Mission     [█████████░░░░░░] 55% 🎯

💭 HOW I'M FEELING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💪 Million $ in revenue a month is a must.

🎯 DAILY CHECK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 Officers and directors are productive, Revenue is up.

💬 THOUGHTS:
[Dynamic reflection here]

🦆⚡ v1.5.89.321


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CODING GUIDE: Dynamic Progress Bars
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## How The Bars Work (15-Block Design)

Each bar = 17 characters total:
[█████████████░░] = 15 blocks inside + 2 brackets

Math:
- Each █ or ░ = ~6.67% (100% ÷ 15 blocks)
- Formula: filled = round(percentage / 6.67)
- Empty = 15 - filled

## Real-Time Percentage to Bar Mapping

| % | Bar | Calculation |
|---|-----|-------------|
| 100% | [███████████████] | 15 █ |
| 95% | [██████████████░] | 14 █ + 1 ░ |
| 91% | [█████████████░░] | 13 █ + 2 ░ |
| 80% | [████████████░░░] | 12 █ + 3 ░ |
| 62% | [██████████░░░░░] | 9 █ + 6 ░ |
| 60% | [█████████░░░░░░] | 9 █ + 6 ░ |
| 55% | [████████░░░░░░░] | 8 █ + 7 ░ |
| 50% | [███████░░░░░░░░] | 7 █ + 8 ░ |
| 25% | [████░░░░░░░░░░░] | 4 █ + 11 ░ |
| 10% | [█░░░░░░░░░░░░░░] | 1 █ + 14 ░ |
| 0% | [░░░░░░░░░░░░░░░] | 0 █ + 15 ░ |

## Dynamic Bar Generation (Python)

```python
def generate_bar(percentage):
    filled = round(percentage / 6.67)
    empty = 15 - filled
    return "█" * filled + "░" * empty

# Real-time examples:
health_pct = 91  # From actual system health
health_bar = generate_bar(health_pct)  # [█████████████░░]
print(f"Health      [{health_bar}] {health_pct}% 🟢")

budget_pct = 60  # From API spend tracking
budget_bar = generate_bar(budget_pct)  # [█████████░░░░░░]
print(f"Budget      [{budget_bar}] {budget_pct}% 🟡")

motivation_pct = 62  # From task completion
motivation_bar = generate_bar(motivation_pct)  # [██████████░░░░░]
print(f"Motivation  [{motivation_bar}] {motivation_pct}% 🔥")
```

## What Each Metric Tracks

**Health (System Health):**
- API response time < 500ms = High health
- Error rate < 1% = Good health
- Context usage < 80% = Healthy
- Source: `session_status` checks

**Budget (API Spend):**
- $0-2.50 spent = 0-50% (LEAN 🟢)
- $2.51-3.75 spent = 51-75% (EFFICIENT 🟢)
- $3.76-4.75 spent = 76-95% (HIGH 🟡)
- $4.76-5.00 spent = 96-100% (CRITICAL 🔴)
- Source: Daily token usage tracking

**Motivation (Task Completion):**
- 90-100% tasks done = 🔥 PEAK
- 70-89% tasks done = ⚡ HIGH
- 40-69% tasks done = 💤 MODERATE
- 0-39% tasks done = 😴 LOW
- Source: Daily goal tracking

**Productivity (Output Rate):**
- Messages/hour > 10 = 100% ⚡
- Code commits/day > 5 = 100% ⚡
- Files modified/hour = Rate tracking

**Mission (Revenue Alignment):**
- Revenue vs target % = Mission score
- $ goals hit = 100% 🎯
- Behind on revenue = Lower %

## Auto-Update Flow

1. **Collect Metrics** (every heartbeat):
   - Query system status
   - Check API spend
   - Count tasks completed
   - Calculate revenue progress

2. **Calculate Percentages**:
   - Health = (system_uptime / total_time) * 100
   - Budget = (spent / 5.00) * 100
   - Motivation = (tasks_done / tasks_planned) * 100

3. **Generate Bars**:
   - Use generate_bar() function
   - Round to nearest block

4. **Pick Status Emoji**:
   - Based on percentage ranges above

5. **Update Message**:
   - Insert new bars
   - Update timestamp
   - Refresh feelings

6. **Sync to GitHub**:
   - Push updated HEARTBEAT.md
   - Commit: "Heartbeat [TIME] - [STATUS]"

## Example State Changes

**Morning Start:**
Health [███████████████] 100% 🟢
Budget [░░░░░░░░░░░░░░░] 0% 🟢
→ Fresh day, ready to execute

**Mid-Day Grinding:**
Health [█████████████░░] 91% 🟢
Budget [█████░░░░░░░░░░] 60% 🟡
→ Systems hot, budget burning

**Evening Wind Down:**
Health [████████████░░░] 80% 🟢
Budget [████████████░░░] 80% 🟡
→ Productive day, near limit

**Critical State:**
Health [███░░░░░░░░░░░░] 20% 🔴
Budget [███████████████] 100% 🔴
→ System issues, budget blown

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DO NOT SEND BELOW THIS LINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# DieselGoose – Heartbeat & Health Monitor

**Repository:** https://github.com/Diesel-Goose/Diesel-Goose
**Role:** Chairman @ Greenhead Labs
**Frequency:** Every 5-10 minutes

## Auto-Sync
Every heartbeat pushes to GitHub with updated bars based on real metrics.

## Contact
nathan@greenhead.io
