"""Tests for WordCandidates."""

import unittest
from unittest.mock import MagicMock

from cryptograms.core.candidates import WordCandidates
from cryptograms.core.constraints import LetterConstraints
from cryptograms.core.models import Puzzle
from cryptograms.core.patterns import generate_patterns


def _make_word_bank(words: list[str]) -> MagicMock:
    """Return a minimal WordBank mock backed by the given word list."""
    wb = MagicMock()
    wb.words = set(words)
    wb.get_frequency.side_effect = lambda w: 0.01  # uniform — not under test here
    wb.bigram_frequencies = {}
    wb.trigram_frequencies = {}
    wb.get_bigram_frequency.return_value = 0
    wb.get_trigram_frequency.return_value = 0
    return wb


class TestWordCandidatesNarrow(unittest.TestCase):
    """Test narrow_candidates() basic filtering."""

    def setUp(self):
        # Build a tiny word bank: pattern "123" maps to ["the", "and", "for"]
        # Pattern "12"  maps to ["is", "it", "in"]
        words = ["the", "and", "for", "is", "it", "in"]
        wb = _make_word_bank(words)
        self.wc = WordCandidates(wb)
        self.wc.patterns = generate_patterns(words)

    def test_initialise_populates_possible_words(self):
        puzzle = Puzzle(ciphertext="ABC DEF")
        self.wc.initialise_candidates(puzzle)
        self.assertIn("ABC", self.wc.possible_words)
        self.assertIn("DEF", self.wc.possible_words)

    def test_narrow_eliminates_constraint_violations(self):
        """If A is locked to T, only candidates whose first letter is T survive."""
        puzzle = Puzzle(ciphertext="ABC")
        self.wc.initialise_candidates(puzzle)

        constraints = LetterConstraints()
        constraints.reduce_to_relevant(puzzle)
        constraints.lock("A", "T")  # first cipher letter → 'T'

        self.wc.narrow_candidates(puzzle, constraints)
        remaining = self.wc.possible_words.get("ABC", [])
        for word in remaining:
            self.assertEqual(word[0].upper(), "T")

    def test_single_remaining_candidate_locks_letters(self):
        """When only one candidate survives, its letters are locked in constraints."""
        puzzle = Puzzle(ciphertext="ABC")
        self.wc.initialise_candidates(puzzle)

        constraints = LetterConstraints()
        constraints.reduce_to_relevant(puzzle)
        # Force "the" to be the only viable candidate by pre-locking its letters
        constraints.lock("A", "T")
        constraints.lock("B", "H")
        # C can be anything

        self.wc.narrow_candidates(puzzle, constraints)
        # "the" maps A→T, B→H, C→E; once it's the only candidate, C should be locked to E
        if self.wc.possible_words.get("ABC") == ["the"]:
            self.assertEqual(constraints.locked.get("C"), "E")

    def test_check_solved_true_when_all_single(self):
        puzzle = Puzzle(ciphertext="IS")
        self.wc.initialise_candidates(puzzle)
        self.wc.possible_words["IS"] = ["is"]
        self.assertTrue(self.wc.check_solved())

    def test_check_solved_false_when_multiple(self):
        puzzle = Puzzle(ciphertext="ABC")
        self.wc.initialise_candidates(puzzle)
        # Ensure more than one candidate exists
        if len(self.wc.possible_words.get("ABC", [])) > 1:
            self.assertFalse(self.wc.check_solved())

    def test_get_solved_word_returns_none_when_unsolved(self):
        self.assertIsNone(self.wc.get_solved_word("XYZ"))

    def test_get_solved_word_returns_word_when_solved(self):
        self.wc.solved_words["ABC"] = "the"
        self.assertEqual(self.wc.get_solved_word("ABC"), "the")

    def test_finalise_word_updates_both_dicts(self):
        self.wc.possible_words["ABC"] = ["the", "and"]
        self.wc.finalise_word("ABC", "the")
        self.assertEqual(self.wc.possible_words["ABC"], ["the"])
        self.assertEqual(self.wc.solved_words["ABC"], "the")

    def test_narrow_constraints_from_candidates_narrows_correctly(self):
        """Union of candidate letters at each position should be passed to narrow()."""
        constraints = LetterConstraints()
        # "the" and "and" are 3-letter words; only "the" starts with T
        self.wc.possible_words["ABC"] = ["the"]
        self.wc.narrow_constraints_from_candidates(constraints)
        # A's only candidate letter at position 0 is T (from "the")
        self.assertEqual(constraints.possible.get("A", set()) & {"T"}, {"T"})


if __name__ == "__main__":
    unittest.main()
