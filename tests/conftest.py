"""
Pytest configuration for Sahayak AI.
Ensures root directory is always on sys.path for unit and integration tests.
"""
import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
