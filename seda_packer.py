import os
import sys
import argparse
import base64

# Configuration: Folders to always ignore (Defaults)
DEFAULT_IGNORE_DIRS = {
    'node_modules', '__pycache__', '.git', 'dist', 'build', 
    '.DS_Store', '.idea', '.vscode', 'coverage'
}

# Configuration: File extensions to always ignore (Defaults)
DEFAULT_IGNORE_EXTENSIONS = {
    '.pyc', '.log', '.seda', '.exe', '.dll', '.so', '.dylib'
}

# The template for the extractor logic
EXTRACTOR_TEMPLATE = r'''
import os
import sys
import base64
import re

def extract_payload():
    current_file = os.path.basename(__file__)
    print(f"📦 Unpacking SEDA Archive: {current_file}...")
    
    # --- FEATURE: SEDA-Commit Message Extraction ---
    # If the file detects it is a 'commit.seda', it tries to extract its own header docstring.
    if current_file.endswith('.commit.seda') or current_file.endswith('.commit.py'):
        try:
            with open(__file__, 'r', encoding='utf-8') as f:
                content = f.read()
                # Extract content between the first set of triple quotes
                match = re.search(r'"""(.*?)"""', content, re.DOTALL)
                if match:
                    msg = match.group(1).strip()
                    # Remove the shebang if it was caught inside (though unlikely with regex)
                    lines = [l for l in msg.splitlines() if not l.startswith("#!")]
                    clean_msg = "\n".join(lines).strip()
                    
                    with open("commit_msg.txt", "w", encoding="utf-8") as msg_file:
                        msg_file.write(clean_msg)
                    print("   📝 SEDA-Commit detected: extracted 'commit_msg.txt'")
        except Exception as e:
            print(f"   ⚠️ Could not extract commit message: {e}")
    # -----------------------------------------------

    for filepath, content in project_files.items():
        dest_path = os.path.join(os.getcwd(), filepath)
        directory = os.path.dirname(dest_path)
        
        if directory:
            os.makedirs(directory, exist_ok=True)
        
        try:
            if isinstance(content, bytes):
                with open(dest_path, 'wb') as f:
                    f.write(content)
            else:
                if filepath.endswith(('.png', '.jpg', '.ico', '.svg', '.pdf')):
                     with open(dest_path, 'wb') as f:
                        f.write(base64.b64decode(content))
                else:
                    with open(dest_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                        
            print(f"   ✅ Extracted: {filepath}")
        except Exception as e:
            print(f"   ❌ Error extracting {filepath}: {e}")

    print("\n✨ Extraction complete! ✨")

if __name__ == "__main__":
    extract_payload()
'''

def is_binary(file_path):
    """Simple check to see if a file is binary text."""
    try:
        with open(file_path, 'tr') as check_file:
            check_file.read()
            return False
    except:
        return True

def generate_seda(source_dir, output_filename, recursive_pack_seda=False, extra_ignore_dirs=None, extra_ignore_exts=None, docstring=None):
    source_dir = os.path.abspath(source_dir)
    
    # Setup ignore sets
    ignore_dirs = set(DEFAULT_IGNORE_DIRS)
    if extra_ignore_dirs:
        ignore_dirs.update(extra_ignore_dirs)
        
    ignore_exts = set(DEFAULT_IGNORE_EXTENSIONS)
    if extra_ignore_exts:
        ignore_exts.update(extra_ignore_exts)
        
    # Handle recursion flag (Principle of Least Surprise: explicit opt-in)
    if recursive_pack_seda and '.seda' in ignore_exts:
        ignore_exts.remove('.seda')
    
    if not os.path.exists(source_dir):
        print(f"Error: Source directory '{source_dir}' does not exist.")
        return

    print(f"🗄️  Packing '{os.path.basename(source_dir)}' into '{output_filename}'...")
    print(f"   ℹ️  Recursive SEDA Packing: {'ENABLED' if recursive_pack_seda else 'DISABLED'}")
    
    if docstring:
        print("   📝 Attaching custom commit message/docstring.")

    file_data = {}

    for root, dirs, files in os.walk(source_dir):
        # Filter ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
        for file in files:
            # Check extensions
            if any(file.endswith(ext) for ext in ignore_exts):
                continue
                
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, source_dir)
            rel_path = rel_path.replace('\\', '/')

            try:
                if is_binary(full_path):
                    with open(full_path, "rb") as f:
                        encoded = base64.b64encode(f.read()).decode('utf-8')
                        file_data[rel_path] = encoded
                else:
                    with open(full_path, "r", encoding="utf-8") as f:
                        file_data[rel_path] = f.read()
                    
                print(f"   ➕ Added: {rel_path}")
            except Exception as e:
                print(f"   ⚠️ Skipping {rel_path}: {e}")

    with open(output_filename, "w", encoding="utf-8") as out:
        out.write("#!/usr/bin/env python3\n")
        
        # WRITE THE DOCSTRING / COMMIT MESSAGE
        if docstring:
            out.write('"""\n')
            out.write(docstring)
            out.write('\n"""\n')
        else:
            out.write('"""\n# SEDA Archive\n"""\n')
            
        out.write("# Generated by SEDA Packer v1.1\n\n")
        out.write("project_files = {\n")
        
        for path, content in file_data.items():
            # SENTINEL CHECK: Guard against delimiter collision
            if isinstance(content, str) and "'''" not in content:
                 out.write(f"    '{path}': r'''{content}''',\n")
            else:
                 print(f"   🛡️  Sentinel Active: {path} contains delimiters. Using safe repr().")
                 out.write(f"    '{path}': {repr(content)},\n")
                 
        out.write("}\n")
        out.write(EXTRACTOR_TEMPLATE)

    print(f"\n🎉 SEDA archive created: {output_filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SEDA Packer Tool v1.1")
    parser.add_argument("source_dir", help="Directory to pack")
    parser.add_argument("output_filename", nargs="?", help="Output filename (default: <dirname>.seda)")
    
    # Flags
    parser.add_argument("--recursive-pack-seda", action="store_true", help="Allow packing of .seda files")
    parser.add_argument("--ignore-dirs", help="Comma-separated list of additional directories to ignore")
    parser.add_argument("--ignore-exts", help="Comma-separated list of additional extensions to ignore")
    
    # New Commit SEDA Flags
    parser.add_argument("--docstring", help="Text to use as the file docstring (commit message)")
    parser.add_argument("--docstring-file", help="File containing text to use as the docstring")

    args = parser.parse_args()
    
    # Process defaults
    target_dir = args.source_dir
    output_name = args.output_filename if args.output_filename else f"{os.path.basename(os.path.abspath(target_dir))}.seda"
    if not output_name.endswith('.seda') and not output_name.endswith('.py'):
        output_name += '.seda'
        
    # Process Lists
    extra_dirs = args.ignore_dirs.split(',') if args.ignore_dirs else []
    extra_exts = args.ignore_exts.split(',') if args.ignore_exts else []
    
    # Process Docstring
    doc_text = args.docstring
    if args.docstring_file:
        try:
            with open(args.docstring_file, 'r', encoding='utf-8') as f:
                doc_text = f.read()
        except Exception as e:
            print(f"Error reading docstring file: {e}")
            sys.exit(1)

    generate_seda(target_dir, output_name, args.recursive_pack_seda, extra_dirs, extra_exts, doc_text)
