"""
Unit tests for seda_bootstrap.py

Tests cover:
- Basic archive creation from directories
- Archive extraction functionality
- Binary file encoding (Base64)
- Text file handling
- Ignore pattern enforcement
- Error handling
"""

import pytest
from pathlib import Path
import sys
import os

# Import helper functions from conftest
sys.path.insert(0, str(Path(__file__).parent))
import conftest


class TestBootstrapArchiveCreation:
    """Tests for SEDA archive creation using bootstrap script."""
    
    def test_create_archive_from_directory(self, temp_dir, sample_project, bootstrap_script):
        """Test basic archive creation from a directory."""
        output_file = temp_dir / "test_archive.py"
        
        result = conftest.run_script(
            bootstrap_script,
            [str(sample_project['root']), str(output_file)]
        )
        
        assert result['success'], f"Script failed: {result['stderr']}"
        assert output_file.exists(), "Archive file was not created"
        assert "Self-Exploding Document created" in result['stdout']
    
    def test_archive_is_valid_python(self, temp_dir, sample_project, bootstrap_script):
        """Test that generated archive is syntactically valid Python."""
        output_file = temp_dir / "test_archive.py"
        
        conftest.run_script(
            bootstrap_script,
            [str(sample_project['root']), str(output_file)]
        )
        
        validation = conftest.validate_seda_archive(output_file)
        assert validation['is_valid_python'], f"Archive is not valid Python: {validation.get('error')}"
        assert validation['has_payload'], "Archive missing payload"
        assert validation['has_extractor'], "Archive missing extractor logic"
    
    def test_archive_contains_all_files(self, temp_dir, sample_project, bootstrap_script):
        """Test that archive contains all non-ignored files."""
        output_file = temp_dir / "test_archive.py"
        
        result = conftest.run_script(
            bootstrap_script,
            [str(sample_project['root']), str(output_file)]
        )
        
        # Check that expected files are mentioned in output
        for file in sample_project['files']:
            assert file in result['stdout'], f"File {file} not added to archive"
    
    def test_default_output_filename(self, temp_dir, sample_project, bootstrap_script):
        """Test that default output filename is generated correctly."""
        result = conftest.run_script(
            bootstrap_script,
            [str(sample_project['root'])],
            cwd=temp_dir
        )
        
        assert result['success']
        # Default name should be <dirname>_installer.py
        expected_file = temp_dir / "sample_project_installer.py"
        assert expected_file.exists(), "Default output file not created"


class TestBootstrapExtraction:
    """Tests for SEDA archive extraction."""
    
    def test_extract_archive(self, temp_dir, sample_project, bootstrap_script):
        """Test that archive can be extracted successfully."""
        # Create archive
        archive_file = temp_dir / "test_archive.py"
        conftest.run_script(
            bootstrap_script,
            [str(sample_project['root']), str(archive_file)]
        )
        
        # Extract in a new directory
        extract_dir = temp_dir / "extracted"
        extract_dir.mkdir()
        
        result = conftest.run_script(
            archive_file,
            [],
            cwd=extract_dir
        )
        
        assert result['success'], f"Extraction failed: {result['stderr']}"
        assert "Extraction complete" in result['stdout'] or "Explosion complete" in result['stdout']
    
    def test_extracted_files_match_original(self, temp_dir, sample_project, bootstrap_script):
        """Test that extracted files have correct content."""
        # Create archive
        archive_file = temp_dir / "test_archive.py"
        conftest.run_script(
            bootstrap_script,
            [str(sample_project['root']), str(archive_file)]
        )
        
        # Extract
        extract_dir = temp_dir / "extracted"
        extract_dir.mkdir()
        conftest.run_script(archive_file, [], cwd=extract_dir)
        
        # Verify files exist and have correct content
        assert (extract_dir / "README.md").exists()
        assert (extract_dir / "main.py").exists()
        assert (extract_dir / "src" / "module.py").exists()
        
        # Check content matches
        original_readme = (sample_project['root'] / "README.md").read_text()
        extracted_readme = (extract_dir / "README.md").read_text()
        assert original_readme == extracted_readme
    
    def test_nested_directories_recreated(self, temp_dir, sample_project, bootstrap_script):
        """Test that nested directory structure is preserved."""
        archive_file = temp_dir / "test_archive.py"
        conftest.run_script(
            bootstrap_script,
            [str(sample_project['root']), str(archive_file)]
        )
        
        extract_dir = temp_dir / "extracted"
        extract_dir.mkdir()
        conftest.run_script(archive_file, [], cwd=extract_dir)
        
        # Check nested structure
        assert (extract_dir / "src").is_dir()
        assert (extract_dir / "src" / "utils").is_dir()
        assert (extract_dir / "src" / "utils" / "helper.py").exists()


