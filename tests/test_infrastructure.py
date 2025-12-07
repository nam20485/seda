"""
Infrastructure smoke tests to verify test setup is working correctly.
"""

import pytest
from pathlib import Path


def test_fixtures_available(temp_dir, sample_project, bootstrap_script, packer_script):
    """Verify that all fixtures are available and working."""
    # Check temp_dir fixture
    assert temp_dir.exists()
    assert temp_dir.is_dir()
    
    # Check sample_project fixture
    assert sample_project['root'].exists()
    assert len(sample_project['files']) > 0
    
    # Check script fixtures
    assert bootstrap_script.exists()
    assert packer_script.exists()


def test_sample_project_structure(sample_project):
    """Verify sample project has expected structure."""
    root = sample_project['root']
    
    # Check expected files exist
    assert (root / "README.md").exists()
    assert (root / "main.py").exists()
    assert (root / "src" / "module.py").exists()
    
    # Check ignored directories exist (but will be filtered by scripts)
    assert (root / "__pycache__").exists()
    assert (root / ".git").exists()


def test_helper_functions_available():
    """Verify helper functions are importable."""
    import sys
    from pathlib import Path
    
    # Add tests directory to path to import conftest
    tests_dir = Path(__file__).parent
    sys.path.insert(0, str(tests_dir))
    
    import conftest
    
    assert callable(conftest.create_test_file)
    assert callable(conftest.run_script)
    assert callable(conftest.validate_seda_archive)
