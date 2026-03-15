"""Utilities for handling English words and dictionary lookups."""

from __future__ import annotations

import nltk
from nltk import bigrams, trigrams

try:
    nltk.data.find('corpora/brown')
except LookupError:
    nltk.download('brown')
from nltk.corpus import brown
from wordfreq import get_frequency_dict, word_frequency
from collections import Counter


class WordBank:
    """Manages a collection of English words and their frequencies."""

    def __init__(self, min_length: int = 1):
        self.min_length = min_length
        self._words: set[str] | None = None
        self._frequencies: dict[str, float] | None = None
        self._bigram_frequencies: dict[tuple[str, str], int] | None = None
        self._trigram_frequencies: dict[tuple[str, str, str], int] | None = None

    # ------------------------------------------------------------------
    # Lazy-loaded properties
    # ------------------------------------------------------------------

    @property
    def words(self) -> set[str]:
        if self._words is None:
            self._words = self._load_english_words()
        return self._words

    @property
    def frequencies(self) -> dict[str, float]:
        if self._frequencies is None:
            self._frequencies = self._load_word_frequencies()
        return self._frequencies

    @property
    def bigram_frequencies(self) -> dict[tuple[str, str], int]:
        if self._bigram_frequencies is None:
            self._bigram_frequencies = self._load_bigram_frequencies()
        return self._bigram_frequencies

    @property
    def trigram_frequencies(self) -> dict[tuple[str, str, str], int]:
        if self._trigram_frequencies is None:
            self._trigram_frequencies = self._load_trigram_frequencies()
        return self._trigram_frequencies

    def clear_cache(self) -> None:
        """Reset all cached data; next access will reload from source."""
        self._words = None
        self._frequencies = None
        self._bigram_frequencies = None
        self._trigram_frequencies = None

    # ------------------------------------------------------------------
    # Word queries
    # ------------------------------------------------------------------

    def is_valid_word(self, word: str) -> bool:
        """Check if a word is valid English (case-insensitive)."""
        return word.lower() in self.words

    def get_frequency(self, word: str) -> float:
        """Get the frequency of a word, or 0.0 if unknown."""
        return self.frequencies.get(word.lower(), 0.0)

    def get_words_by_length(self, n: int) -> set[str]:
        """Return all words of exactly length n (lowercase)."""
        return {w for w in self.words if len(w) == n}

    def get_words_by_length_sorted(self, n: int, limit: int | None = None) -> list[str]:
        """Return words of length n sorted by frequency descending."""
        words = sorted(
            self.get_words_by_length(n),
            key=lambda w: self.get_frequency(w),
            reverse=True,
        )
        return words[:limit] if limit is not None else words

    def get_simple_words(self) -> list[str]:
        """Return 1- and 2-letter words sorted by frequency descending."""
        simple = {w for w in self.words if len(w) <= 2}
        return sorted(simple, key=lambda w: self.get_frequency(w), reverse=True)

    def get_words_with_apostrophes(self) -> list[str]:
        """Return all words that contain an apostrophe."""
        return [w for w in self.words if "'" in w]

    # ------------------------------------------------------------------
    # Corpus frequency queries
    # ------------------------------------------------------------------

    @staticmethod
    def get_word_frequency(word: str) -> float:
        """Direct wordfreq lookup (bypasses the cached frequency dict)."""
        return word_frequency(word.lower(), 'en')

    def get_bigram_frequency(self, first: str, second: str) -> int:
        return self.bigram_frequencies.get((first.upper(), second.upper()), 0)

    def get_trigram_frequency(self, first: str, second: str, third: str) -> int:
        return self.trigram_frequencies.get((first.upper(), second.upper(), third.upper()), 0)

    # ------------------------------------------------------------------
    # Private loaders
    # ------------------------------------------------------------------

    def _load_english_words(self) -> set[str]:
        freq_dict = get_frequency_dict('en', wordlist='best')
        words = {
            word.lower()
            for word, freq in freq_dict.items()
            if len(word) >= self.min_length and freq > 1e-7
        }
        words.add('a')
        words.add('i')
        return words

    def _load_word_frequencies(self) -> dict[str, float]:
        frequencies = {}
        for word in self.words:  # reuses the cached word set
            freq = word_frequency(word, 'en')
            if freq > 0:
                frequencies[word] = freq
        return frequencies

    @staticmethod
    def _load_bigram_frequencies() -> dict[tuple[str, str], int]:
        all_bigrams = list(bigrams([w.upper() for w in brown.words()]))
        return Counter(all_bigrams)

    @staticmethod
    def _load_trigram_frequencies() -> dict[tuple[str, str, str], int]:
        all_trigrams = list(trigrams([w.upper() for w in brown.words()]))
        return Counter(all_trigrams)
