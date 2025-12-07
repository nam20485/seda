# Design Document

## Overview

This design document outlines the implementation of a comprehensive testing suite and CI workflow for the SEDA tools. The solution will use Python's `pytest` framework for unit testing and `hypothesis` for property-based testing. The CI workflow will be implemented using GitHub Actions to ensure cross-platform compatibility and multi-version Python support.

The testing strategy follows a dual approach: unit tests validate specific behaviors and edge cases, while property-based tests verify universal correctness properties across randomly generated inputs. This combination provides both concrete validation and broad coverage.

## Architecture

### Testing Architecture

The testing system consists of three main layers:

1. **Test Fixtures Layer**: Provides reusable test utilities, temporary directory management, and sample data generation
2. **Unit Test Layer**: Contains specific test cases for known scenarios, edge cases, and error conditions
3. **Property-Based Test Layer**: Contains generative tests that validate universal properties across random inputs

### CI Architecture

The CI system uses GitHub Actions with a matrix strategy to test across:
- Multiple Python versions (3.8, 3.9, 3.10, 3.11, 3.12)
- Multiple operating systems (Ubuntu, Windows, macOS)
- Multiple test suites (unit tests, property-based tests)

## Components and Interfaces

### Test Fixtures (`tests/conftest.py`)

**Purpose**: Provide reusable test utilities and fixtures

**Key Components**:
- `temp_dir`: Pytest fixture that creates and cleans up temporary directories
- `sample_project`: Fixture that creates a sample directory structure with various file types
- `create_test_file`: Helper function to create files with specific content
- `run_script`: Helper function to execute Python scripts and capture output

### Unit Tests (`tests/test_bootstrap.py`, `tests/test_packer.py`)

**Purpose**: Validate specific behaviors and edge cases

**Test Categories**:
- Archive creation tests
- Extraction tests
- Binary file handling tests
- Text file handling tests
- Ignore pattern tests
- Error handling tests
- Command-line argument tests

### Property-Based Tests (`tests/test_properties.py`)

**Purpose**: Validate universal correctness properties

**Test Categories**:
- Round-trip consistency tests
- Content preservation tests
- Structure preservation tests
- Sentinel strategy tests

### CI Workflow (`.github/workflows/test.yml`)

**Purpose**: Automate testing on code changes

**Triggers**:
- Push to main branch
- Pull request creation/update
- Manual workflow dispatch

**Jobs**:
- Test matrix across Python versions and operating systems
- Install dependencies
- Run pytest with coverage reporting
- Upload test results and coverage reports

## Data Models

### Test Data Structures

