# cryptograms

[![PyPI version](https://img.shields.io/pypi/v/cryptograms)](https://pypi.org/project/cryptograms/)
[![Python versions](https://img.shields.io/pypi/pyversions/cryptograms)](https://pypi.org/project/cryptograms/)
[![License](https://img.shields.io/pypi/l/cryptograms)](https://github.com/not-em/cryptograms/blob/main/LICENSE)

A Python package for solving simple substitution ciphers using pattern matching and constraint propagation.

## Installation

```bash
pip install cryptograms
```

## Usage

### Python API

```python
from cryptograms import solve_cryptogram, encrypt_cryptogram

# Solve a cipher
solution = solve_cryptogram("Ebiil tloia")
print(solution.plaintext)    # Hello world
print(solution.confidence)   # 0.95

# Encrypt plaintext (useful for generating puzzles)
ciphertext = encrypt_cryptogram("Hello world")
print(ciphertext)            # e.g. Ebiil tloia
```

### Command line

```bash
# Decrypt — accepts a string or a file path
cryptograms decrypt "Ebiil tloia"
cryptograms decrypt puzzle.txt

# Encrypt
cryptograms encrypt "Hello world"
cryptograms encrypt "Hello world" --seed 42   # reproducible output
```

## How it works

The solver uses word-pattern matching and constraint propagation rather than frequency analysis:

1. Each cipher word is encoded as a numeric pattern — `"KHOOR"` → `"12334"`
2. Candidate plaintext words are looked up by pattern from a ~200k-word frequency-weighted dictionary
3. `LetterConstraints` tracks which plaintext letters each cipher letter can still map to, and propagates locks globally when a mapping is confirmed
4. Candidates and constraints are narrowed iteratively until every cipher word resolves to one plaintext word
5. When stuck, the solver uses NLTK Brown corpus bigram/trigram frequencies to pick the most contextually likely candidate and continues

## Data

Word frequencies from [wordfreq](https://github.com/rspeer/wordfreq). Bigram and trigram context from the [NLTK](https://www.nltk.org/) Brown corpus, downloaded automatically on first use.

## Web interface

A self-hostable web interface is available in the [repository](https://github.com/not-em/cryptograms). Run it with:

```bash
pip install cryptograms[web]
uvicorn cryptograms.api:app
```
