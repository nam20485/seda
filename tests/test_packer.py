"""
Unit tests for seda_packer.py

Tests cover:
- Type 0 (standard) SEDA archive creation
- Type 5 (commit) SEDA archive creation with docstrings
- commit_msg.txt extraction from Type 5 archives
- Custom ignore directories via CLI arguments
- Custom ignore extensions via CLI arguments
- --recursive-pack-seda flag behavior
- --docstring-file argument
- Error handling
"""

import pytest
from pathlib import Path
import sys
import os

# Import helper functions from conftest
sys.path.insert(0, str(Path(__file__).parent))
import conftest


class TestPackerType0Archives:
    """Tests for Type 0 (standard) SEDA archive creation."""
    
    def test_create_type0_archive(self, temp_dir, sample_project, packer_script):
        """Test basic Type 0 archive creation."""
        output_file = temp_dir / "test.seda"
        
        result = conftest.run_script(
            packer_script,
            [str(sample_project['root']), str(output_file)]
        )
        
        assert result['success'], f"Script failed: {result['stderr']}"
        assert output_file.exists(), "Archive file was not created"
        assert "SEDA archive created" in result['stdout']
    
    def test_type0_archive_is_valid_python(self, temp_dir, sample_project, packer_script):
        """Test that generated Type 0 archive is syntactically valid Python."""
        output_file = temp_dir / "test.seda"
        
        conftest.run_script(
            packer_script,
            [str(sample_project['root']), str(output_file)]
        )
        
        validation = conftest.validate_seda_archive(output_file)
        assert validation['is_valid_python'], f"Archive is not valid Python: {validation.get('error')}"
        assert validation['has_payload'], "Archive missing payload"
        assert validation['has_extractor'], "Archive missing extractor logic"
    
    def test_type0_default_extension(self, temp_dir, sample_project, packer_script):
        """Test that .seda extension is added by default."""
        output_file = temp_dir / "test"
        
        result = conftest.run_script(
            packer_script,
            [str(sample_project['root']), str(output_file)]
        )
        
        assert result['success']
        # Should create test.seda
        assert (temp_dir / "test.seda").exists()


class TestPackerType5Archives:
    """Tests for Type 5 (commit) SEDA archive creation."""
    
    def test_create_type5_with_docstring(self, temp_dir, sample_project, packer_script):
        """Test Type 5 archive creation with docstring."""
        output_file = temp_dir / "test.commit.seda"
        docstring = "This is a test commit message\nWith multiple lines"
        
        result = conftest.run_script(
            packer_script,
            [str(sample_project['root']), str(output_file), "--docstring", docstring]
        )
        
        assert result['success'], f"Script failed: {result['stderr']}"
        assert output_file.exists()
        
        # Check that docstring is in the archive
        content = output_file.read_text(encoding='utf-8')
        assert docstring in content
    
    def test_type5_docstring_embedding(self, temp_dir, sample_project, packer_script):
        """Test that docstring is properly embedded in archive header."""
        output_file = temp_dir / "test.commit.seda"
        docstring = "Feature: Add new functionality\n\nThis commit adds important features."
        
        conftest.run_script(
            packer_script,
            [str(sample_project['root']), str(output_file), "--docstring", docstring]
        )
        
        content = output_file.read_text(encoding='utf-8')
        # Docstring should be in triple quotes near the top
        assert '"""' in content
        assert docstring in content
    
    def test_type5_commit_msg_extraction(self, temp_dir, sample_project, packer_script):
        """Test that commit_msg.txt is created when extracting Type 5 archive."""
        output_file = temp_dir / "test.commit.seda"
        docstring = "Test commit message for extraction"
        
        conftest.run_script(
            packer_script,
            [str(sample_project['root']), str(output_file), "--docstring", docstring]
        )
        
        # Extract the archive
        extract_dir = temp_dir / "extracted"
        extract_dir.mkdir()
        result = conftest.run_script(output_file, [], cwd=extract_dir)
        
        assert result['success']
        
        # Check that commit_msg.txt was created
        commit_msg_file = extract_dir / "commit_msg.txt"
        assert commit_msg_file.exists(), "commit_msg.txt was not created"
        
        # Check content matches
        extracted_msg = commit_msg_file.read_text(encoding='utf-8')
        assert docstring in extracted_msg
    
    def test_docstring_file_argument(self, temp_dir, sample_project, packer_script):
        """Test --docstring-file argument."""
        # Create a file with docstring content
        docstring_file = temp_dir / "commit_message.txt"
        docstring_content = "Commit message from file\n\nDetailed description here."
        docstring_file.write_text(docstring_content, encoding='utf-8')
        
        output_file = temp_dir / "test.commit.seda"
        result = conftest.run_script(
            packer_script,
            [str(sample_project['root']), str(output_file), "--docstring-file", str(docstring_file)]
        )
        
        assert result['success']
        
        # Check that docstring from file is in archive
        content = output_file.read_text(encoding='utf-8')
        assert docstring_content in content


