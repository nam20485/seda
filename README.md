# 📦 SEDA: Self-Extracting Document Archive

**Version:** 1.5
**Status:** Active (Vault Support)

## What is SEDA?
SEDA is a protocol for packaging files, directory structures, and metadata into a single, executable Python script.

## Subtypes & Extensions

| Type | Extension | Capability |
| :--- | :--- | :--- |
| **0** | `.seda` | **Core:** Unpacks files to disk. |
| **5** | `.commit.seda` | **Commit:** Unpacks + extracts git commit message. |
| **1** | `.construct.seda` | **Construct:** Unpacks + runs setup commands. |
| **1+5**| `.smartpatch.seda`| **SmartPatch:** Unpacks + Validates + Commits. |
| **3** | `.seda.html` | **Web:** Polyglot. Runs in Python OR Browser. |
| **2** | `.vault.seda` | **Vault:** Encrypted. Requires password. |

## The Tools

### `seda_packer.py`
**Usage:**

**Create a Vault Archive (Type 2)**
```bash
python tools/seda_packer.py ./secrets --vault
# Prompts for password...
# Output: secrets.vault.seda
```
When the user runs `python secrets.vault.seda`, they will be prompted for the password before extraction begins.
