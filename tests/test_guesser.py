"""Tests for Guesser — unified best_guess() and scoring methods."""

import unittest
from unittest.mock import MagicMock


def _make_word_bank(
    frequencies: dict[str, float], bigrams: dict = None, trigrams: dict = None
) -> MagicMock:
    """Return a WordBank mock with controllable frequency/bigram/trigram data."""
    wb = MagicMock()
    wb.get_frequency.side_effect = lambda w: frequencies.get(w.lower(), 0.0)
    wb.get_bigram_frequency.side_effect = lambda a, b: (bigrams or {}).get(
        (a.upper(), b.upper()), 0
    )
    wb.get_trigram_frequency.side_effect = lambda a, b, c: (trigrams or {}).get(
        (a.upper(), b.upper(), c.upper()), 0
    )
    return wb


class TestMakeFrequencyGuess(unittest.TestCase):

    def _make_guesser(self, frequencies):
        from cryptograms.core.guess import Guesser

        return Guesser(_make_word_bank(frequencies))

    def test_returns_highest_frequency_word(self):
        g = self._make_guesser({"the": 0.07, "and": 0.03, "for": 0.01})
        word, confidence = g.make_frequency_guess(["the", "and", "for"])
        self.assertEqual(word, "the")

    def test_confidence_is_proportion_of_total(self):
        g = self._make_guesser({"the": 0.06, "and": 0.04})
        _, confidence = g.make_frequency_guess(["the", "and"])
        self.assertAlmostEqual(confidence, 0.6, places=5)

    def test_zero_frequency_gives_zero_confidence(self):
        g = self._make_guesser({})
        word, confidence = g.make_frequency_guess(["xyz", "qqq"])
        self.assertEqual(confidence, 0.0)


class TestMakeGuessWithBigrams(unittest.TestCase):
    """Bigram scores fire, frequency floor prevents all-zero collapse."""

    def _make_guesser(self, frequencies, bigrams=None):
        from cryptograms.core.guess import Guesser

        return Guesser(_make_word_bank(frequencies, bigrams=bigrams))

    def test_bigram_context_preferred_over_pure_frequency(self):
        """Word supported by bigram should beat a more frequent word with no bigram support."""
        # "it" is less frequent than "in", but "is it" bigram fires
        freqs = {"it": 0.02, "in": 0.05}
        bigrams = {("IS", "IT"): 50}
        g = self._make_guesser(freqs, bigrams)
        word, confidence = g.make_guess_with_bigrams(["it", "in"], preceding="is")
        self.assertEqual(word, "it")
        self.assertGreater(confidence, 0.0)

    def test_frequency_floor_prevents_zero_confidence(self):
        """When no bigrams fire, word frequency alone still produces nonzero confidence."""
        freqs = {"the": 0.07, "zyx": 0.001}
        g = self._make_guesser(freqs, bigrams={})  # no bigram data
        word, confidence = g.make_guess_with_bigrams(["the", "zyx"], preceding="of")
        self.assertGreater(confidence, 0.0)
        self.assertEqual(word, "the")


class TestMakeGuessWithTrigrams(unittest.TestCase):

    def _make_guesser(self, frequencies, bigrams=None, trigrams=None):
        from cryptograms.core.guess import Guesser

        return Guesser(_make_word_bank(frequencies, bigrams=bigrams, trigrams=trigrams))

    def test_trigram_context_influences_choice(self):
        freqs = {"the": 0.07, "and": 0.05}
        trig = {("OF", "THE", "END"): 30}
        g = self._make_guesser(freqs, trigrams=trig)
        word, _ = g.make_guess_with_trigrams(
            ["the", "and"], preceding="of", following="end"
        )
        self.assertEqual(word, "the")

    def test_frequency_floor_prevents_zero_confidence(self):
        """When trigrams and bigrams are both 0, word frequency is the only signal."""
        freqs = {"the": 0.07, "xyz": 0.0001}
        g = self._make_guesser(freqs, bigrams={}, trigrams={})
        _, confidence = g.make_guess_with_trigrams(
            ["the", "xyz"], preceding="of", following="end"
        )
        self.assertGreater(confidence, 0.0)


class TestBestGuess(unittest.TestCase):
    """Unified best_guess() routing: trigrams > bigrams > frequency."""

    def _make_guesser(self, frequencies, bigrams=None, trigrams=None):
        from cryptograms.core.guess import Guesser

        return Guesser(_make_word_bank(frequencies, bigrams=bigrams, trigrams=trigrams))

    def test_uses_trigrams_when_both_neighbours_known(self):
        freqs = {"the": 0.07, "and": 0.05}
        trig = {("OF", "THE", "END"): 100}
        g = self._make_guesser(freqs, trigrams=trig)
        word, _ = g.best_guess(["the", "and"], preceding="of", following="end")
        self.assertEqual(word, "the")

    def test_uses_bigrams_when_only_one_neighbour_known(self):
        freqs = {"it": 0.02, "in": 0.05}
        bigrams = {("IS", "IT"): 200}
        g = self._make_guesser(freqs, bigrams=bigrams)
        word, _ = g.best_guess(["it", "in"], preceding="is", following=None)
        self.assertEqual(word, "it")

    def test_falls_back_to_frequency_with_no_neighbours(self):
        freqs = {"the": 0.07, "and": 0.03}
        g = self._make_guesser(freqs)
        word, confidence = g.best_guess(["the", "and"], preceding=None, following=None)
        self.assertEqual(word, "the")
        self.assertGreater(confidence, 0.0)

    def test_frequency_floor_still_works_when_no_neighbours(self):
        """No neighbours + no bigram data → frequency floor is the only signal; nonzero."""
        freqs = {"the": 0.07, "xyz": 0.001}
        g = self._make_guesser(freqs, bigrams={}, trigrams={})
        _, confidence = g.best_guess(["the", "xyz"], preceding=None, following=None)
        self.assertGreater(confidence, 0.0)


if __name__ == "__main__":
    unittest.main()
