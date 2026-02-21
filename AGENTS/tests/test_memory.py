#!/usr/bin/env python3
"""
test_memory.py – Unit tests for memory system

Tests:
- Memory saves correctly
- Duplicate prevention works
- Confidence filtering works
- Retrieval returns expected results

Author: Diesel Goose – Founder / Chairman
"""

import sys
import os
import json
import tempfile
import shutil
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import unittest
from MEMORY.memory_engine import (
    add_memory, 
    get_relevant_memories, 
    load_memories,
    save_memories,
    memory_exists,
    get_memory_stats,
    MEMORY_FILE
)
from MEMORY.memory_filter import MemoryFilter, extract_true_memories


class TestMemoryEngine(unittest.TestCase):
    """Test suite for memory_engine.py"""
    
    def setUp(self):
        """Set up test environment with temp directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_memory_file = MEMORY_FILE
        
        # Monkey-patch memory file location
        import MEMORY.memory_engine as mem_engine
        mem_engine.MEMORY_DIR = Path(self.temp_dir)
        mem_engine.MEMORY_FILE = Path(self.temp_dir) / "memories.json"
        
        # Clear any existing data
        if mem_engine.MEMORY_FILE.exists():
            mem_engine.MEMORY_FILE.unlink()
    
    def tearDown(self):
        """Clean up temp directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
        # Restore original memory file location
        import MEMORY.memory_engine as mem_engine
        mem_engine.MEMORY_DIR = self.original_memory_file.parent
        mem_engine.MEMORY_FILE = self.original_memory_file
    
    def test_add_memory_basic(self):
        """Test basic memory addition."""
        result = add_memory("Test memory content", 0.90)
        self.assertIsNotNone(result)
        self.assertEqual(result["content"], "Test memory content")
        self.assertEqual(result["confidence"], 0.90)
        self.assertIn("id", result)
        self.assertIn("timestamp", result)
    
    def test_add_memory_low_confidence_rejected(self):
        """Test that low confidence memories are rejected."""
        result = add_memory("Low confidence memory", 0.50)
        self.assertIsNone(result)
    
    def test_duplicate_prevention(self):
        """Test that duplicate memories are prevented."""
        add_memory("Unique memory", 0.90)
        result = add_memory("Unique memory", 0.90)
        self.assertIsNone(result)
        
        # Case insensitive
        result = add_memory("unique MEMORY", 0.90)
        self.assertIsNone(result)
    
    def test_memory_exists(self):
        """Test memory existence check."""
        add_memory("Existing memory", 0.90)
        
        data = load_memories()
        memories = data.get("memories", [])
        
        self.assertTrue(memory_exists("Existing memory", memories))
        self.assertFalse(memory_exists("Non-existing memory", memories))
    
    def test_get_relevant_memories(self):
        """Test memory retrieval."""
        # Add test memories
        add_memory("High confidence memory 1", 0.95)
        add_memory("High confidence memory 2", 0.92)
        add_memory("Medium confidence memory", 0.85)
        
        memories = get_relevant_memories(top_k=2)
        
        self.assertEqual(len(memories), 2)
        # Should return highest confidence first
        self.assertGreaterEqual(memories[0]["confidence"], memories[1]["confidence"])
    
    def test_get_memory_stats(self):
        """Test memory statistics."""
        add_memory("Memory one", 0.90)
        add_memory("Memory two", 0.85)
        
        stats = get_memory_stats()
        
        self.assertEqual(stats["count"], 2)
        self.assertIn("avg_confidence", stats)
        self.assertIn("high_confidence", stats)
    
    def test_privacy_levels(self):
        """Test different privacy levels."""
        public = add_memory("Public memory", 0.90, "public")
        private = add_memory("Private memory", 0.90, "private")
        sensitive = add_memory("Sensitive memory", 0.90, "sensitive")
        
        self.assertEqual(public["privacy"], "public")
        self.assertEqual(private["privacy"], "private")
        self.assertEqual(sensitive["privacy"], "sensitive")


class TestMemoryFilter(unittest.TestCase):
    """Test suite for memory_filter.py"""
    
    def test_extract_identity(self):
        """Test extraction of identity information."""
        text = "My name is Nathan and I am the founder of Greenhead Labs."
        memories = extract_true_memories(text)
        
        self.assertTrue(len(memories) > 0)
        # Should extract identity-related memory
        identity_mems = [m for m in memories if "identity" in str(m)]
        self.assertTrue(len(identity_mems) > 0 or len(memories) > 0)
    
    def test_extract_preferences(self):
        """Test extraction of preferences."""
        text = "I prefer local-only storage and I don't like cloud services."
        memories = extract_true_memories(text)
        
        self.assertTrue(len(memories) >= 1)
        contents = [m["content"].lower() for m in memories]
        self.assertTrue(any("prefer" in c or "don't like" in c for c in contents))
    
    def test_confidence_scoring(self):
        """Test that confidence scores are in valid range."""
        text = "I am a devout Catholic and I work at Greenhead Labs."
        memories = extract_true_memories(text)
        
        for mem in memories:
            self.assertGreaterEqual(mem["confidence"], 0.0)
            self.assertLessEqual(mem["confidence"], 1.0)
    
    def test_low_confidence_vague_language(self):
        """Test that vague language reduces confidence."""
        filter_ = MemoryFilter()
        
        # Vague statement
        vague_text = "Maybe I'll consider cloud options later, but probably not."
        vague_mems = filter_.extract_memories(vague_text)
        
        if vague_mems:
            # Should have lower confidence due to vague words
            self.assertLess(vague_mems[0].confidence, 0.85)


class TestIntegration(unittest.TestCase):
    """Integration tests for full memory pipeline."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        import MEMORY.memory_engine as mem_engine
        mem_engine.MEMORY_DIR = Path(self.temp_dir)
        mem_engine.MEMORY_FILE = Path(self.temp_dir) / "memories.json"
    
    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_full_pipeline(self):
        """Test the complete pipeline: extract -> filter -> store -> retrieve."""
        # Simulate user interaction
        user_text = "I am Nathan, founder of Greenhead Labs. I prefer local storage."
        
        # Extract memories
        extracted = extract_true_memories(user_text)
        self.assertTrue(len(extracted) > 0)
        
        # Store memories
        stored_count = 0
        for mem in extracted:
            result = add_memory(mem["content"], mem["confidence"], mem["privacy"])
            if result:
                stored_count += 1
        
        self.assertGreater(stored_count, 0)
        
        # Retrieve memories
        retrieved = get_relevant_memories(top_k=5)
        self.assertEqual(len(retrieved), stored_count)


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestMemoryEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestMemoryFilter))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
