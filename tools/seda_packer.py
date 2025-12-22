import os
import sys
import argparse
import base64
import re

# Defaults
DEFAULT_IGNORE_DIRS = {'node_modules', '__pycache__', '.git', 'dist', 'build', '.DS_Store'}
DEFAULT_IGNORE_EXTENSIONS = {'.pyc', '.log', '.seda', '.exe', '.dll', '.so', '.dylib'}

EXTRACTOR_TEMPLATE = r'''
import os
import sys
import base64
import re
import subprocess

def extract_payload():
    current_file = os.path.basename(__file__)
    print(f"📦 Unpacking SEDA Archive: {current_file}...")
    
    # Context Extraction (Type 5/1+5)
    if any(current_file.endswith(ext) for ext in ['.commit.seda', '.smartpatch.seda']):
        try:
            with open(__file__, 'r', encoding='utf-8') as f:
                content = f.read()
                match = re.search(r'"""(.*?)"""', content, re.DOTALL)
                if match:
                    msg = "\n".join([l for l in match.group(1).strip().splitlines() if not l.startswith("#!")]).strip()
                    with open("commit_msg.txt", "w", encoding="utf-8") as msg_file:
                        msg_file.write(msg)
                    print("   📝 Context extracted to 'commit_msg.txt'")
        except: pass

    # Extraction Loop
    for filepath, content in project_files.items():
        dest_path = os.path.join(os.getcwd(), filepath)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        try:
            if isinstance(content, bytes):
                with open(dest_path, 'wb') as f: f.write(content)
            else:
                if filepath.endswith(('.png', '.jpg', '.ico', '.svg', '.pdf')):
                     with open(dest_path, 'wb') as f: f.write(base64.b64decode(content))
                else:
                    with open(dest_path, 'w', encoding='utf-8') as f: f.write(content)
            print(f"   ✅ Extracted: {filepath}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

    # Post-Install (Type 1/1+5)
    if 'POST_INSTALL' in globals():
        print("\n⚙️  Running Pipeline...")
        cmd = POST_INSTALL.get('nt', POST_INSTALL.get('universal')) if os.name == 'nt' else POST_INSTALL.get('posix', POST_INSTALL.get('universal'))
        if cmd:
            try:
                subprocess.run(cmd, shell=True, check=True)
                print("   ✅ Success.")
            except subprocess.CalledProcessError as e:
                print(f"   ❌ Failed (Code {e.returncode})")
                sys.exit(e.returncode)

if __name__ == "__main__":
    extract_payload()
'''

def generate_seda(source_dir, output_filename, docstring=None, post_install=None):
    # MANDATE EXTENSION LOGIC
    base_output = output_filename if output_filename else os.path.basename(os.path.abspath(source_dir))
    
    # Strip existing extensions to prevent "name.seda.commit.seda"
    for ext in ['.smartpatch.seda', '.construct.seda', '.commit.seda', '.seda', '.py']:
        if base_output.lower().endswith(ext):
            base_output = base_output[:-len(ext)]
            break

    # Determine functionality extension
    if docstring and post_install:
        final_ext = ".smartpatch.seda"
    elif docstring:
        final_ext = ".commit.seda"
    elif post_install:
        final_ext = ".construct.seda"
    else:
        final_ext = ".seda"
    
    output_name = base_output + final_ext
    print(f"🗄️  Packing into mandated format: {output_name}")

    file_data = {}
    for root, dirs, files in os.walk(source_dir):
        dirs[:] = [d for d in dirs if d not in DEFAULT_IGNORE_DIRS]
        for file in files:
            if any(file.endswith(ext) for ext in DEFAULT_IGNORE_EXTENSIONS): continue
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, source_dir).replace('\\', '/')
            try:
                with open(full_path, "r", encoding="utf-8") as f: file_data[rel_path] = f.read()
                print(f"   ➕ Added: {rel_path}")
            except:
                with open(full_path, "rb") as f: file_data[rel_path] = base64.b64encode(f.read()).decode('utf-8')
    
    with open(output_name, "w", encoding="utf-8") as out:
        out.write("#!/usr/bin/env python3\n")
        out.write(f'"""\n{docstring if docstring else "# SEDA Archive"}\n"""\n')
        out.write(f"# SEDA v1.3 Standardized Release\n\n")
        if post_install: out.write(f"POST_INSTALL = {repr(post_install)}\n\n")
        out.write("project_files = {\n")
        for path, content in file_data.items():
            if isinstance(content, str) and "'''" not in content:
                out.write(f"    '{path}': r'''{content}''',\n")
            else:
                out.write(f"    '{path}': {repr(content)},\n")
        out.write("}\n" + EXTRACTOR_TEMPLATE)
    
    os.chmod(output_name, 0o755)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source_dir")
    parser.add_argument("output_filename", nargs="?")
    parser.add_argument("--docstring")
    parser.add_argument("--post-install")
    args = parser.parse_args()
    
    post_map = None
    if args.post_install:
        if "win:" in args.post_install:
            post_map = {}
            for p in args.post_install.split(','):
                if p.startswith("win:"): post_map['nt'] = p[4:]
                if p.startswith("unix:"): post_map['posix'] = p[5:]
        else: post_map = {"universal": args.post_install}
        
    generate_seda(args.source_dir, args.output_filename, args.docstring, post_map)
