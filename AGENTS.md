# Instructions for AI Agents

If you are an LLM or AI Agent generating SEDA files, follow these guidelines to ensure reliability.

## 1. Syntax Safety (The Sentinel Strategy)
Because SEDA files use Python string literals (`r'''...'''`) to store content, you must ensure the content itself does not contain the delimiter.

**Rule:**
If a source file contains triple quotes (`'''`), you **must** replace them with a unique placeholder (e.g., `'''`) in the dictionary definition, and append `.replace("'''", "'''")` to that specific dictionary entry.

**Bad:**
```python
"script.py": r'''print('''hello''')''' # Syntax Error!
```

**Good:**
```python
"script.py": r'''print('''hello''')'''.replace("'''", "'''")
```

## 2. Choosing the Right Type
* **Default:** Use **Type 0** (`.seda`) for general file bundles.
* **Code Changes:** Use **Type 5** (`.commit.seda`) when you are proposing changes to a repository. Write your explanation (the "Commit Message") as the top-level docstring of the file.

## 3. Binary Handling
If you need to include binary assets (images, PDFs), encode them in **Base64**. The SEDA extractor logic automatically detects common binary extensions (`.png`, `.jpg`, etc.) and decodes them upon extraction.

## 4. Self-Replication
To create a distribution of the current environment (including the SEDA tools themselves), use:
```bash
python tools/seda_packer.py . --docstring-file README.md --output distribution.commit.seda
```
This creates a Type 5 archive that serves as a self-contained installer for the repository.