class TestPackerCustomIgnore:
    """Tests for custom ignore patterns."""
    
    def test_custom_ignore_directories(self, temp_dir, packer_script):
        """Test custom ignore directories via --ignore-dirs."""
        project_dir = temp_dir / "custom_ignore_test"
        project_dir.mkdir()
        
        # Create custom directory to ignore
        custom_dir = project_dir / "temp_data"
        custom_dir.mkdir()
        (custom_dir / "data.txt").write_text("should be ignored")
        
        # Create normal file
        (project_dir / "main.py").write_text("print('hello')")
        
        output_file = temp_dir / "custom_ignore.seda"
        result = conftest.run_script(
            packer_script,
            [str(project_dir), str(output_file), "--ignore-dirs", "temp_data"]
        )
        
        assert result['success']
        
        # Check that custom directory was ignored
        content = output_file.read_text(encoding='utf-8')
        assert "temp_data" not in content or "temp_data/data.txt" not in content
        assert "main.py" in content
    
    def test_custom_ignore_extensions(self, temp_dir, packer_script):
        """Test custom ignore extensions via --ignore-exts."""
        project_dir = temp_dir / "ext_ignore_test"
        project_dir.mkdir()
        
        # Create files with custom extension to ignore
        (project_dir / "data.tmp").write_text("should be ignored")
        (project_dir / "backup.bak").write_text("should be ignored")
        
        # Create normal file
        (project_dir / "main.py").write_text("print('hello')")
        
        output_file = temp_dir / "ext_ignore.seda"
        result = conftest.run_script(
            packer_script,
            [str(project_dir), str(output_file), "--ignore-exts", ".tmp,.bak"]
        )
        
        assert result['success']
        
        # Check that custom extensions were ignored
        content = output_file.read_text(encoding='utf-8')
        assert "data.tmp" not in content
        assert "backup.bak" not in content
        assert "main.py" in content
    
    def test_multiple_custom_ignore_dirs(self, temp_dir, packer_script):
        """Test multiple custom ignore directories."""
        project_dir = temp_dir / "multi_ignore_test"
        project_dir.mkdir()
        
        # Create multiple directories to ignore
        (project_dir / "temp").mkdir()
        (project_dir / "temp" / "file.txt").write_text("ignore")
        (project_dir / "cache").mkdir()
        (project_dir / "cache" / "file.txt").write_text("ignore")
        
        (project_dir / "main.py").write_text("keep")
        
        output_file = temp_dir / "multi_ignore.seda"
        result = conftest.run_script(
            packer_script,
            [str(project_dir), str(output_file), "--ignore-dirs", "temp,cache"]
        )
        
        assert result['success']
        content = output_file.read_text(encoding='utf-8')
        assert "temp/file.txt" not in content
        assert "cache/file.txt" not in content
        assert "main.py" in content


class TestPackerRecursiveSeda:
    """Tests for --recursive-pack-seda flag."""
    
    def test_seda_files_ignored_by_default(self, temp_dir, packer_script):
        """Test that .seda files are ignored by default."""
        project_dir = temp_dir / "seda_default_test"
        project_dir.mkdir()
        
        (project_dir / "existing.seda").write_text("fake seda content")
        (project_dir / "main.py").write_text("print('test')")
        
        output_file = temp_dir / "default.seda"
        result = conftest.run_script(
            packer_script,
            [str(project_dir), str(output_file)]
        )
        
        assert result['success']
        assert "existing.seda" not in result['stdout']
        assert "main.py" in result['stdout']
    
    def test_recursive_pack_seda_flag(self, temp_dir, packer_script):
        """Test that --recursive-pack-seda includes .seda files."""
        project_dir = temp_dir / "seda_recursive_test"
        project_dir.mkdir()
        
        (project_dir / "existing.seda").write_text("fake seda content")
        (project_dir / "main.py").write_text("print('test')")
        
        output_file = temp_dir / "recursive.seda"
        result = conftest.run_script(
            packer_script,
            [str(project_dir), str(output_file), "--recursive-pack-seda"]
        )
        
        assert result['success']
        assert "Recursive SEDA Packing: ENABLED" in result['stdout']
        assert "existing.seda" in result['stdout']
        assert "main.py" in result['stdout']


