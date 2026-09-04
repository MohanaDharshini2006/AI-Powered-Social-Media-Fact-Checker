#!/usr/bin/env python
import sys
print("Python version:", sys.version)
print("Loading dependencies...")

try:
    import torch
    print("✓ PyTorch loaded")
except Exception as e:
    print("✗ PyTorch error:", e)
    sys.exit(1)

try:
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    print("✓ Transformers loaded")
except Exception as e:
    print("✗ Transformers error:", e)
    sys.exit(1)

try:
    import fastapi
    print("✓ FastAPI loaded")
except Exception as e:
    print("✗ FastAPI error:", e)
    sys.exit(1)

print("\nAll dependencies OK. Starting backend...")
exec(open('backend.py').read())
