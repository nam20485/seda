# 📦 SEDA: Self-Extracting Document Archive

**Version:** 1.3
**Status:** Active (Standardized Extensions)

## What is SEDA?
SEDA is a protocol for packaging files, directory structures, and metadata into a single, executable Python script.

## The Extension Mandate (v1.3)
To ensure reliability and user expectation, the SEDA toolset now mandates subtype extensions. Users provide a **Base Name**, and the tool determines the **Functionality Extension** based on the contents:

* **`NAME.seda`** (Type 0): Standard archive. Unpacks files only.
* **`NAME.commit.seda`** (Type 5): Contextual patch. Unpacks files + extracts commit message.
* **`NAME.construct.seda`** (Type 1): Active installer. Unpacks files + runs setup commands.
* **`NAME.smartpatch.seda`** (Type 1+5): Validated patch. Unpacks + Validates + Commits.

## The Tools

### `seda_packer.py`
**Usage:**
```bash
# User only provides the name 'patch-v1'. 
# Tool appends '.commit.seda' automatically because --docstring is present.
python tools/seda_packer.py ./src patch-v1 --docstring "Fix bugs"
```

### `seda_bootstrap.py`
A lightweight script to generate SEDA files if the packer is not available.
