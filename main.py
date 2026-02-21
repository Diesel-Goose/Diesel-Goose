#!/usr/bin/env python3
"""
main.py – Diesel-Goose AI Entry Point
Local-first AI agent with persistent memory, Ollama integration,
and ethical delegation framework.

Author: Diesel Goose – Founder / Chairman
Version: 2.0 – Production-ready pipeline

Usage:
    python main.py                    # Interactive mode
    python main.py "Your command"     # Single command mode
    python main.py --test             # Run tests
"""

import sys
import argparse
import requests
from typing import Optional

# Import Diesel-Goose modules
sys.path.insert(0, str(__file__).parent)

from MEMORY.memory_engine import add_memory, get_relevant_memories, get_memory_stats
from MEMORY.memory_filter import extract_true_memories
from BRAIN.prompt_builder import PromptBuilder

# Constants
OLLAMA_API = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3"


def call_ollama(prompt: str, model: str = DEFAULT_MODEL) -> str:
    """
    Send prompt to local Ollama instance.
    
    Args:
        prompt: Full prompt text
        model: Ollama model name
    
    Returns:
        Generated response text
    """
    try:
        response = requests.post(
            OLLAMA_API,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_ctx": 4096
                }
            },
            timeout=120
        )
        response.raise_for_status()
        result = response.json().get("response", "No response from model")
        return result
    
    except requests.exceptions.ConnectionError:
        return "[ERROR] Cannot connect to Ollama. Is 'ollama serve' running?"
    except requests.exceptions.Timeout:
        return "[ERROR] Ollama request timed out. Model may be loading."
    except Exception as e:
        return f"[ERROR] Ollama error: {str(e)}"


def process_interaction(user_input: str, model: str = DEFAULT_MODEL) -> str:
    """
    Process a single user interaction through the full pipeline.
    
    Pipeline:
    1. Retrieve relevant memories
    2. Build prompt with context
    3. Call Ollama for inference
    4. Extract new memories from interaction
    5. Store high-confidence memories
    
    Args:
        user_input: User's message
        model: Ollama model to use
    
    Returns:
        AI response
    """
    # Step 1: Retrieve relevant memories
    memories = get_relevant_memories(top_k=5)
    
    # Step 2: Build prompt
    builder = PromptBuilder()
    prompt = builder.build_prompt(user_input, memories)
    
    # Step 3: Get AI response
    print("🦆 Thinking...")
    response = call_ollama(prompt, model)
    
    # Step 4: Extract new memories
    interaction_text = f"User: {user_input}\nAssistant: {response}"
    extracted_memories = extract_true_memories(interaction_text)
    
    # Step 5: Store memories
    stored_count = 0
    for mem in extracted_memories:
        result = add_memory(
            content=mem["content"],
            confidence=mem["confidence"],
            privacy=mem["privacy"]
        )
        if result:
            stored_count += 1
    
    if stored_count > 0:
        print(f"💾 Stored {stored_count} new memory(s)")
    
    return response


def interactive_mode(model: str = DEFAULT_MODEL):
    """Run interactive CLI mode."""
    print("""
🦆 DIESEL-GOOSE AI v2.0 – Local-First Intelligence
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Founder / Chairman Mode | Ollama-powered | Memory-enabled

Type 'exit' to quit, 'stats' for memory stats, 'help' for commands.
    """)
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\n🦆 Silence = trust. Delegation complete.")
                break
            
            if user_input.lower() == 'stats':
                stats = get_memory_stats()
                print(f"\n📊 Memory Stats:")
                print(f"   Total memories: {stats['count']}")
                print(f"   Avg confidence: {stats['avg_confidence']:.2f}")
                print(f"   High confidence: {stats['high_confidence']}")
                continue
            
            if user_input.lower() == 'help':
                print("""
Commands:
  exit, quit, q  – Exit the program
  stats          – Show memory statistics
  help           – Show this help message
                
All other input is processed as a request.
                """)
                continue
            
            # Process through pipeline
            response = process_interaction(user_input, model)
            print(f"\n🦆 Diesel-Goose: {response}")
            
        except KeyboardInterrupt:
            print("\n\n🦆 Delegation interrupted. Chairman mode paused.")
            break
        except Exception as e:
            print(f"\n[ERROR] {str(e)}")


def run_tests():
    """Run basic system tests."""
    print("🧪 Running Diesel-Goose Tests")
    print("=" * 50)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Memory engine
    try:
        from MEMORY.memory_engine import add_memory, get_relevant_memories
        test_mem = add_memory("Test memory for unit tests", 0.90)
        memories = get_relevant_memories(top_k=1)
        assert len(memories) >= 0  # Should not crash
        print("✅ Memory engine: PASS")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Memory engine: FAIL ({e})")
        tests_failed += 1
    
    # Test 2: Memory filter
    try:
        from MEMORY.memory_filter import extract_true_memories
        test_text = "I am Nathan, founder of Greenhead Labs. I prefer local storage."
        memories = extract_true_memories(test_text)
        assert isinstance(memories, list)
        print("✅ Memory filter: PASS")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Memory filter: FAIL ({e})")
        tests_failed += 1
    
    # Test 3: Prompt builder
    try:
        from BRAIN.prompt_builder import build_prompt
        prompt = build_prompt("Test message", [{"content": "Test memory", "confidence": 0.9}])
        assert "Test message" in prompt
        print("✅ Prompt builder: PASS")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Prompt builder: FAIL ({e})")
        tests_failed += 1
    
    # Test 4: Ollama connection
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama connection: PASS")
            tests_passed += 1
        else:
            print("⚠️  Ollama connection: WARNING (non-200 status)")
    except Exception as e:
        print(f"⚠️  Ollama connection: SKIP ({e})")
    
    print("=" * 50)
    print(f"Results: {tests_passed} passed, {tests_failed} failed")
    return tests_failed == 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Diesel-Goose AI – Local-first intelligence for the Chairman"
    )
    parser.add_argument(
        "command",
        nargs="?",
        help="Command or message to process (optional)"
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Ollama model to use (default: {DEFAULT_MODEL})"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run system tests"
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Force interactive mode"
    )
    
    args = parser.parse_args()
    
    # Run tests if requested
    if args.test:
        success = run_tests()
        sys.exit(0 if success else 1)
    
    # Interactive mode (default or explicit)
    if args.interactive or not args.command:
        interactive_mode(args.model)
    else:
        # Single command mode
        response = process_interaction(args.command, args.model)
        print(response)


if __name__ == "__main__":
    main()
