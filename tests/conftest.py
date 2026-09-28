"""
Pytest configuration for Sahayak AI.
Ensures root directory is always on sys.path for unit and integration tests.
"""
import sys
import os
import builtins
import typing

# Ensure typing constructs are available globally for dynamic modules
builtins.Union = typing.Union
builtins.Tuple = typing.Tuple
builtins.List = typing.List
builtins.Dict = typing.Dict
builtins.Optional = typing.Optional
builtins.Any = typing.Any

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
