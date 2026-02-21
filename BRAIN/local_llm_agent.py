#!/usr/bin/env python3
"""
local_llm_agent.py – Greenhead Labs Agent Brain Tie-In
Queries local Ollama on Mac Mini M4 for inference (e.g., ethical veto, task delegation).
Million-dollar: Error-safe, async-friendly, heartbeat-logged.
Usage: python local_llm_agent.py "Prompt here" --model llama3
"""

import requests
import sys
import datetime
import argparse

HEARTBEAT_PATH = "../HEARTBEAT.md"  # Relative to Brain/
OLLAMA_API = "http://localhost:11434/api/generate"

def log_heartbeat(message: str):
    ts = datetime.datetime.utcnow().isoformat() + "Z"
    entry = f"[HEARTBEAT {ts}] | Local LLM: {message} | MAXIMUM EXECUTION\n"
    with open(HEARTBEAT_PATH, "a", encoding="utf-8") as f:
        f.write(entry)

def query_ollama(prompt: str, model: str = "llama3") -> str:
    try:
        response = requests.post(OLLAMA_API, json={
            "model": model,
            "prompt": prompt,
            "stream": False
        })
        response.raise_for_status()
        result = response.json().get("response", "No response")
        log_heartbeat(f"Inference complete: {result[:50]}...")
        return result
    except requests.RequestException as e:
        log_heartbeat(f"Error: {str(e)}")
        return f"Error: {str(e)}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Local LLM Agent Inference")
    parser.add_argument("prompt", type=str, help="Inference prompt")
    parser.add_argument("--model", type=str, default="llama3", help="Ollama model")
    args = parser.parse_args()

    result = query_ollama(args.prompt, args.model)
    print(result)
