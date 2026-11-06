#!/usr/bin/env python3
"""
Main entry point for running the PNA client application in a development environment.
Automatically detects and uses the local virtual environment (.venv) if present.

Usage:
    python3 run.py
"""
import sys
import os
import subprocess

if __name__ == "__main__":
    client_dir = os.path.dirname(os.path.abspath(__file__))
    client_main = os.path.join(client_dir, "main.py")
    
    # Select Python interpreter (use client .venv if available)
    python_bin = sys.executable
    venv_python = os.path.join(client_dir, ".venv", "bin", "python")
    if os.path.exists(venv_python):
        python_bin = venv_python
    elif os.name == "nt":
        venv_python_win = os.path.join(client_dir, ".venv", "Scripts", "python.exe")
        if os.path.exists(venv_python_win):
            python_bin = venv_python_win

    sys.exit(subprocess.call([python_bin, client_main] + sys.argv[1:], cwd=client_dir))