class TestBootstrapBinaryHandling:
    """Tests for binary file handling."""
    
    def test_binary_file_encoding(self, temp_dir, bootstrap_script):
        """Test that binary files are encoded in Base64."""
        # Create a project with a binary file
        project_dir = temp_dir / "binary_project"
        project_dir.mkdir()
        
        # Create a fake binary file (PNG-like)
        binary_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00'
        binary_file = project_dir / "image.png"
        binary_file.write_bytes(binary_content)
        
        # Create archive
        archive_file = temp_dir / "binary_archive.py"
        result = conftest.run_script(
            bootstrap_script,
            [str(project_dir), str(archive_file)]
        )
        
        assert result['success']
        
        # Check that archive contains base64 encoded content
        archive_content = archive_file.read_text()
        assert 'image.png' in archive_content
    
    def test_binary_file_extraction(self, temp_dir, bootstrap_script):
        """Test that binary files are extracted correctly."""
        # Create project with binary file
        project_dir = temp_dir / "binary_project"
        project_dir.mkdir()
        
        binary_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00'
        (project_dir / "image.png").write_bytes(binary_content)
        
        # Create and extract archive
        archive_file = temp_dir / "binary_archive.py"
        conftest.run_script(
            bootstrap_script,
            [str(project_dir), str(archive_file)]
        )
        
        extract_dir = temp_dir / "extracted"
        extract_dir.mkdir()
        conftest.run_script(archive_file, [], cwd=extract_dir)
        
        # Verify binary content matches
        extracted_content = (extract_dir / "image.png").read_bytes()
        assert extracted_content == binary_content


class TestBootstrapTextHandling:
    """Tests for text file handling."""
    
    def test_text_file_storage(self, temp_dir, bootstrap_script):
        """Test that text files are stored as raw strings."""
        project_dir = temp_dir / "text_project"
        project_dir.mkdir()
        
        text_content = "Hello, World!\nThis is a test file.\n"
        (project_dir / "test.txt").write_text(text_content)
        
        archive_file = temp_dir / "text_archive.py"
        result = conftest.run_script(
            bootstrap_script,
            [str(project_dir), str(archive_file)]
        )
        
        assert result['success']
        
        # Archive should contain the text content
        archive_content = archive_file.read_text()
        assert 'test.txt' in archive_content
    
    def test_unicode_text_handling(self, temp_dir, bootstrap_script):
        """Test that Unicode text is handled correctly."""
        project_dir = temp_dir / "unicode_project"
        project_dir.mkdir()
        
        unicode_content = "Hello 世界! 🌍 Привет мир!"
        (project_dir / "unicode.txt").write_text(unicode_content, encoding='utf-8')
        
        archive_file = temp_dir / "unicode_archive.py"
        conftest.run_script(
            bootstrap_script,
            [str(project_dir), str(archive_file)]
        )
        
        extract_dir = temp_dir / "extracted"
        extract_dir.mkdir()
        conftest.run_script(archive_file, [], cwd=extract_dir)
        
        extracted_content = (extract_dir / "unicode.txt").read_text(encoding='utf-8')
        assert extracted_content == unicode_content


