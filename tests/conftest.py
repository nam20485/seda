"""
Shared test fixtures and utilities for SEDA testing.

This module provides reusable pytest fixtures and helper functions
for testing the SEDA bootstrap and packer scripts.
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
import pytest


@pytest.fixture
def temp_dir(tmp_path):
    """
    Pytest fixture that provides a temporary directory for tests.
    
    The directory is automatically cleaned up after the test completes.
    
    Args:
        tmp_path: Pytest's built-in tmp_path fixture
        
    Returns:
        Path: Path object pointing to the temporary directory
    """
    return tmp_path


@pytest.fixture
def sample_project(temp_dir):
    """
    Create a sample project structure with various file types.
    
    Creates a directory structure with:
    - Text files (Python, Markdown, JSON)
    - Binary files (simulated with encoded content)
    - Nested directories
    - Files that should be ignored
    
    Args:
        temp_dir: Temporary directory fixture
        
    Returns:
        dict: Dictionary with 'root' (Path to project root) and 'files' (list of created files)
    """
    project_root = temp_dir / "sample_project"
    project_root.mkdir()
    
    # Create text files
    (project_root / "README.md").write_text("# Sample Project\n\nThis is a test project.")
    (project_root / "main.py").write_text("#!/usr/bin/env python3\nprint('Hello, World!')\n")
    (project_root / "config.json").write_text('{"name": "test", "version": "1.0"}')
    
    # Create nested directory with files
    src_dir = project_root / "src"
    src_dir.mkdir()
    (src_dir / "module.py").write_text("def hello():\n    return 'Hello'\n")
    (src_dir / "data.txt").write_text("Sample data file\nWith multiple lines\n")
    
    # Create a subdirectory
    utils_dir = src_dir / "utils"
    utils_dir.mkdir()
    (utils_dir / "helper.py").write_text("def helper():\n    pass\n")
    
    # Create files that should be ignored
    pycache_dir = project_root / "__pycache__"
    pycache_dir.mkdir()
    (pycache_dir / "main.cpython-39.pyc").write_bytes(b"fake pyc content")
    
    # Create a .git directory (should be ignored)
    git_dir = project_root / ".git"
    git_dir.mkdir()
    (git_dir / "config").write_text("fake git config")
    
    created_files = [
        "README.md",
        "main.py",
        "config.json",
        "src/module.py",
        "src/data.txt",
        "src/utils/helper.py"
    ]
    
    return {
        'root': project_root,
        'files': created_files
    }


def create_test_file(directory, filename, content, binary=False):
    """
    Helper function to create a test file with specific content.
    
    Args:
        directory: Path or str - Directory where file should be created
        filename: str - Name of the file (can include subdirectories)
        content: str or bytes - Content to write to the file
        binary: bool - Whether to write in binary mode
        
    Returns:
        Path: Path to the created file
    """
    directory = Path(directory)
    file_path = directory / filename
    
    # Create parent directories if needed
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    if binary:
        file_path.write_bytes(content if isinstance(content, bytes) else content.encode())
    else:
        file_path.write_text(content if isinstance(content, str) else content.decode())
    
    return file_path


def run_script(script_path, args, cwd=None):
    """
    Execute a Python script and capture its output.
    
    Args:
        script_path: str or Path - Path to the Python script to run
        args: list - Command-line arguments to pass to the script
        cwd: str or Path - Working directory for script execution (optional)
        
    Returns:
        dict: Dictionary with 'returncode', 'stdout', 'stderr', and 'success' keys
    """
    script_path = Path(script_path)
    
    if not script_path.exists():
        raise FileNotFoundError(f"Script not found: {script_path}")
    
    cmd = [sys.executable, str(script_path)] + [str(arg) for arg in args]
    
    try:
        result = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return {
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'success': result.returncode == 0
        }
    except subprocess.TimeoutExpired:
        return {
            'returncode': -1,
            'stdout': '',
            'stderr': 'Script execution timed out',
            'success': False
        }
    except Exception as e:
        return {
            'returncode': -1,
            'stdout': '',
            'stderr': str(e),
            'success': False
        }


def validate_seda_archive(archive_path):
    """
    Validate that a SEDA archive is syntactically correct Python.
    
    Args:
        archive_path: str or Path - Path to the SEDA archive file
        
    Returns:
        dict: Dictionary with validation results including:
            - is_valid_python: bool
            - has_payload: bool
            - has_extractor: bool
            - error: str (if validation failed)
    """
    archive_path = Path(archive_path)
    
    if not archive_path.exists():
        return {
            'is_valid_python': False,
            'has_payload': False,
            'has_extractor': False,
            'error': 'File does not exist'
        }
    
    try:
        content = archive_path.read_text(encoding='utf-8')
        
        # Try to compile the file as Python
        compile(content, str(archive_path), 'exec')
        is_valid = True
        error = None
    except SyntaxError as e:
        is_valid = False
        error = f"Syntax error: {e}"
    except Exception as e:
        is_valid = False
        error = f"Compilation error: {e}"
    
    # Check for required components
    has_payload = 'PAYLOAD' in content or 'project_files' in content
    has_extractor = 'extract_payload' in content or 'def extract' in content
    
    return {
        'is_valid_python': is_valid,
        'has_payload': has_payload,
        'has_extractor': has_extractor,
        'error': error
    }


@pytest.fixture
def workspace_root():
    """
    Fixture that provides the path to the workspace root.
    
    Returns:
        Path: Path to the workspace root directory
    """
    # Assuming tests are in a 'tests' directory at the workspace root
    return Path(__file__).parent.parent


@pytest.fixture
def bootstrap_script(workspace_root):
    """
    Fixture that provides the path to seda_bootstrap.py.
    
    Returns:
        Path: Path to the bootstrap script
    """
    return workspace_root / "seda_bootstrap.py"


@pytest.fixture
def packer_script(workspace_root):
    """
    Fixture that provides the path to seda_packer.py.
    
    Returns:
        Path: Path to the packer script
    """
    return workspace_root / "seda_packer.py"
