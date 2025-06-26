"""
Entrypoint for running team builder from CLI or via PyInstaller.
Delegates to CLI handler.

See /docs/spec.md for full specification.
"""
from teambuilder.cli import main

if __name__ == "__main__":
    main()
