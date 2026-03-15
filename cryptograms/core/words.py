"""Utilities for handling English words and dictionary lookups.

Recommended libraries:
1. NLTK (Natural Language Toolkit) - Comprehensive word lists and corpora
2. wordfreq - Simple word frequency lookups from multiple sources

Install with: pip install nltk wordfreq
"""
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
        self.words = self.load_english_words(min_length)
        self.frequencies = self.load_word_frequencies()
        self.bigram_frequencies = self.load_bigram_frequencies()
        self.trigram_frequencies = self.load_trigram_frequencies()

    def is_valid_word(self, word: str) -> bool:
        """Check if a word is valid English."""
        return word.lower() in self.words

    def get_frequency(self, word: str) -> float:
        """Get the frequency of a word, or 0.0 if unknown."""
        return self.frequencies.get(word.upper(), 0.0)

    # Install: pip install wordfreq

    @staticmethod
    def load_english_words(min_length: int = 1) -> set[str]:

        # 'en' includes contractions and is based on web text
        freq_dict = get_frequency_dict('en', wordlist='best')

        words = {word.upper() for word, freq in freq_dict.items() if len(word) >= min_length and freq > 1e-7}

        if 'A' not in words:
            words.add('A')
        if 'I' not in words:
            words.add('I')

        return words

    def load_word_frequencies(self) -> dict[str, float]:
        """
        Load English word frequencies.

        Uses the 'wordfreq' library which provides word frequencies from various sources.
        Returns frequencies as probabilities (sum to ~1.0).

        Returns:
            Dictionary mapping words to their frequency scores
        """

        # Load common words with their frequencies
        common_words = self.load_english_words()
        frequencies = {}

        for word in common_words:
            freq = word_frequency(word, 'en')
            if freq > 0:
                frequencies[word] = freq

        return frequencies

    @staticmethod
    def get_word_frequency(word: str) -> float:
        """
        Get the frequency of a specific word.

        Args:
            word: The word to look up

        Returns:
            Frequency score (0.0 to 1.0), or 0.0 if word is unknown
        """
        return word_frequency(word.lower(), 'en')

    @staticmethod
    def load_bigram_frequencies() -> dict[tuple[str, str], int]:
        # Get bigrams from Brown corpus
        all_bigrams = list(bigrams([w.upper() for w in brown.words()]))
        bigram_freq = Counter(all_bigrams)
        return bigram_freq

    def get_bigram_frequency(self, first: str, second: str) -> int:
        return self.bigram_frequencies.get((first.upper(), second.upper()), 0)

    def load_trigram_frequencies(self) -> dict[tuple[str, str, str], int]:
        # Get trigrams from Brown corpus
        all_trigrams = list(trigrams([w.upper() for w in brown.words()]))
        trigram_freq = Counter(all_trigrams)
        return trigram_freq

    def get_trigram_frequency(self, first: str, second: str, third: str) -> int:
        return self.trigram_frequencies.get((first.upper(), second.upper(), third.upper()), 0)

