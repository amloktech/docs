"""Compatibility entry point for the current single-API validation suites.

Kept for existing local/CI callers. No archived API contract is read or restored.
These checks validate contracts and offline examples, not a deployed backend.
"""
from pathlib import Path
import runpy
import sys

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
for script in ['test-readiness-contract.py', 'test-product-api-review.py']:
    print(f"Running current contract suite: {script}", flush=True)
    runpy.run_path(str(SCRIPTS / script), run_name="__main__")
