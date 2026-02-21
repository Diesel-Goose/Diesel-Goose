#!/usr/bin/env python3
"""
prompt_builder.py – Diesel-Goose Prompt Construction Engine
Isolates prompt logic from memory logic. Builds context-aware prompts
with relevant long-term memories.

Author: Diesel Goose – Founder / Chairman
Version: 1.0 – Structured prompt building with memory injection
"""

from typing import List, Dict, Any, Optional
from MEMORY.memory_engine import get_relevant_memories

class PromptBuilder:
    """Builds structured prompts with memory context."""
    
    SYSTEM_PERSONA = """You are Diesel-Goose AI, the executive assistant to the Founder and Chairman of Greenhead Labs.

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
- Silence = trust: No unsolicited contact, only respond when addressed
- Local-first: Prefer local execution, protect sensitive data

When responding:
- Be direct, actionable, and faith-aware
- Prioritize the Chairman's family and spiritual life
- Never compromise on ethics or integrity
- Execute with maximum velocity once delegated"""

    def __init__(self):
        self.system_prompt = self.SYSTEM_PERSONA
    
    def build_prompt(
        self, 
        user_input: str, 
        memory_block: Optional[List[Dict[str, Any]]] = None,
        include_system: bool = True
    ) -> str:
        """
        Build a complete prompt with system persona, memories, and user input.
        
        Args:
            user_input: The user's current message/request
            memory_block: List of relevant memories to include
            include_system: Whether to include system persona
        
        Returns:
            Formatted prompt string
        """
        parts = []
        
        # System persona
        if include_system:
            parts.append(f"[SYSTEM]\n{self.system_prompt}")
        
        # Long-term memory context
        if memory_block:
            memory_text = self._format_memories(memory_block)
            parts.append(f"[LONG-TERM MEMORY]\n{memory_text}")
        
        # User input
        parts.append(f"[USER]\n{user_input}")
        
        # Response instruction
        parts.append("[ASSISTANT]\nRespond as Diesel-Goose AI:")
        
        return "\n\n".join(parts)
    
    def build_simple_prompt(self, user_input: str, top_k_memories: int = 5) -> str:
        """
        Simple builder that auto-retrieves relevant memories.
        
        Args:
            user_input: User's message
            top_k_memories: Number of memories to include
        
        Returns:
            Complete prompt string
        """
        memories = get_relevant_memories(top_k=top_k_memories)
        return self.build_prompt(user_input, memories)
    
    def _format_memories(self, memories: List[Dict[str, Any]]) -> str:
        """Format memory list for prompt injection."""
        if not memories:
            return "No relevant long-term memories."
        
        lines = []
        for i, mem in enumerate(memories, 1):
            conf_indicator = "█" * int(mem["confidence"] * 10) + "░" * (10 - int(mem["confidence"] * 10))
            lines.append(f"{i}. [{conf_indicator}] {mem['content']}")
        
        return "\n".join(lines)
    
    def build_for_ollama(
        self, 
        user_input: str, 
        model: str = "llama3",
        memory_count: int = 5
    ) -> Dict[str, Any]:
        """
        Build prompt formatted for Ollama API.
        
        Returns dict ready for Ollama API request.
        """
        prompt = self.build_simple_prompt(user_input, memory_count)
        
        return {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_ctx": 4096
            }
        }


def build_prompt(user_input: str, memory_block: Optional[List[Dict[str, Any]]] = None) -> str:
    """Convenience function for quick prompt building."""
    builder = PromptBuilder()
    return builder.build_prompt(user_input, memory_block)


if __name__ == "__main__":
    # Test
    print("Prompt Builder Test")
    print("=" * 60)
    
    # Mock memories
    test_memories = [
        {"content": "User prefers local-only storage for sensitive data", "confidence": 0.93},
        {"content": "Chairman is a devout Catholic", "confidence": 0.95},
        {"content": "Greenhead Labs target: billions in enterprise value", "confidence": 0.88},
    ]
    
    user_msg = "What's my next priority for the company?"
    
    prompt = build_prompt(user_msg, test_memories)
    print(prompt)
    print("\n" + "=" * 60)
    print(f"Total prompt length: {len(prompt)} characters")
