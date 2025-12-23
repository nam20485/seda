# Instructions for AI Agents (v1.5)

## 1. Extension Mandating
Follow the functional extension naming convention.

| Content | Extension | Type |
| :--- | :--- | :--- |
| Files only | `.seda` | 0 |
| Files + Message | `.commit.seda` | 5 |
| Files + Commands | `.construct.seda` | 1 |
| Validated Patch | `.smartpatch.seda` | 1+5 |
| Encrypted | `.vault.seda` | 2 |
| Polyglot Web | `.seda.html` | 3 |

## 2. Generating Type 2 (Vault)
To generate a Type 2 archive, use the `--vault` flag. The tool handles the encryption logic. Do not attempt to implement the encryption manually in the payload generation; rely on the tool.
