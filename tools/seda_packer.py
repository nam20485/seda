import os
import sys
import argparse
import base64
import re
import getpass
import hashlib
import json

DEFAULT_IGNORE_DIRS = {'node_modules', '__pycache__', '.git', 'dist', 'build', '.DS_Store'}
DEFAULT_IGNORE_EXTENSIONS = {'.pyc', '.log', '.seda', '.exe', '.dll', '.so', '.dylib'}

# --- VAULT TEMPLATES ---
VAULT_EXTRACTOR_TEMPLATE = r'''
import os
import sys
import base64
import re
import subprocess
import getpass
import hashlib
import json
import itertools

def derive_key(password, salt, iterations=100000):
    return hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations)

def decrypt_payload(encrypted_blob, password):
    try:
        data = base64.b64decode(encrypted_blob)
        salt = data[:16]
        ciphertext = data[16:]
        
        key = derive_key(password, salt)
        
        # XOR Decryption (Simple stream cipher for dependency-free portability)
        decrypted = bytearray()
        for b, k in zip(ciphertext, itertools.cycle(key)):
            decrypted.append(b ^ k)
            
        return json.loads(decrypted.decode('utf-8'))
    except Exception:
        return None

def extract_payload():
    current_file = os.path.basename(__file__)
    print(f"🔒 Locked Archive: {current_file}")
    
    password = getpass.getpass("🔑 Enter Password: ")
    
    # Decrypt Payload
    # 'VAULT_BLOB' is injected by the packer
    project_files = decrypt_payload(VAULT_BLOB, password)
    
    if project_files is None:
        print("❌ Error: Invalid Password or Corrupted Archive.")
        sys.exit(1)
        
    print(f"🔓 Access Granted. Unpacking...")

    # --- STANDARD EXTRACTION LOGIC ---
    # Context Extraction (From decrypted payload if present in special key)
    if '__docstring__' in project_files:
        try:
            with open("commit_msg.txt", "w", encoding="utf-8") as msg_file:
                msg_file.write(project_files['__docstring__'])
            print("   📝 Context extracted to 'commit_msg.txt'")
            del project_files['__docstring__'] # Remove from file list
        except: pass

    # Extraction Loop
    for filepath, content in project_files.items():
        dest_path = os.path.join(os.getcwd(), filepath)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        try:
            if isinstance(content, str) and content.startswith('BASE64:'):
                 with open(dest_path, 'wb') as f: f.write(base64.b64decode(content[7:]))
            else:
                with open(dest_path, 'w', encoding='utf-8') as f: f.write(content)
            print(f"   ✅ Extracted: {filepath}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

    # Post-Install
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

# --- STANDARD TEMPLATES ---
# (Existing template for non-vault archives)
STANDARD_EXTRACTOR_TEMPLATE = r'''
import os
import sys
import base64
import re
import subprocess

def extract_payload():
    current_file = os.path.basename(__file__)
    print(f"📦 Unpacking SEDA Archive: {current_file}...")
    
    # Context Extraction
    if any(current_file.endswith(ext) for ext in ['.commit.seda', '.smartpatch.seda']):
        try:
            with open(__file__, 'r', encoding='utf-8') as f:
                content = f.read()
                match = re.search(r'"""(.*?)"""', content, re.DOTALL)
                if match:
                    clean_msg = re.sub(r'<[^>]+>', '', match.group(1)).strip()
                    clean_msg = "\n".join([l for l in clean_msg.splitlines() if not l.startswith("#!") and not l.strip() == ""]).strip()
                    with open("commit_msg.txt", "w", encoding="utf-8") as msg_file:
                        msg_file.write(clean_msg)
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

    # Post-Install
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

def encrypt_payload(payload_dict, password):
    import itertools
    # Convert payload to JSON bytes
    # Handle mixed types (bytes/str)
    clean_payload = {}
    for k, v in payload_dict.items():
        if isinstance(v, bytes):
            clean_payload[k] = "BASE64:" + v.decode('utf-8') # Packer stored b64 as bytes in dict
        else:
            clean_payload[k] = v
            
    plaintext = json.dumps(clean_payload).encode('utf-8')
    
    # Generate Salt
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    
    # XOR Encryption
    ciphertext = bytearray()
    for b, k in zip(plaintext, itertools.cycle(key)):
        ciphertext.append(b ^ k)
        
    # Return Salt + Ciphertext (Base64 encoded for text file safety)
    return base64.b64encode(salt + ciphertext).decode('utf-8')