```python
# Sample project structure for testing
SampleProject = {
    'files': List[Tuple[str, str, bool]],  # (path, content, is_binary)
    'directories': List[str],
    'ignored_items': List[str]
}

# Test execution result
TestResult = {
    'success': bool,
    'stdout': str,
    'stderr': str,
    'exit_code': int
}

# Archive validation result
ArchiveValidation = {
    'is_valid_python': bool,
    'has_payload': bool,
    'has_extractor': bool,
    'file_count': int
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property 1: Round-trip preservation

*For any* directory structure containing text files, binary files, and nested directories, packing the directory into a SEDA archive and then extracting it should reproduce all original files with identical content, structure, and hierarchy.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4**

### Property 2: Sentinel strategy safety

*For any* file content containing triple quotes (`'''`), the generated SEDA archive should be syntactically valid Python without syntax errors.

**Validates: Requirements 3.5**

### Property 3: Ignore pattern enforcement

*For any* directory structure containing directories from the ignore list (node_modules, __pycache__, .git, etc.), those directories should not appear in the generated SEDA archive payload.

**Validates: Requirements 1.5**

### Property 4: Custom ignore directories

*For any* set of custom ignore directory names provided via command-line arguments, directories matching those names should be excluded from the archive in addition to default ignores.

**Validates: Requirements 2.4**

### Property 5: Custom ignore extensions

*For any* set of custom file extensions provided via command-line arguments, files with those extensions should be excluded from the archive in addition to default ignores.

**Validates: Requirements 2.5**

### Property 6: Commit message round-trip

*For any* text content used as a docstring when creating a Type 5 SEDA-Commit archive, extracting that archive should produce a commit_msg.txt file containing identical text content.

**Validates: Requirements 2.3**

### Property 7: Docstring embedding

*For any* docstring content provided to the packer script, the generated SEDA archive should contain that exact content in its file header docstring.

**Validates: Requirements 2.2**

### Property 8: Recursive SEDA packing

*For any* directory containing .seda files, when the --recursive-pack-seda flag is enabled, those .seda files should be included in the generated archive; when the flag is disabled, they should be excluded.

**Validates: Requirements 2.6**

### Property 9: Docstring file reading

*For any* file containing text content, when that file is specified via --docstring-file argument, the generated archive should have a docstring matching the file's content.

**Validates: Requirements 2.7**

### Property 10: File overwrite behavior

*For any* existing file in a directory, when a SEDA archive containing a file with the same path is extracted, the existing file should be overwritten with the archive's content.

**Validates: Requirements 4.5**

### Property 11: Special character filename handling

*For any* filename containing special characters (spaces, Unicode, punctuation), the system should correctly pack and extract files with those names.

**Validates: Requirements 5.4**

### Property 12: Cross-platform path handling

*For any* file path, the system should normalize path separators correctly across different operating systems (Windows backslashes vs Unix forward slashes).

**Validates: Requirements 7.5**

## Error Handling

### Error Scenarios

1. **Non-existent source directory**: Both scripts should detect when the source directory doesn't exist and display a clear error message without crashing
2. **Empty directories**: Scripts should handle empty directories gracefully and create valid (but empty) archives
3. **Permission errors**: Scripts should handle file permission errors gracefully and report which files couldn't be processed
4. **Invalid command-line arguments**: Scripts should validate arguments and display helpful usage information
5. **Extraction failures**: The extractor should handle individual file extraction failures without stopping the entire process

### Error Messages

All error messages should:
- Clearly identify what went wrong
- Provide context about which file or operation failed
- Suggest potential solutions when applicable
- Use consistent formatting with emoji indicators (❌ for errors, ⚠️ for warnings)

## Testing Strategy

### Unit Testing Approach

Unit tests will use `pytest` as the testing framework. Tests will be organized into separate files:

- `tests/test_bootstrap.py`: Tests for seda_bootstrap.py functionality
- `tests/test_packer.py`: Tests for seda_packer.py functionality
- `tests/test_extraction.py`: Tests for archive extraction behavior
- `tests/conftest.py`: Shared fixtures and utilities

**Unit Test Categories**:
1. **Basic functionality tests**: Verify core operations work with simple inputs
2. **Edge case tests**: Test empty directories, single files, deeply nested structures
3. **Error handling tests**: Verify proper error messages for invalid inputs
4. **Command-line argument tests**: Verify all CLI flags work correctly
5. **Integration tests**: Test complete workflows from pack to extract

**Unit Test Examples**:
- Test that non-existent directory produces error (Requirement 4.1, 4.2)
- Test that empty directory creates valid archive (Requirement 4.3)
- Test that directory with only ignored files creates empty archive (Requirement 4.4)

### Property-Based Testing Approach

Property-based tests will use `hypothesis` library for Python. Hypothesis will generate random test data to validate universal properties.

**Configuration**:
- Each property-based test MUST run a minimum of 100 iterations
- Tests MUST be tagged with comments referencing the design document property
- Tag format: `# Feature: seda-testing-ci, Property {number}: {property_text}`

**Property Test Implementation Requirements**:
1. Each correctness property MUST be implemented by a SINGLE property-based test
2. Tests MUST use hypothesis strategies to generate random inputs
3. Tests MUST validate the property holds for all generated inputs
4. When tests fail, hypothesis will automatically shrink the failing input to the minimal example

**Hypothesis Strategies**:
- `directory_structure`: Generates random directory trees with files
- `file_content`: Generates random text and binary content
- `filenames`: Generates valid filenames including edge cases
- `docstrings`: Generates random text for commit messages
- `ignore_patterns`: Generates random ignore lists

**Property Test Examples**:
- Property 1 (Round-trip): Generate random directory → pack → extract → verify identical
- Property 2 (Sentinel): Generate content with triple quotes → pack → verify valid Python
- Property 6 (Commit round-trip): Generate random docstring → pack Type 5 → extract → verify commit_msg.txt

### Test Execution

**Local Testing**:
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run only unit tests
pytest tests/test_bootstrap.py tests/test_packer.py

# Run only property tests
pytest tests/test_properties.py

# Run with verbose output
pytest -v
```

**CI Testing**:
- Tests run automatically on push and pull requests
- Matrix testing across Python 3.8, 3.9, 3.10, 3.11, 3.12
- Matrix testing across Ubuntu, Windows, macOS
- Coverage reports uploaded to workflow artifacts

### Test Data Management

**Temporary Directories**:
- Use pytest's `tmp_path` fixture for isolated test environments
- Each test gets a fresh temporary directory
- Automatic cleanup after test completion

**Sample Data**:
- Create reusable fixtures for common test scenarios
- Include samples of: text files, binary files, nested directories, special characters
- Store minimal sample data in fixtures, generate larger data with hypothesis

## CI Workflow Design

### GitHub Actions Workflow

**File**: `.github/workflows/test.yml`

**Workflow Structure**:
```yaml
name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  workflow_dispatch:

jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.8', '3.9', '3.10', '3.11', '3.12']
    
    runs-on: ${{ matrix.os }}
    
    steps:
      - Checkout code
      - Setup Python
      - Install dependencies
      - Run pytest with coverage
      - Upload coverage reports
      - Upload test results
```

**Workflow Features**:
1. **Matrix testing**: Automatically tests all combinations of OS and Python version
2. **Dependency caching**: Caches pip packages to speed up workflow
3. **Coverage reporting**: Generates and uploads coverage reports
4. **Artifact upload**: Saves test results and coverage for review
5. **Status badges**: Provides badge for README showing test status

### CI Requirements

**Dependencies**:
- pytest >= 7.0.0
- hypothesis >= 6.0.0
- pytest-cov >= 4.0.0

**Test Execution**:
- All tests must pass for CI to succeed
- Coverage threshold: aim for >90% code coverage
- Property tests must complete within reasonable time (< 5 minutes per test file)

### Failure Handling

**When Tests Fail**:
1. CI marks the build as failed
2. GitHub prevents merging if required checks fail
3. Test output shows which specific tests failed
4. Hypothesis shows minimal failing example for property tests
5. Coverage report shows which lines aren't tested

## Implementation Notes

### Testing Best Practices

1. **Isolation**: Each test should be independent and not rely on other tests
2. **Clarity**: Test names should clearly describe what is being tested
3. **Minimal**: Tests should be as simple as possible while still being thorough
4. **Fast**: Unit tests should run quickly; property tests may take longer
5. **Deterministic**: Tests should produce consistent results (except for property tests which are intentionally random)

### Hypothesis Strategy Design

**Smart Generators**:
- Constrain generated data to valid input space
- Include edge cases in generation (empty strings, special characters, etc.)
- Use `hypothesis.strategies.composite` for complex data structures
- Use `hypothesis.assume()` to filter invalid combinations

**Example Strategy**:
```python
@composite
def directory_structure(draw):
    # Generate 0-10 files
    num_files = draw(integers(min_value=0, max_value=10))
    # Generate filenames without path separators
    filenames = draw(lists(
        text(alphabet=characters(blacklist_categories=['Cs']), 
             min_size=1, max_size=50),
        min_size=num_files, max_size=num_files
    ))
    # Generate content for each file
    contents = draw(lists(
        one_of(text(), binary()),
        min_size=num_files, max_size=num_files
    ))
    return list(zip(filenames, contents))
```

### Cross-Platform Considerations

1. **Path Separators**: Always use `os.path.join()` and normalize paths
2. **Line Endings**: Be aware of CRLF vs LF differences
3. **File Permissions**: Windows doesn't support Unix-style permissions
4. **Case Sensitivity**: Windows is case-insensitive, Unix is case-sensitive
5. **Executable Bit**: The `chmod +x` operation may not work on Windows

### Coverage Goals

**Target Coverage**:
- Overall: >90%
- Core packing logic: 100%
- Core extraction logic: 100%
- Error handling: >80%
- CLI argument parsing: >90%

**Excluded from Coverage**:
- `if __name__ == "__main__"` blocks (tested via integration tests)
- Platform-specific code that can't run on all platforms
- Defensive error handling for truly exceptional cases

## Dependencies

### Testing Dependencies

```
pytest>=7.0.0
hypothesis>=6.0.0
pytest-cov>=4.0.0
```

### Runtime Dependencies

The SEDA tools themselves have no external dependencies (only Python stdlib), which should be preserved. Tests may use external libraries, but the tools should remain dependency-free.

## Future Enhancements

### Potential Improvements

1. **Performance testing**: Add tests to measure pack/extract speed
2. **Stress testing**: Test with very large files and deep directory structures
3. **Mutation testing**: Use mutation testing to verify test quality
4. **Benchmark tracking**: Track performance over time
5. **Security testing**: Test handling of malicious or malformed archives
6. **Documentation testing**: Use doctest for documentation examples

### Monitoring and Metrics

1. **Test execution time**: Track how long tests take to run
2. **Coverage trends**: Monitor coverage percentage over time
3. **Flaky test detection**: Identify tests that fail intermittently
4. **Property test statistics**: Track how many examples hypothesis generates
