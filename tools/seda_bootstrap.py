import os
import sys
import base64

# The "Self-Exploding" Header
# This makes the file executable Python AND readable Markdown.
BOOTSTRAP_HEADER = r'''#!/usr/bin/env python3
"""
# 📦 Self-Extracting Document Archive (SEDA)

This file is a **self-extracting archive**. You can read it as documentation, or you can **run it** to unpack the contents.

## 🚀 Quick Start

To extract the contents of this archive, simply run this file with Python:

```bash
python {filename}
```

## 📄 Contents

This archive contains the following files:
{file_list}

---
**Technical Details:**
This file is a valid Python script that contains a payload of files encoded in Base64.
When executed, it will recreate the directory structure in your current folder.

_(The extraction logic is embedded below this documentation)_
"""
import os
import base64
import sys

# --- END OF DOCUMENTATION / START OF PAYLOAD ---
'''

# The Extractor Logic (The "Engine" inside the document)
EXTRACTOR_LOGIC = r'''
def extract_payload():
    print(f"Self-Exploding SEDA Archive: {os.path.basename(__file__)}")
    print("   Extracting files...")
    
    for filepath, content in PAYLOAD.items():
        # Determine destination
        dest_path = os.path.join(os.getcwd(), filepath)
        directory = os.path.dirname(dest_path)
        
        # Create directories
        if directory:
            os.makedirs(directory, exist_ok=True)
        
        # Write file
        try:
            # If content is bytes (binary), write directly
            if isinstance(content, bytes):
                with open(dest_path, 'wb') as f:
                    f.write(content)
            # If content is string (text or base64 representation), handle accordingly
            elif isinstance(content, str):
                 # Heuristic: If it looks like a text file, try writing as text
                 # Otherwise try decoding base64
                 try:
                     # Try treating as base64 first for known binary extensions
                     if filepath.endswith(('.png', '.jpg', '.ico', '.svg', '.pdf', '.zip', '.exe')):
                         with open(dest_path, 'wb') as f:
                            f.write(base64.b64decode(content))
                     else:
                         # Default to text
                         with open(dest_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                 except Exception:
                     # Fallback: write as raw text if decoding fails
                     with open(dest_path, 'w', encoding='utf-8') as f:
                        f.write(content)

            print(f"   [OK] Extracted: {filepath}")
        except Exception as e:
            print(f"   [ERROR] Error extracting {filepath}: {e}")

    print("\nExplosion complete! All files extracted.")

if __name__ == "__main__":
    extract_payload()
'''

IGNORE_DIRS = {
    'node_modules', '__pycache__', '.git', 'dist', 'build', 
    '.DS_Store', '.idea', '.vscode', 'coverage'
}

IGNORE_EXTENSIONS = {
    '.pyc', '.log', '.seda', '.exe', '.dll', '.so', '.dylib', '.zip'
}

def is_binary(file_path):
    """Check if file is binary."""
    try:
        with open(file_path, 'r', encoding='utf-8') as check_file:
            check_file.read()
            return False
    except:
        return True

def create_bootstrap_seda(source_dir, output_filename):
    source_dir = os.path.abspath(source_dir)
    
    if not os.path.exists(source_dir):
        print(f"Error: Source directory '{source_dir}' does not exist.")
        return

    print(f"Preparing self-exploding document from '{os.path.basename(source_dir)}'...")

    file_data = {}
    file_list_md = ""

    for root, dirs, files in os.walk(source_dir):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            if any(file.endswith(ext) for ext in IGNORE_EXTENSIONS):
                continue
            
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, source_dir).replace('\\', '/')
            
            file_list_md += f"- `{rel_path}`\n"

            try:
                if is_binary(full_path):
                    with open(full_path, "rb") as f:
                        encoded = base64.b64encode(f.read()).decode('utf-8')
                        file_data[rel_path] = encoded
                else:
                    with open(full_path, "r", encoding="utf-8") as f:
                        file_data[rel_path] = f.read()
                print(f"   + Added: {rel_path}")
            except Exception as e:
                print(f"   ! Skipping {rel_path}: {e}")

    # Assemble the document
    with open(output_filename, "w", encoding="utf-8") as out:
        # 1. Write the Header (Shebang + Markdown Doc)
        header = BOOTSTRAP_HEADER.format(
            filename=os.path.basename(output_filename),
            file_list=file_list_md
        )
        out.write(header)
        
        # 2. Write the Payload Dictionary
        out.write("\n# Payload Data\nPAYLOAD = {\n")
        for path, content in file_data.items():
            # Use repr() for safe string representation
            out.write(f"    '{path}': {repr(content)},\n")
        out.write("}\n")
        
        # 3. Write the Extractor Logic
        out.write(EXTRACTOR_LOGIC)

    # Make it executable (Unix/Linux/Mac)
    try:
        mode = os.stat(output_filename).st_mode
        os.chmod(output_filename, mode | 0o111)
    except:
        pass

    print(f"\nSelf-Exploding Document created: {output_filename}")
    print(f"   Try running it: ./ {output_filename}  (or python {output_filename})")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python seda_bootstrap.py <directory_to_pack> [output_filename.py]")
    else:
        target_dir = sys.argv[1]
        output_name = sys.argv[2] if len(sys.argv) > 2 else f"{os.path.basename(os.path.abspath(target_dir))}_installer.py"
        create_bootstrap_seda(target_dir, output_name)
