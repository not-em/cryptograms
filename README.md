# Cryptogram Solver

A Python package for solving simple substitution cryptograms using frequency analysis and pattern matching.

## Structure

```
cryptograms/
├── cryptograms/              # Main package
│   ├── core/                 # Core solving logic
│   │   ├── models.py         # Data structures (Puzzle, Solution, CipherMapping)
│   │   ├── solver.py         # Main solver implementation
│   │   ├── parser.py         # Text parsing and preprocessing
│   │   ├── frequency.py      # Letter frequency analysis
│   │   ├── scoring.py        # Solution quality scoring
│   │   ├── constraints.py    # Constraint checking and propagation
│   │   └── exceptions.py     # Custom exceptions
│   ├── cli/                  # Command-line interface
│   │   └── main.py          # CLI entry point
│   ├── resources/            # Data files
│   │   └── english_freq.json # English language statistics
│   └── service.py            # High-level API
├── tests/                    # Unit tests
│   └── test_solver.py
├── main.py                   # Application entry point
└── requirements.txt          # Dependencies
```

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### As a Python package

```python
from cryptograms import solve_cryptogram

solution = solve_cryptogram("KHOOR ZRUOG")
print(solution.plaintext)
print(solution.format_summary())
```

### Command-line interface

```bash
# Solve text directly
python -m cryptograms.cli.main text "KHOOR ZRUOG"

# Solve from a file
python -m cryptograms.cli.main file puzzle.txt

# With a clue
python -m cryptograms.cli.main text "KHOOR ZRUOG" --clue "Caesar cipher"
```

## Algorithm

The solver uses a multi-step approach:

1. **Frequency Analysis**: Compute letter frequencies in the ciphertext
2. **Initial Mapping**: Match cipher frequencies to known English frequencies
3. **Constraint Application**: Apply any user-provided letter mappings
4. **Scoring**: Evaluate solution quality using dictionary matching and language patterns
5. **Refinement**: (TODO) Iteratively improve using hill-climbing or simulated annealing

## Development

Run tests:
```bash
python -m pytest tests/
```

## TODO

- [ ] Implement dictionary-based word matching
- [ ] Add bigram/trigram analysis
- [ ] Implement iterative refinement (hill-climbing)
- [ ] Add support for pattern-based solving
- [ ] Create a web interface
- [ ] Add more comprehensive tests