class TestPackerDefaultIgnores:
    """Tests for default ignore patterns."""
    
    def test_default_ignore_pycache(self, temp_dir, packer_script):
        """Test that __pycache__ is ignored by default."""
        project_dir = temp_dir / "pycache_test"
        project_dir.mkdir()
        
        pycache = project_dir / "__pycache__"
        pycache.mkdir()
        (pycache / "test.pyc").write_bytes(b"fake")
        
        (project_dir / "main.py").write_text("print('test')")
        
        output_file = temp_dir / "pycache.seda"
        result = conftest.run_script(
            packer_script,
            [str(project_dir), str(output_file)]
        )
        
        assert result['success']
        assert "__pycache__" not in result['stdout'] or "__pycache__" not in output_file.read_text()
    
    def test_default_ignore_git(self, temp_dir, packer_script):
        """Test that .git directory is ignored by default."""
        project_dir = temp_dir / "git_test"
        project_dir.mkdir()
        
        git_dir = project_dir / ".git"
        git_dir.mkdir()
        (git_dir / "config").write_text("fake")
        
        (project_dir / "README.md").write_text("# Test")
        
        output_file = temp_dir / "git.seda"
        result = conftest.run_script(
            packer_script,
            [str(project_dir), str(output_file)]
        )
        
        assert result['success']
        content = output_file.read_text(encoding='utf-8')
        assert ".git/config" not in content


class TestPackerErrorHandling:
    """Tests for error handling and edge cases."""
    
    def test_nonexistent_directory_error(self, temp_dir, packer_script):
        """Test error handling for non-existent source directory."""
        nonexistent = temp_dir / "does_not_exist"
        output_file = temp_dir / "error.seda"
        
        result = conftest.run_script(
            packer_script,
            [str(nonexistent), str(output_file)]
        )
        
        assert not result['success'] or "does not exist" in result['stdout']
    
    def test_empty_directory(self, temp_dir, packer_script):
        """Test handling of empty directory."""
        empty_dir = temp_dir / "empty"
        empty_dir.mkdir()
        
        output_file = temp_dir / "empty.seda"
        result = conftest.run_script(
            packer_script,
            [str(empty_dir), str(output_file)]
        )
        
        assert result['success']
        assert output_file.exists()
        
        # Archive should be valid Python even with no files
        validation = conftest.validate_seda_archive(output_file)
        assert validation['is_valid_python']
    
    def test_invalid_docstring_file(self, temp_dir, sample_project, packer_script):
        """Test error handling for non-existent docstring file."""
        output_file = temp_dir / "test.seda"
        nonexistent_file = temp_dir / "nonexistent.txt"
        
        result = conftest.run_script(
            packer_script,
            [str(sample_project['root']), str(output_file), "--docstring-file", str(nonexistent_file)]
        )
        
        # Should fail or show error
        assert not result['success'] or "Error" in result['stdout'] or "Error" in result['stderr']


class TestPackerExtraction:
    """Tests for archive extraction."""
    
    def test_type0_extraction(self, temp_dir, sample_project, packer_script):
        """Test that Type 0 archives can be extracted."""
        output_file = temp_dir / "test.seda"
        conftest.run_script(
            packer_script,
            [str(sample_project['root']), str(output_file)]
        )
        
        # Extract
        extract_dir = temp_dir / "extracted"
        extract_dir.mkdir()
        result = conftest.run_script(output_file, [], cwd=extract_dir)
        
        assert result['success']
        assert "Extraction complete" in result['stdout']
        
        # Check files were extracted
        assert (extract_dir / "README.md").exists()
        assert (extract_dir / "main.py").exists()
    
    def test_extracted_content_matches(self, temp_dir, sample_project, packer_script):
        """Test that extracted content matches original."""
        output_file = temp_dir / "test.seda"
        conftest.run_script(
            packer_script,
            [str(sample_project['root']), str(output_file)]
        )
        
        extract_dir = temp_dir / "extracted"
        extract_dir.mkdir()
        conftest.run_script(output_file, [], cwd=extract_dir)
        
        # Compare content
        original_readme = (sample_project['root'] / "README.md").read_text()
        extracted_readme = (extract_dir / "README.md").read_text()
        assert original_readme == extracted_readme
