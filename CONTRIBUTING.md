# Contributing to Diesel-Goose

Thank you for your interest in contributing to Diesel-Goose. This document outlines the standards and practices for maintaining code quality and alignment with the project's mission.

---

## Branch Strategy

We use a simple Git workflow:

### Main Branches

- `main` – Production-ready code. Only tested, reviewed code merges here.
- `develop` – Integration branch for features before merging to main.

### Feature Branches

Name branches descriptively:

```bash
feature/memory-embedding
test/prompt-builder
fix/memory-duplication
docs/readme-update
```

### Workflow

```bash
# 1. Create feature branch
git checkout -b feature/your-feature-name

# 2. Make changes, commit often
git add .
git commit -m "Clear description of changes"

# 3. Push branch
git push origin feature/your-feature-name

# 4. Open Pull Request to develop branch
# 5. After review, merge to develop
# 6. Periodically merge develop to main
```

---

## Running Tests

All contributions must include tests and pass existing ones.

### Run All Tests

```bash
python3 -m pytest tests/ -v
```

### Run Specific Test

```bash
python3 -m pytest tests/test_memory.py -v
```

### Test Coverage

Aim for >80% coverage on new code:

```bash
python3 -m pytest --cov=. --cov-report=html
```

---

## Code Style Rules

We follow PEP 8 with these specific guidelines:

### Python

- **Line length**: 100 characters max
- **Indentation**: 4 spaces (no tabs)
- **Imports**: Grouped as stdlib, third-party, local
- **Docstrings**: Required for all public functions/classes
- **Type hints**: Encouraged for function signatures

Example:

```python
def add_memory(content: str, confidence: float, privacy: str = "private") -> Optional[Dict]:
    """
    Add a new memory to storage.
    
    Args:
        content: The memory content
        confidence: Confidence score (0.0-1.0)
        privacy: Privacy level (private, public, sensitive)
    
    Returns:
        Memory dict if added, None if rejected
    """
    # Implementation
```

### File Organization

```python
#!/usr/bin/env python3
"""
module_name.py – Short description

Longer description of module purpose.

Author: Diesel Goose – Founder / Chairman
Version: X.Y – Brief changelog note
"""

# Standard library imports
import os
import sys
from typing import Dict, List, Optional

# Third-party imports
import requests

# Local imports
from MEMORY.memory_engine import add_memory

# Constants
DEFAULT_TIMEOUT = 30

# Implementation
```

---

## DO NOT Commit

### Never Commit These Files

```bash
# Local memory (CRITICAL)
MEMORY/memory_store/
*.json
*.db
*.sqlite
*.sqlite3

# Secrets
.env
*.key
*.pem
secrets/

# Python cache
__pycache__/
*.pyc
.pytest_cache/

# OS files
.DS_Store
Thumbs.db
```

These are already in `.gitignore`. **Never** remove them or force-commit these files.

### Pre-Commit Checklist

Before every commit, verify:

- [ ] No `memory_store/` files staged
- [ ] No `.env` or secret files staged
- [ ] No `__pycache__` directories staged
- [ ] Tests pass: `python3 main.py --test`
- [ ] Code follows style guidelines
- [ ] Docstrings added for new functions

### Verification Command

```bash
# Check what's staged
git status

# Review staged changes
git diff --staged

# Ensure no sensitive files
git diff --staged --name-only | grep -E "(memory_store|\.env|\.key)" && echo "❌ REJECTED" || echo "✅ OK"
```

---

## Commit Message Format

Use clear, descriptive commit messages:

```
[type]: Brief description (50 chars or less)

Optional longer explanation (wrap at 72 chars).
Explain what changed and why, not how.

- Bullet points for multiple changes
- Reference issues: Fixes #123
```

### Types

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Adding or updating tests
- `refactor:` Code restructuring
- `perf:` Performance improvements
- `security:` Security-related changes

### Examples

```
feat: Add memory deduplication logic

Prevents identical memories from being stored twice.
Uses lowercase normalized string comparison.

fix: Handle Ollama connection timeout gracefully

docs: Update README with installation steps

test: Add unit tests for memory_filter.py
```

---

## Code Review Process

1. **Self-review** your code before submitting PR
2. **All tests must pass** in CI
3. **At least one approval** required from maintainers
4. **Address feedback** promptly and respectfully
5. **Keep PRs focused** – one feature/fix per PR

---

## Mission Alignment

All contributions should align with Diesel-Goose core principles:

✅ **Local-first** – Prefer local execution  
✅ **Privacy-protecting** – Never expose user data  
✅ **Faith-aligned** – Maintain integrity in all code  
✅ **Family-focused** – Efficiency over complexity  
✅ **Billion-scale** – Design for massive impact  

---

## Questions?

Open an issue for:
- Feature requests
- Bug reports
- Architecture discussions
- Security concerns

**Remember: Silence = trust. Execute with excellence.**

🦆 Quack protocol active.
