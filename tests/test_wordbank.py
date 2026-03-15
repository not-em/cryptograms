"""Test the WordBank class."""

import unittest
from cryptograms.core.words import WordBank


class TestWordBank(unittest.TestCase):
    """Test the WordBank class functionality."""

    @classmethod
    def setUpClass(cls):
        """Set up a WordBank instance for all tests."""
        cls.bank = WordBank(min_length=1)

    def test_initialization(self):
        """Test WordBank initializes correctly."""
        bank = WordBank(min_length=2)
        self.assertEqual(bank.min_length, 2)
        self.assertIsNone(bank._words)
        self.assertIsNone(bank._frequencies)

    def test_lazy_loading(self):
        """Test that words are loaded lazily."""
        bank = WordBank()
        # Words should load on first access
        words = bank.words
        self.assertIsNotNone(words)
        self.assertIsInstance(words, set)
        self.assertGreater(len(words), 100)

    def test_get_words_by_length(self):
        """Test getting words by specific length."""
        # Single letter words
        one_letter = self.bank.get_words_by_length(1)
        self.assertIn('a', one_letter)
        self.assertIn('i', one_letter)

        # Two letter words
        two_letter = self.bank.get_words_by_length(2)
        self.assertGreater(len(two_letter), 10)
        self.assertIn('is', two_letter)
        self.assertIn('it', two_letter)

    def test_get_frequency(self):
        """Test word frequency lookup."""
        # Common words should have higher frequency
        freq_the = self.bank.get_frequency('the')
        freq_hello = self.bank.get_frequency('hello')
        freq_rare = self.bank.get_frequency('zymurgy')

        self.assertGreater(freq_the, freq_hello)
        self.assertGreater(freq_hello, freq_rare)

    def test_is_valid_word(self):
        """Test word validation."""
        self.assertTrue(self.bank.is_valid_word('hello'))
        self.assertTrue(self.bank.is_valid_word('HELLO'))  # Case insensitive
        self.assertTrue(self.bank.is_valid_word('world'))
        self.assertFalse(self.bank.is_valid_word('xyz123'))
        self.assertFalse(self.bank.is_valid_word('asdfgh'))

    def test_get_words_by_length_sorted(self):
        """Test getting sorted words by length."""
        sorted_words = self.bank.get_words_by_length_sorted(3, limit=10)

        # Should return 10 words
        self.assertEqual(len(sorted_words), 10)

        # Should be sorted by frequency (descending)
        freqs = [self.bank.get_frequency(w) for w in sorted_words]
        self.assertEqual(freqs, sorted(freqs, reverse=True))

    def test_get_simple_words(self):
        """Test getting simple words."""
        simple = self.bank.get_simple_words()

        # Should include single letter words
        self.assertIn('a', simple)
        self.assertIn('i', simple)

        # Should have some two-letter words
        self.assertGreater(len(simple), 5)

    def test_get_words_with_apostrophes(self):
        """Test getting words with apostrophes."""
        apostrophe_words = self.bank.get_words_with_apostrophes()

        # Should find some words
        self.assertGreater(len(apostrophe_words), 0)

        # All should contain apostrophe
        for word in apostrophe_words:
            self.assertIn("'", word)

    def test_cache_persistence(self):
        """Test that caching works."""
        # Access words twice
        words1 = self.bank.words
        words2 = self.bank.words

        # Should be the same object (cached)
        self.assertIs(words1, words2)

    def test_clear_cache(self):
        """Test cache clearing."""
        # Load some data
        _ = self.bank.words
        _ = self.bank.frequencies

        # Clear cache
        self.bank.clear_cache()

        # Should be None again
        self.assertIsNone(self.bank._words)
        self.assertIsNone(self.bank._frequencies)


if __name__ == '__main__':
    unittest.main()
