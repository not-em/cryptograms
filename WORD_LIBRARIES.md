# English Word Libraries Guide

## Recommended Libraries

### 1. **NLTK (Natural Language Toolkit** ⭐ BEST CHOICE
- **Installation**: `pip install nltk`
- **Pros**:
  - 236K+ words in the words corpus
  - Well-maintained and widely used
  - Includes multiple corpora (Brown, Gutenberg, etc.)
  - Built-in frequency distributions
  - Academic-grade quality
- **Cons**: 
  - Requires downloading data files (automatic in our implementation)
  - Can be slower for large operations
- **Perfect for**: Cryptogram solving, NLP tasks

### 2. **wordfreq** ⭐ BEST FOR FREQUENCIES
- **Installation**: `pip install wordfreq`
- **Pros**:
  - Excellent frequency data from multiple sources (Wikipedia, Twitter, subtitles)
  - Very fast lookups
  - Simple API: `word_frequency('hello', 'en')`
  - Frequencies normalized across languages
- **Cons**: 
  - Not a complete dictionary (focused on common words)
- **Perfect for**: Scoring solutions based on word commonality

### 3. **PyEnchant** (Alternative)
- **Installation**: `pip install pyenchant`
- **Pros**:
  - Spell-checking capabilities
  - Multiple language support
  - Good for validation
- **Cons**: 
  - Requires system libraries (hunspell/aspell)
  - More complex setup on Windows
  - No frequency data

## Our Implementation

The `words.py` file now uses:
- **NLTK** for comprehensive word lists (~236K words)
- **wordfreq** for word frequency lookups
- **Fallback system** if libraries aren't installed

## Installation

```bash
pip install nltk wordfreq
```

## Usage Examples

```python
from cryptograms.core.words import (
  load_english_words,
  get_word_frequency,
  is_valid_english_word
)

# Load all English words
words = load_english_words(min_length=3)
print(f"Loaded {len(words)} words")  # ~236,000 words

# Check word frequency
freq = get_word_frequency("hello")
print(f"'hello' frequency: {freq}")  # ~0.00017

# Validate a word
is_valid = is_valid_english_word("cryptogram")
print(f"Is 'cryptogram' valid? {is_valid}")  # True
```

## Data Quality Comparison

| Library | Word Count | Frequency Data | Quality | Speed |
|---------|-----------|----------------|---------|-------|
| NLTK | 236K+ | Via Brown corpus | Academic | Medium |
| wordfreq | ~500K | Multiple sources | Excellent | Fast |
| PyEnchant | ~100K | None | Good | Fast |

## Why NLTK + wordfreq?

1. **NLTK** provides comprehensive word lists - essential for validating decrypted text
2. **wordfreq** provides accurate frequency data - crucial for scoring solutions
3. Both are pure Python and easy to install
4. They complement each other perfectly

## First-Time Setup

When you first run the code, NLTK will automatically download its data:

```python
from cryptograms.core.words import load_english_words

words = load_english_words()  # Downloads NLTK data on first run
```

This creates a `~/nltk_data` directory with the word corpus (~5MB).