def generate_seda(source_dir, output_filename, docstring=None, post_install=None, is_web=False, is_vault=False):
    base_output = output_filename if output_filename else os.path.basename(os.path.abspath(source_dir))
    
    # Strip extensions
    for ext in ['.smartpatch.seda', '.construct.seda', '.commit.seda', '.seda.html', '.vault.seda', '.seda', '.py']:
        if base_output.lower().endswith(ext):
            base_output = base_output[:-len(ext)]
            break

    # Determine Extension
    if is_vault:
        final_ext = ".vault.seda"
    elif is_web:
        final_ext = ".seda.html"
    elif docstring and post_install:
        final_ext = ".smartpatch.seda"
    elif docstring:
        final_ext = ".commit.seda"
    elif post_install:
        final_ext = ".construct.seda"
    else:
        final_ext = ".seda"
    
    output_name = base_output + final_ext
    print(f"🗄️  Packing: {output_name}")

    if is_vault:
        password = getpass.getpass("🔑 Enter Password for Vault: ")
        confirm = getpass.getpass("🔑 Confirm Password: ")
        if password != confirm:
            print("❌ Passwords do not match.")
            sys.exit(1)

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
                with open(full_path, "rb") as f: 
                    # Store as string for consistency in vault logic
                    file_data[rel_path] = "BASE64:" + base64.b64encode(f.read()).decode('utf-8')
    
    # Inject docstring into payload for Vaults (so it's encrypted too)
    if is_vault and docstring:
        file_data['__docstring__'] = docstring

    with open(output_name, "w", encoding="utf-8") as out:
        if is_web:
            # Type 3 Polyglot Header (Not supported for Vault yet)
            out.write("<!--\n")
            out.write('"""\n')
        
        out.write("#!/usr/bin/env python3\n")
        
        # Docstring (Public for standard, hidden for Vault)
        if docstring and not is_vault:
            out.write('"""\n' + docstring + '\n"""\n')
        else:
            out.write('"""\n# SEDA Archive\n"""\n')
            
        out.write(f"# Generated by SEDA Packer v1.5\n\n")
        if post_install: out.write(f"POST_INSTALL = {repr(post_install)}\n\n")
        
        if is_vault:
            encrypted_blob = encrypt_payload(file_data, password)
            out.write(f"VAULT_BLOB = {repr(encrypted_blob)}\n")
            out.write(VAULT_EXTRACTOR_TEMPLATE)
        else:
            out.write("project_files = {\n")
            for path, content in file_data.items():
                # Handle base64 prefix from reading loop
                val_to_write = content
                if isinstance(content, str) and content.startswith("BASE64:"):
                     # Decode back to bytes for standard packer logic compatibility or keep as b64 str
                     # v1.5 Standard packer expects raw bytes or str.
                     # Reverting the prefix for standard:
                     val_to_write = base64.b64decode(content[7:])
                
                if isinstance(val_to_write, str) and "'''" not in val_to_write:
                    out.write(f"    '{path}': r'''{val_to_write}''',\n")
                else:
                    out.write(f"    '{path}': {repr(val_to_write)},\n")
            out.write("}\n")
            out.write(STANDARD_EXTRACTOR_TEMPLATE)
        
        if is_web:
            out.write('\n"""\n-->')
    
    try: os.chmod(output_name, 0o755)
    except: pass

    print(f"\n🎉 Created: {output_name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source_dir")
    parser.add_argument("output_filename", nargs="?")
    parser.add_argument("--docstring")
    parser.add_argument("--post-install")
    parser.add_argument("--web", action="store_true", help="Generate Type 3 Polyglot")
    parser.add_argument("--vault", action="store_true", help="Generate Type 2 Encrypted Vault")
    args = parser.parse_args()
    
    post_map = None
    if args.post_install:
        if "win:" in args.post_install:
            post_map = {}
            for p in args.post_install.split(','):
                if p.startswith("win:"): post_map['nt'] = p[4:]
                if p.startswith("unix:"): post_map['posix'] = p[5:]
        else: post_map = {"universal": args.post_install}
        
    generate_seda(args.source_dir, args.output_filename, args.docstring, post_map, args.web, args.vault)
