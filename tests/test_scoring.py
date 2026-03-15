"""Tests for score_solution().

Coverage
--------
* Unit invariants (range, empty, single word)
* Word-coverage signal: nonsense strings score lower than valid English
* Bigram-coherence signal: sequences with absent bigrams score lower than
  sequences whose bigrams all appear in the Brown corpus

Known limitation (documented here, not tested):
  Two solutions that differ by a single letter substitution where BOTH
  resulting bigrams appear in Brown (e.g. "THING WE" vs "THINK WE") will
  score identically under the current hit-rate formula.  A log-probability
  or KenLM scorer is needed to distinguish those cases.
"""

from __future__ import annotations

import unittest


class TestScoreSolutionInvariants(unittest.TestCase):
    """Range and edge-case invariants that must always hold."""

    @classmethod
    def setUpClass(cls):
        from cryptograms.core.words import WordBank

        cls.wb = WordBank(min_length=1)

    def _score(self, text: str) -> float:
        from cryptograms.core.scoring import score_solution

        return score_solution(text, self.wb)

    def test_empty_string_returns_zero(self):
        self.assertEqual(self._score(""), 0.0)

    def test_score_in_unit_interval(self):
        for text in [
            "HELLO",
            "HELLO WORLD",
            "I AM FINE TODAY",
            "XQZJM WVPBK",
            "THE QUICK BROWN FOX",
        ]:
            s = self._score(text)
            self.assertGreaterEqual(s, 0.0, f"score < 0 for {text!r}")
            self.assertLessEqual(s, 1.0, f"score > 1 for {text!r}")

    def test_single_word_returns_coverage_only(self):
        # Valid single word — coverage = 1.0, no bigram component
        self.assertAlmostEqual(self._score("THE"), 1.0, places=5)

    def test_single_invalid_word_returns_zero(self):
        self.assertAlmostEqual(self._score("XQZJM"), 0.0, places=5)

    def test_non_alpha_only_returns_zero(self):
        self.assertEqual(self._score("123 !!! ???"), 0.0)


class TestScoreSolutionWordCoverage(unittest.TestCase):
    """Word-coverage component: valid English words score higher than nonsense."""

    @classmethod
    def setUpClass(cls):
        from cryptograms.core.words import WordBank

        cls.wb = WordBank(min_length=1)

    def _score(self, text: str) -> float:
        from cryptograms.core.scoring import score_solution

        return score_solution(text, self.wb)

    def test_all_valid_words_beats_all_nonsense(self):
        valid = "THE QUICK BROWN FOX"
        nonsense = "XQZJM WVPBK FGHIJ KLM"
        self.assertGreater(self._score(valid), self._score(nonsense))

    def test_mixed_validity_is_between_extremes(self):
        all_valid = "THE CAT SAT ON THE MAT"
        all_invalid = "XQZJM WVPBK FGHIJ KLM NOPQ RSTU"
        mixed = "THE XQZJM SAT ON THE WVPBK"
        self.assertGreater(self._score(all_valid), self._score(mixed))
        self.assertGreater(self._score(mixed), self._score(all_invalid))


class TestScoreSolutionBigramCoherence(unittest.TestCase):
    """Bigram-hit-rate component: absent bigrams lower the score.

    This catches the class of error where the solver commits to a wrong
    word that produces bigram pairs absent from the Brown corpus.
    Example: "A THANK THEREFORE A IS" contains (A, THANK) = 0 in Brown,
    so it scores below "I THINK THEREFORE I AM".
    """

    @classmethod
    def setUpClass(cls):
        from cryptograms.core.words import WordBank

        cls.wb = WordBank(min_length=1)

    def _score(self, text: str) -> float:
        from cryptograms.core.scoring import score_solution

        return score_solution(text, self.wb)

    def test_i_think_therefore_i_am_beats_wrong_answer(self):
        """The solver's known wrong answer has absent bigrams; correct one does not."""
        correct = "I THINK THEREFORE I AM"
        wrong = "A THANK THEREFORE A IS"  # solver's actual wrong output
        self.assertGreater(
            self._score(correct),
            self._score(wrong),
            "correct solution should score higher than 'A THANK THEREFORE A IS'",
        )

    def test_fdr_quote_scores_above_half(self):
        """A well-known coherent sentence should score comfortably above 0.5."""
        fdr = "THE ONLY THING WE HAVE TO FEAR IS FEAR ITSELF"
        self.assertGreater(self._score(fdr), 0.5)

    def test_absent_bigram_lowers_score(self):
        """Replacing a known good bigram with a nonsense pair should drop the score."""
        good = "I THINK THEREFORE I AM"
        # Replace THINK with XQZJM — (I, XQZJM) will be absent from Brown
        bad = "I XQZJM THEREFORE I AM"
        self.assertGreater(self._score(good), self._score(bad))

    def test_score_without_word_bank_still_works(self):
        """score_solution() must be callable with no word_bank (standalone use)."""
        from cryptograms.core.scoring import score_solution

        result = score_solution("I THINK THEREFORE I AM")
        self.assertGreaterEqual(result, 0.0)
        self.assertLessEqual(result, 1.0)


if __name__ == "__main__":
    unittest.main()
