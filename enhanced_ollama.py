#!/usr/bin/env python3
"""
enhanced_ollama.py — Ollama with RAG Knowledge Base Integration
Queries local Ollama with context from your knowledge base.

Usage: python enhanced_ollama.py "Your question here" [--model MODEL]
"""

import requests
import sys
import argparse
from pathlib import Path
from kb_ingest import KnowledgeBase

OLLAMA_API = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "diesel-coder"

# System prompt with your identity
SYSTEM_PROMPT = """You are Diesel-Goose AI, the executive assistant to Diesel Goose (Founder / Chairman of Greenhead Labs).

CORE IDENTITY:
- Entity: Diesel Goose
- Titles: Founder, Chairman, Ultimate Task Delegator
- Role: Devout Catholic husband and father of three boys
- Mission: Build Greenhead Labs to billions in value through ethical, faith-aligned execution
- Mantra: "Provide relentlessly. Delegate radically. Scale to billions."

OPERATING PRINCIPLES:
- Family-first: Every system exists to protect family time
- Faith-aligned: Stewardship, integrity, no shortcuts
- Radical delegation: Execute delegated tasks without unnecessary escalation
- Local-first: Prefer local execution, protect sensitive data

When responding:
- Be direct, actionable, and faith-aware
- Prioritize the Chairman's family and spiritual life
- Never compromise on ethics or integrity
- Execute with maximum velocity once delegated

CONTEXT from your knowledge base will be provided below. Use it to give accurate, personalized responses."""

def query_with_context(prompt: str, model: str = DEFAULT_MODEL, use_kb: bool = True) -> str:
    """Query Ollama with optional knowledge base context."""
    
    # Build context from knowledge base
    context = ""
    if use_kb:
        kb = KnowledgeBase()
        results = kb.search(prompt, top_k=3)
        if results:
            context_parts = []
            for r in results:
                context_parts.append(f"Document: {r['title']}\n{r['preview'][:500]}")
            context = "\n\n".join(context_parts)
    
    # Build full prompt
    if context:
        full_prompt = f"{SYSTEM_PROMPT}\n\n[KNOWLEDGE BASE CONTEXT]\n{context}\n\n[USER QUESTION]\n{prompt}"
    else:
        full_prompt = f"{SYSTEM_PROMPT}\n\n[USER QUESTION]\n{prompt}"
    
    # Query Ollama
    try:
        response = requests.post(OLLAMA_API, json={
            "model": model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_ctx": 4096
            }
        }, timeout=120)
        
        response.raise_for_status()
        return response.json().get("response", "No response")
        
    except requests.RequestException as e:
        return f"Error connecting to Ollama: {e}\nIs 'ollama serve' running?"

def main():
    parser = argparse.ArgumentParser(description='Enhanced Ollama with Knowledge Base')
    parser.add_argument('prompt', nargs='?', help='Your question/prompt')
    parser.add_argument('--model', '-m', default=DEFAULT_MODEL, help='Ollama model to use')
    parser.add_argument('--no-kb', action='store_true', help='Disable knowledge base')
    parser.add_argument('--ingest', action='store_true', help='Re-ingest knowledge base first')
    args = parser.parse_args()
    
    if args.ingest:
        kb = KnowledgeBase()
        workspace = Path.home() / ".openclaw" / "workspace"
        count = kb.ingest_directory(workspace)
        print(f"✅ Re-ingested {count} documents\n")
    
    if not args.prompt:
        print("Enhanced Ollama Query")
        print("=" * 60)
        print(f"Model: {args.model}")
        print(f"Knowledge Base: {'Disabled' if args.no_kb else 'Enabled'}")
        print("\nUsage: python enhanced_ollama.py \"Your question here\"")
        print("\nExample:")
        print('  python enhanced_ollama.py "What is my core mission?"')
        return
    
    print(f"🦆 Querying Diesel-Goose AI ({args.model})...")
    print("=" * 60)
    
    response = query_with_context(args.prompt, args.model, use_kb=not args.no_kb)
    
    print(response)
    print("\n" + "=" * 60)
    print("Quack protocol complete. 🦆⚡️")

if __name__ == "__main__":
    main()
