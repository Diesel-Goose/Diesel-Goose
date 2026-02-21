# 🦆 Diesel-Goose

**Local-first AI agent framework with persistent memory.**

Built for the Chairman. Designed for billion-scale execution. Faith-aligned, family-first, radically delegated.

---

## What Diesel-Goose Is

Diesel-Goose is a sovereign AI system that runs entirely on your local Mac Mini M4 (or any ARM64 machine). It combines:

- **Local LLM inference** via Ollama (no API costs, no data leakage)
- **Persistent memory** with confidence scoring and privacy controls
- **Structured prompting** with automatic context retrieval
- **Ethical delegation** framework aligned with founder principles

All data stays local. All memories are private. All execution is delegated.

---

## Architecture

```
User Input
    ↓
┌─────────────────────────────────────┐
│  BRAIN (prompt_builder.py)          │
│  • Retrieves relevant memories      │
│  • Constructs context-aware prompt  │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  Ollama (local LLM)                 │
│  • Inference on localhost:11434     │
│  • Zero external data transmission  │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  MEMORY (memory_filter.py)          │
│  • Extracts long-term memories      │
│  • Scores confidence (0.0-1.0)      │
│  • Filters for privacy level        │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  MEMORY (memory_engine.py)          │
│  • Stores in local JSON (gitignored)│
│  • Prevents duplicates              │
│  • Enforces confidence threshold    │
└─────────────────────────────────────┘
```

---

## Installation

### Prerequisites

- macOS (ARM64 optimized for M4)
- Homebrew
- Python 3.10+

### Step 1: Install Ollama

```bash
# Using Homebrew (recommended)
brew install ollama
brew services start ollama

# Or official installer
curl -fsSL https://ollama.com/install.sh | sh
```

### Step 2: Pull LLM Model

```bash
ollama pull llama3
```

### Step 3: Install Diesel-Goose

```bash
git clone https://github.com/Diesel-Goose/Diesel-Goose.git
cd Diesel-Goose

# Install Python dependencies
pip3 install requests --user --break-system-packages
```

---

## Running

### Interactive Mode (Recommended)

```bash
python3 main.py
```

Type commands naturally. The system will:
1. Retrieve relevant memories
2. Build context-aware prompt
3. Query local Ollama instance
4. Extract and store new memories

### Single Command

```bash
python3 main.py "What's my next priority?"
```

### Run Tests

```bash
python3 main.py --test
```

---

## Commands

| Command | Description |
|---------|-------------|
| `help` | Show available commands |
| `stats` | Display memory statistics |
| `exit` / `quit` / `q` | Exit the program |

---

## Project Structure

```
Diesel-Goose/
├── main.py                 # Entry point
├── README.md              # This file
├── CONTRIBUTING.md        # Contribution guidelines
├── .gitignore            # Protects local memory
│
├── BRAIN/                # Core intelligence
│   ├── prompt_builder.py # Prompt construction
│   ├── orchestrator.py   # Task orchestration
│   └── local_llm_agent.py # Ollama interface
│
├── MEMORY/               # Memory system
│   ├── memory_engine.py  # Storage engine
│   ├── memory_filter.py  # Extraction & scoring
│   └── memory_store/     # Local data (gitignored)
│
├── AGENTS/               # Agent implementations
│   ├── base_agent.py     # Agent base class
│   └── tests/            # Test suite
│
└── [Legacy files...]
```

---

## Security Note

**Memory is local-only and gitignored.**

Your conversation history, extracted memories, and personal data are:
- ✅ Stored only in `MEMORY/memory_store/` 
- ✅ Never committed to GitHub
- ✅ Never transmitted to external APIs
- ✅ Protected by `.gitignore` rules

The only external connection is to your local Ollama instance (`localhost:11434`).

---

## Founder Principles

This system embodies the Diesel-Goose operating philosophy:

1. **Radical Delegation** – Delegate once, execute completely
2. **Family First** – Systems exist to protect family time
3. **Faith-Aligned** – Stewardship, integrity, no shortcuts
4. **Local Sovereignty** – Own your data, own your intelligence
5. **Billions or Nothing** – Build for exponential scale

---

## Version

**v2.0** – Local-first architecture with structured memory

Built with ❤️ for the Chairman and his family.

🦆 **Quack protocol: Active.**
