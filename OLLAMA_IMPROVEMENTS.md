# Ollama Enhancement Plan — Greenhead Labs

**Current State:**
- Model: llama3:latest (8B params, Q4_0 quantized, 4.7GB)
- Hardware: Mac Mini M4 (ARM64)
- API: Running on localhost:11434
- Memory: Basic JSON store (no embeddings)

---

## 🎯 Recommended Improvements

### 1. **Model Optimization** (Immediate — High Impact)

**Current:** llama3 8B Q4_0 — Good but not optimal for M4

**Better Options:**
| Model | Size | Best For | Speed |
|-------|------|----------|-------|
| `llama3.2` | 3B | Fast inference, simple tasks | ⚡️ Fastest |
| `llama3.1:8b` | 8B | Better reasoning than llama3 | ⚡️ Fast |
| `qwen2.5:7b` | 7B | Coding, reasoning | ⚡️ Fast |
| `mistral-nemo:12b` | 12B | Complex analysis | 🔄 Slower |
| `llama3.2-vision` | 11B | Image + text | 🔄 Slower |

**Recommendation:** Deploy `llama3.2:3b` for fast tasks + `llama3.1:8b` for deep reasoning

```bash
ollama pull llama3.2:3b
ollama pull llama3.1:8b
```

---

### 2. **RAG Knowledge Base** (High Impact)

**Problem:** Ollama has no context of your 39+ markdown files

**Solution:** Build embeddings index of all KB docs

**Implementation:**
```python
# Ingest all .md files into ChromaDB
# Query with context from your documents
```

**Benefits:**
- Ollama knows your SOUL.md, IDENTITY.md, HEARTBEAT history
- Can answer: "What did I work on last week?"
- Can answer: "What's my core mission?"

---

### 3. **Memory-Enhanced Prompts** (Medium Impact)

**Current:** prompt_builder.py has basic memory injection

**Enhancement:** Semantic memory retrieval before Ollama calls

```python
# Before querying Ollama:
1. Get relevant memories from ChromaDB
2. Get recent HEARTBEAT entries
3. Inject into system prompt
4. Query Ollama with full context
```

---

### 4. **Specialized Agents** (Medium Impact)

Create purpose-tuned models via Modelfile:

```dockerfile
# Diesel-Coder.modelfile
FROM llama3.2:3b
SYSTEM """You are Diesel-Coder, specialized in:
- Python, Rust, Bash
- XRPL/Web3 development
- Clean, faith-aligned code
Always provide working code examples."""
```

```bash
ollama create diesel-coder -f Diesel-Coder.modelfile
```

**Agents to create:**
- `diesel-coder` — Code generation/review
- `diesel-strategist` — Business analysis
- `diesel-security` — Security audit focus

---

### 5. **Performance Optimization** (Immediate)

**For M4 Mac:**
```bash
# Use Metal GPU acceleration
export OLLAMA_GPU_OVERHEAD=0.1

# Keep models in memory
ollama run llama3.2:3b --keepalive 30m
```

**Create launch script:**
```bash
#!/bin/bash
# ollama_optimal.sh
export OLLAMA_NUM_PARALLEL=4
export OLLAMA_MAX_LOADED_MODELS=2
export OLLAMA_GPU_OVERHEAD=0.1
ollama serve
```

---

### 6. **Integration Hooks** (Medium Impact)

**Enhance local_llm_agent.py:**
- Retry logic with exponential backoff
- Streaming responses for long outputs
- Automatic fallback to cloud API if local fails
- Cost tracking (local = $0, but track tokens)

---

## 📊 Implementation Priority

| Priority | Task | Effort | Impact |
|----------|------|--------|--------|
| P0 | Pull llama3.2:3b + llama3.1:8b | 5 min | High |
| P0 | GPU acceleration config | 10 min | High |
| P1 | RAG knowledge base | 2 hrs | Very High |
| P1 | Memory-enhanced prompts | 1 hr | High |
| P2 | Specialized agents | 30 min | Medium |
| P2 | Integration hooks | 1 hr | Medium |

---

## 🚀 Quick Wins (Do Now)

```bash
# 1. Pull optimized models
ollama pull llama3.2:3b
ollama pull llama3.1:8b

# 2. Test speed comparison
ollama run llama3.2:3b "Explain quantum computing"
ollama run llama3.1:8b "Explain quantum computing"

# 3. Create custom agent
cat > ~/.ollama/Diesel-Coder.modelfile << 'EOF'
FROM llama3.2:3b
SYSTEM """You are Diesel-Coder, the coding assistant for Greenhead Labs.
You write clean, efficient, faith-aligned code.
Always include error handling and comments."""
EOF
ollama create diesel-coder -f ~/.ollama/Diesel-Coder.modelfile
```

---

## 💡 Chairman's Choice

**Option A: Quick Upgrade (15 min)**
- Pull better models
- GPU optimization
- Immediate speed boost

**Option B: Full RAG (2-3 hrs)**
- Knowledge base with all your docs
- Semantic memory search
- Ollama knows your entire history

**Option C: Both**
- Start with Quick Upgrade
- Build RAG in background

Which path, Chairman? 🦆
