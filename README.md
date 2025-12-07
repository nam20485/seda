# 📦 SEDA: Self-Extracting Document Archive

**Version:** 0.9.1
**Status:** Beta

## What is SEDA?
SEDA is a protocol for packaging files, directory structures, and metadata into a single, executable Python script. It effectively turns a directory of code into a self-contained installer.

## Motivation
The protocol was invented to solve a specific friction point in AI-assisted software development: **The "Copy-Paste" Bottleneck.**

When an AI generates a multi-file project or a complex refactor:
1.  The human must copy/paste multiple files.
2.  File paths and directory structures are often lost or manual.
3.  The "context" (why these changes were made) is lost when moving from Chat to Git.

SEDA solves this by encapsulating the **Code**, the **Structure**, and the **Context** (Commit Message) into a single file that does the work for you.

## How It Works
A `.seda` file is a valid Python script containing:
1.  **The Header:** A docstring containing metadata or commit messages.
2.  **The Payload:** A Python dictionary where keys are file paths and values are content (Text or Base64-encoded Binary).
3.  **The Engine:** A small, embedded script that iterates through the payload and writes files to disk.

## The Tools

### `seda_packer.py`
Creates SEDA archives from existing directories.

**Usage:**
```bash
# Create a standard archive from a specific folder
python tools/seda_packer.py ./my-project

# Create a Commit Archive (Type 5) with a specific message
python tools/seda_packer.py ./my-project --docstring "Fix login bug" --output fix_login.commit.seda

# Create a self-distribution of the current repo (Type 0)
python tools/seda_packer.py . --output release_v0.9.1.seda

# Create a self-documenting distribution (Type 5) using README as the commit message
python tools/seda_packer.py . --docstring-file README.md --output release_v0.9.1.commit.seda
```

### `seda_bootstrap.py`
A lightweight script to generate SEDA files if the packer is not available.

## File Format & Subtypes

### 🟢 Type 0: SEDA-Core
The standard format.
* **Extension:** `.seda`
* **Behavior:** Unpacks files to the current directory.
* **Use Case:** Backups, project transport.

### 🟠 Type 5: SEDA-Commit
The "Patch" format.
* **Extension:** `.commit.seda`
* **Behavior:** 1.  Unpacks files to the current directory.
    2.  Extracts the archive's internal docstring/header into a file named `commit_msg.txt`.
* **Use Case:** Rapid "Chat-to-Git" workflow.
* **Workflow:**
    ```bash
    python feature.commit.seda
    git add .
    git commit -F commit_msg.txt
    ```


## Development and Testing

### Running Tests

The project includes a comprehensive test suite covering all functionality of both `seda_bootstrap.py` and `seda_packer.py`.

**Install test dependencies:**
```bash
pip install -r requirements-dev.txt
```

**Run all tests:**
```bash
pytest
```

**Run tests with verbose output:**
```bash
pytest -v
```

**Run tests with coverage:**
```bash
pytest --cov=. --cov-report=html
```

**Run specific test files:**
```bash
pytest tests/test_bootstrap.py
pytest tests/test_packer.py
pytest tests/test_extraction.py
```

### Test Structure

The test suite is organized into:
- `tests/test_bootstrap.py` - Tests for seda_bootstrap.py functionality
- `tests/test_packer.py` - Tests for seda_packer.py functionality
- `tests/test_extraction.py` - Integration tests for extraction and cross-platform behavior
- `tests/conftest.py` - Shared fixtures and utilities

### Continuous Integration

The project uses GitHub Actions to automatically run tests on:
- **Operating Systems:** Ubuntu, Windows, macOS
- **Python Versions:** 3.8, 3.9, 3.10, 3.11, 3.12

Tests run automatically on:
- Push to main/develop branches
- Pull request creation/updates
- Manual workflow dispatch

### Test Coverage

The test suite includes:
- 53+ unit and integration tests
- Archive creation and extraction tests
- Binary and text file handling tests
- Ignore pattern enforcement tests
- Error handling and edge case tests
- Cross-platform path handling tests
- End-to-end workflow tests
