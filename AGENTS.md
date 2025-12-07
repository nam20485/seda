# Instructions for AI Agents

If you are an LLM or AI Agent generating SEDA files, follow these guidelines to ensure reliability and correctness.

## Overview

SEDA (Self-Extracting Document Archive) is a protocol for packaging files into executable Python scripts. As an AI agent, you can generate SEDA files to deliver multi-file projects, patches, or code changes in a single, self-contained package.

## 1. Syntax Safety (The Sentinel Strategy)

Because SEDA files use Python string literals (`r'''...'''`) to store content, you must ensure the content itself does not contain the delimiter.

**Rule:**
If a source file contains triple quotes (`'''`), you **must** replace them with a unique placeholder (e.g., `'''`) in the dictionary definition, and append `.replace("'''", "'''")` to that specific dictionary entry.

**Bad:**
```python
"script.py": r'''print('''hello''')'''  # Syntax Error!
```

**Good:**
```python
"script.py": r'''print('''hello''')'''.replace("'''", "'''")
```

**Detection Strategy:**
- Scan each file's content for `'''` before adding to the payload
- If found, use the `.replace()` pattern
- This applies to both text and code files

## 2. Choosing the Right Type

### Type 0: SEDA-Core (`.seda`)
**Use for:**
- General file bundles
- Project backups
- Code libraries
- Documentation packages
- Any multi-file delivery that doesn't need commit context

**Example:**
```bash
python tools/seda_packer.py ./my-library --output my-library-v1.0.seda
```

### Type 5: SEDA-Commit (`.commit.seda`)
**Use for:**
- Code changes/patches
- Feature implementations
- Bug fixes
- Refactoring work
- Any change that should become a git commit

**Key Feature:** Automatically extracts commit message to `commit_msg.txt`

**Example:**
```bash
python tools/seda_packer.py ./changes --docstring "Fix authentication bug" --output fix-auth.commit.seda
```

**Workflow:**
```bash
# User runs the commit archive
python fix-auth.commit.seda

# Files are extracted and commit message is ready
git add .
git commit -F commit_msg.txt
```

## 3. Binary Handling

### Automatic Detection
The SEDA tools automatically detect binary files based on:
- File extension (`.png`, `.jpg`, `.ico`, `.svg`, `.pdf`, `.zip`, `.exe`)
- Content analysis (files that can't be read as UTF-8 text)

### Encoding Rules
- **Binary files:** Automatically Base64-encoded in the payload
- **Text files:** Stored as raw strings
- **Mixed projects:** Both types handled transparently

### Supported Binary Extensions
```python
['.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', 
 '.pdf', '.zip', '.tar', '.gz', '.exe', '.dll', 
 '.so', '.dylib', '.woff', '.woff2', '.ttf', '.eot']
```

### Manual Binary Encoding (if needed)
```python
import base64

with open('image.png', 'rb') as f:
    encoded = base64.b64encode(f.read()).decode('utf-8')
    
payload = {
    'image.png': encoded
}
```

## 4. File Ignore Patterns

### Default Ignored Directories
```python
['node_modules', '__pycache__', '.git', 'dist', 
 'build', '.DS_Store', '.idea', '.vscode', 'coverage']
```

### Default Ignored Extensions
```python
['.pyc', '.log', '.seda', '.exe', '.dll', 
 '.so', '.dylib', '.zip']
```

### Custom Ignore Patterns
```bash
# Ignore additional directories
python tools/seda_packer.py ./project --ignore-dirs "temp,cache,logs"

# Ignore additional extensions
python tools/seda_packer.py ./project --ignore-exts ".tmp,.bak,.swp"
```

## 5. Advanced Features

### Recursive SEDA Packing
By default, `.seda` files are ignored. To include them:
```bash
python tools/seda_packer.py ./project --recursive-pack-seda
```

**Use case:** Creating a SEDA archive that contains other SEDA archives

### Docstring from File
```bash
python tools/seda_packer.py ./project --docstring-file CHANGELOG.md
```

**Use case:** Using existing documentation as the commit message

### Self-Replication
To create a distribution of the current environment (including the SEDA tools themselves):
```bash
python tools/seda_packer.py . --docstring-file README.md --output distribution.commit.seda
```

This creates a Type 5 archive that serves as a self-contained installer for the repository.

## 6. Best Practices for AI Agents

### When Generating Code Changes
1. **Always use Type 5** (`.commit.seda`) for code changes
2. **Write clear commit messages** explaining what changed and why
3. **Include context** in the docstring about the problem being solved
4. **Test the archive** before delivering (if possible)

### Commit Message Format
```
Brief summary of changes (50 chars or less)

Detailed explanation of what changed and why. Include:
- What problem this solves
- What approach was taken
- Any important implementation details
- Breaking changes or migration notes

