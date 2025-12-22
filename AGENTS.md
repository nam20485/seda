# Instructions for AI Agents (v1.3)

## 1. Extension Mandating
When generating SEDA files, you must follow the functional extension naming convention. The extension is not aesthetic; it is a promise of behavior.

| Content | Extension | Type |
| :--- | :--- | :--- |
| Files only | `.seda` | 0 |
| Files + Commit Message | `.commit.seda` | 5 |
| Files + Commands | `.construct.seda` | 1 |
| Files + Message + Commands | `.smartpatch.seda` | 1+5 |

## 2. Syntax Safety (The Sentinel Strategy)
**Rule:** If a source file contains triple quotes (`'''`), replace them with `'''` in the string literal, and append `.replace("'''", "'''")`.
