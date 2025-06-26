"""
Entrypoint for running team builder from CLI or via PyInstaller.
Delegates to CLI handler.

See /docs/spec.md for full specification.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from teambuilder.cli import main

if __name__ == "__main__":
    main()
