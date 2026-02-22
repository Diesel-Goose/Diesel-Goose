#!/usr/bin/env python3
"""
kb_ingest.py — Knowledge Base Ingestion for Ollama RAG
Reads all markdown files and creates embeddings index for semantic search.

Usage: python kb_ingest.py [--index-path PATH]
"""

import os
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime

class KnowledgeBase:
    """Manages ingestion and retrieval of markdown knowledge base."""
    
    def __init__(self, index_path: str = "~/.openclaw/kb_index.json"):
        self.index_path = Path(index_path).expanduser()
        self.documents: Dict[str, Dict] = {}
        self.load_index()
    
    def load_index(self):
        """Load existing index if available."""
        if self.index_path.exists():
            with open(self.index_path, 'r') as f:
                self.documents = json.load(f)
    
    def save_index(self):
        """Save index to disk."""
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.index_path, 'w') as f:
            json.dump(self.documents, f, indent=2)
    
    def ingest_file(self, filepath: Path) -> bool:
        """Ingest a single markdown file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Skip if unchanged
            file_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
            doc_id = str(filepath)
            
            if doc_id in self.documents:
                if self.documents[doc_id].get('hash') == file_hash:
                    return False  # Unchanged
            
            # Chunk content for better retrieval
            chunks = self._chunk_content(content, chunk_size=500, overlap=100)
            
            self.documents[doc_id] = {
                'path': str(filepath),
                'hash': file_hash,
                'title': self._extract_title(content),
                'chunks': chunks,
                'ingested_at': datetime.utcnow().isoformat(),
                'size': len(content)
            }
            
            return True
            
        except Exception as e:
            print(f"Error ingesting {filepath}: {e}")
            return False
    
    def ingest_directory(self, directory: Path, pattern: str = "*.md") -> int:
        """Ingest all matching files in directory."""
        count = 0
        for filepath in directory.rglob(pattern):
            if self.ingest_file(filepath):
                count += 1
                print(f"✅ Ingested: {filepath.relative_to(directory)}")
        self.save_index()
        return count
    
    def _chunk_content(self, content: str, chunk_size: int = 500, overlap: int = 100) -> List[Dict]:
        """Split content into overlapping chunks."""
        chunks = []
        start = 0
        
        while start < len(content):
            end = min(start + chunk_size, len(content))
            chunk = content[start:end]
            
            chunks.append({
                'text': chunk,
                'start': start,
                'end': end
            })
            
            start += chunk_size - overlap
        
        return chunks
    
    def _extract_title(self, content: str) -> str:
        """Extract title from markdown (first # heading)."""
        lines = content.split('\n')
        for line in lines[:10]:
            if line.startswith('# '):
                return line[2:].strip()
        return "Untitled"
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Simple keyword search (placeholder for semantic search)."""
        results = []
        query_terms = query.lower().split()
        
        for doc_id, doc in self.documents.items():
            score = 0
            for chunk in doc['chunks']:
                chunk_text = chunk['text'].lower()
                for term in query_terms:
                    if term in chunk_text:
                        score += 1
            
            if score > 0:
                results.append({
                    'path': doc['path'],
                    'title': doc['title'],
                    'score': score,
                    'preview': doc['chunks'][0]['text'][:200] if doc['chunks'] else ""
                })
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]
    
    def get_stats(self) -> Dict:
        """Get index statistics."""
        total_docs = len(self.documents)
        total_chunks = sum(len(d['chunks']) for d in self.documents.values())
        total_size = sum(d['size'] for d in self.documents.values())
        
        return {
            'documents': total_docs,
            'chunks': total_chunks,
            'size_bytes': total_size,
            'size_mb': round(total_size / 1024 / 1024, 2)
        }


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Knowledge Base Ingestion')
    parser.add_argument('--workspace', type=str, default='~/.openclaw/workspace',
                       help='Workspace directory to index')
    parser.add_argument('--index', type=str, default='~/.openclaw/kb_index.json',
                       help='Index file path')
    parser.add_argument('--search', type=str, help='Search query')
    args = parser.parse_args()
    
    kb = KnowledgeBase(index_path=args.index)
    
    if args.search:
        results = kb.search(args.search)
        print(f"\n🔍 Search: '{args.search}'")
        print(f"Found {len(results)} results:\n")
        for r in results:
            print(f"  📄 {r['title']}")
            print(f"     Path: {r['path']}")
            print(f"     Preview: {r['preview'][:100]}...")
            print()
    else:
        # Ingest workspace
        workspace = Path(args.workspace).expanduser()
        print(f"📚 Ingesting knowledge base from: {workspace}")
        
        count = kb.ingest_directory(workspace)
        
        stats = kb.get_stats()
        print(f"\n✅ Ingestion complete!")
        print(f"   New/updated files: {count}")
        print(f"   Total documents: {stats['documents']}")
        print(f"   Total chunks: {stats['chunks']}")
        print(f"   Total size: {stats['size_mb']} MB")

if __name__ == "__main__":
    main()