Fixes: #issue-number (if applicable)
```

### File Organization
- Maintain the original directory structure
- Don't flatten nested directories
- Preserve relative paths
- Keep related files together

### Error Prevention
1. **Check for triple quotes** in all text content
2. **Verify binary files** are properly detected
3. **Test extraction** in a clean directory
4. **Validate Python syntax** of generated archive

## 7. Testing Generated Archives

### Quick Validation
```bash
# Check if archive is valid Python
python -m py_compile archive.seda

# Test extraction in temp directory
mkdir test_extract && cd test_extract
python ../archive.seda
```

### Automated Testing
The SEDA project includes comprehensive tests. Run them with:
```bash
pytest tests/
```

## 8. Common Pitfalls

### ❌ Don't Do This
```python
# Hardcoded paths
"file.txt": r'''/home/user/project/file.txt'''

# Absolute paths in payload keys
"/absolute/path/file.txt": r'''content'''

# Unescaped triple quotes
"code.py": r'''def foo():
    """docstring"""  # This will break!
'''
```

### ✅ Do This Instead
```python
# Relative paths
"file.txt": r'''content'''

# Relative paths in payload keys
"src/utils/file.txt": r'''content'''

# Escaped triple quotes
"code.py": r'''def foo():
    """docstring"""
'''.replace('"""', '"""')
```

## 9. Platform Compatibility

### Path Separators
- Always use forward slashes (`/`) in payload keys
- The extractor handles platform-specific separators automatically
- Example: `"src/utils/helper.py"` works on all platforms

### Line Endings
- Text files preserve their original line endings
- No automatic conversion (CRLF ↔ LF)
- Binary files are byte-perfect

### Encoding
- All text files use UTF-8 encoding
- Binary files use Base64 encoding
- Archive files themselves are UTF-8

## 10. Integration with Development Workflows

### Chat-to-Git Workflow
```bash
# 1. AI generates fix-bug.commit.seda
# 2. User extracts it
python fix-bug.commit.seda

# 3. Review changes
git diff

# 4. Commit with extracted message
git add .
git commit -F commit_msg.txt

# 5. Clean up
rm commit_msg.txt
```

### Code Review Workflow
```bash
# 1. AI generates feature.commit.seda
# 2. Reviewer extracts to review branch
git checkout -b review/feature
python feature.commit.seda

# 3. Review and test
pytest
git diff

# 4. Approve or request changes
```

### Deployment Workflow
```bash
# 1. Create release archive
python tools/seda_packer.py . --output release-v1.0.seda

# 2. Deploy to server
scp release-v1.0.seda server:/tmp/

# 3. Extract on server
ssh server "cd /app && python /tmp/release-v1.0.seda"
```

## 11. Troubleshooting

### Archive Won't Execute
- Check for syntax errors: `python -m py_compile archive.seda`
- Verify triple quotes are escaped
- Ensure file is UTF-8 encoded

### Files Not Extracted
- Check ignore patterns
- Verify file paths are relative
- Ensure binary files are properly encoded

### Commit Message Not Created
- Verify using Type 5 (`.commit.seda` extension)
- Check docstring is present in archive
- Ensure archive filename ends with `.commit.seda`

## 12. Security Considerations

### What SEDA Does NOT Do
- No code signing or verification
- No encryption of payload
- No sandboxing of extraction
- No validation of file contents

### Safe Usage
- Only run SEDA archives from trusted sources
- Review archive contents before extraction
- Extract in isolated directories for testing
- Use version control to track changes

### For AI Agents
- Never include sensitive data (passwords, keys, tokens)
- Don't generate archives that modify system files
- Avoid including executable binaries without user consent
- Document any security-relevant changes in commit messages

## 13. Performance Considerations

### Archive Size
- Text files: ~1x original size
- Binary files: ~1.33x original size (Base64 overhead)
- Typical project: 1-10 MB
- Large projects: Consider splitting into multiple archives

### Extraction Speed
- Fast for small projects (< 1 second)
- Scales linearly with file count
- Binary files slightly slower (Base64 decoding)

### Optimization Tips
- Exclude unnecessary files (logs, caches, build artifacts)
- Use ignore patterns effectively
- Consider compressing large binary files before encoding
- Split very large projects into logical chunks

## 14. Version Compatibility

### Python Versions
- Minimum: Python 3.6
- Recommended: Python 3.8+
- Tested: Python 3.8, 3.9, 3.10, 3.11, 3.12

### Cross-Version Compatibility
- Archives created on Python 3.8 work on Python 3.12
- Archives created on Python 3.12 work on Python 3.8
- No version-specific features used

## 15. Quick Reference

### Create Standard Archive
```bash
python tools/seda_packer.py <directory> --output <name>.seda
```

### Create Commit Archive
```bash
python tools/seda_packer.py <directory> --docstring "message" --output <name>.commit.seda
```

### Extract Archive
```bash
python <archive>.seda
```

### Test Archive
```bash
python -m py_compile <archive>.seda
```

### View Archive Contents
```bash
# Archives are just Python files - you can read them!
cat <archive>.seda | head -50
```