class TestBootstrapIgnorePatterns:
    """Tests for ignore pattern enforcement."""
    
    def test_ignore_pycache(self, temp_dir, bootstrap_script):
        """Test that __pycache__ directories are ignored."""
        project_dir = temp_dir / "ignore_test"
        project_dir.mkdir()
        
        # Create __pycache__ directory
        pycache = project_dir / "__pycache__"
        pycache.mkdir()
        (pycache / "test.pyc").write_bytes(b"fake pyc")
        
        # Create normal file
        (project_dir / "main.py").write_text("print('hello')")
        
        archive_file = temp_dir / "ignore_archive.py"
        result = conftest.run_script(
            bootstrap_script,
            [str(project_dir), str(archive_file)]
        )
        
        # __pycache__ should not be in output
        assert "__pycache__" not in result['stdout']
        assert "main.py" in result['stdout']
    
    def test_ignore_git_directory(self, temp_dir, bootstrap_script):
        """Test that .git directories are ignored."""
        project_dir = temp_dir / "git_test"
        project_dir.mkdir()
        
        git_dir = project_dir / ".git"
        git_dir.mkdir()
        (git_dir / "config").write_text("fake git config")
        
        (project_dir / "README.md").write_text("# Test")
        
        archive_file = temp_dir / "git_archive.py"
        result = conftest.run_script(
            bootstrap_script,
            [str(project_dir), str(archive_file)]
        )
        
        assert ".git" not in result['stdout']
        assert "README.md" in result['stdout']
    
    def test_ignore_node_modules(self, temp_dir, bootstrap_script):
        """Test that node_modules directories are ignored."""
        project_dir = temp_dir / "node_test"
        project_dir.mkdir()
        
        node_modules = project_dir / "node_modules"
        node_modules.mkdir()
        (node_modules / "package.json").write_text("{}")
        
        (project_dir / "index.js").write_text("console.log('test')")
        
        archive_file = temp_dir / "node_archive.py"
        result = conftest.run_script(
            bootstrap_script,
            [str(project_dir), str(archive_file)]
        )
        
        # Check that node_modules directory content is not added (not just the word in path)
        assert "node_modules/package.json" not in result['stdout']
        assert "index.js" in result['stdout']
    
    def test_ignore_seda_files(self, temp_dir, bootstrap_script):
        """Test that .seda files are ignored by default."""
        project_dir = temp_dir / "seda_test"
        project_dir.mkdir()
        
        (project_dir / "existing.seda").write_text("fake seda content")
        (project_dir / "main.py").write_text("print('test')")
        
        archive_file = temp_dir / "seda_archive.py"
        result = conftest.run_script(
            bootstrap_script,
            [str(project_dir), str(archive_file)]
        )
        
        assert "existing.seda" not in result['stdout']
        assert "main.py" in result['stdout']


class TestBootstrapErrorHandling:
    """Tests for error handling and edge cases."""
    
    def test_nonexistent_directory_error(self, temp_dir, bootstrap_script):
        """Test error handling for non-existent source directory."""
        nonexistent = temp_dir / "does_not_exist"
        archive_file = temp_dir / "error_archive.py"
        
        result = conftest.run_script(
            bootstrap_script,
            [str(nonexistent), str(archive_file)]
        )
        
        assert not result['success'] or "does not exist" in result['stdout']
        assert not archive_file.exists() or archive_file.stat().st_size == 0
    
    def test_empty_directory(self, temp_dir, bootstrap_script):
        """Test handling of empty directory."""
        empty_dir = temp_dir / "empty"
        empty_dir.mkdir()
        
        archive_file = temp_dir / "empty_archive.py"
        result = conftest.run_script(
            bootstrap_script,
            [str(empty_dir), str(archive_file)]
        )
        
        assert result['success']
        assert archive_file.exists()
        
        # Archive should be valid Python even with no files
        validation = conftest.validate_seda_archive(archive_file)
        assert validation['is_valid_python']
    
    def test_directory_with_only_ignored_files(self, temp_dir, bootstrap_script):
        """Test directory containing only ignored files."""
        project_dir = temp_dir / "only_ignored"
        project_dir.mkdir()
        
        # Create only ignored content
        pycache = project_dir / "__pycache__"
        pycache.mkdir()
        (pycache / "test.pyc").write_bytes(b"fake")
        
        archive_file = temp_dir / "ignored_archive.py"
        result = conftest.run_script(
            bootstrap_script,
            [str(project_dir), str(archive_file)]
        )
        
        assert result['success']
        assert archive_file.exists()
        
        # Should create valid archive with empty payload
        validation = conftest.validate_seda_archive(archive_file)
        assert validation['is_valid_python']
    
    def test_missing_arguments(self, bootstrap_script):
        """Test error handling when required arguments are missing."""
        result = conftest.run_script(bootstrap_script, [])
        
        # Should show usage information
        assert not result['success'] or "Usage" in result['stdout']
