"""Tests for LetterConstraints."""

import unittest

from cryptograms.core.constraints import LetterConstraints
from cryptograms.core.models import Puzzle


class TestLetterConstraintsLock(unittest.TestCase):
    """Test lock() and its global propagation."""

    def setUp(self):
        self.c = LetterConstraints()

    def test_lock_sets_locked_dict(self):
        self.c.lock("A", "T")
        self.assertEqual(self.c.locked["A"], "T")

    def test_lock_collapses_possible_set(self):
        self.c.lock("A", "T")
        self.assertEqual(self.c.possible["A"], {"T"})

    def test_lock_propagates_removes_plain_from_others(self):
        """Locking A→T must remove T from every other cipher letter's possibilities."""
        self.c.lock("A", "T")
        for other in self.c.possible:
            if other != "A":
                self.assertNotIn("T", self.c.possible[other])

    def test_double_lock_same_letter_is_idempotent(self):
        self.c.lock("A", "T")
        self.c.lock("A", "T")  # should not raise
        self.assertEqual(self.c.locked["A"], "T")

    def test_multiple_locks_do_not_conflict(self):
        self.c.lock("A", "T")
        self.c.lock("B", "H")
        self.assertNotIn("T", self.c.possible["B"])
        self.assertNotIn("H", self.c.possible["A"])


class TestLetterConstraintsNarrow(unittest.TestCase):
    """Test narrow() including the auto-lock trigger."""

    def setUp(self):
        self.c = LetterConstraints()

    def test_narrow_intersects_possibilities(self):
        self.c.narrow("A", {"T", "H", "E"})
        self.assertEqual(self.c.possible["A"], {"T", "H", "E"})

    def test_narrow_auto_locks_when_single_candidate(self):
        self.c.narrow("A", {"T"})
        self.assertIn("A", self.c.locked)
        self.assertEqual(self.c.locked["A"], "T")

    def test_narrow_skips_already_locked(self):
        self.c.lock("A", "T")
        self.c.narrow("A", {"H"})  # should be ignored
        self.assertEqual(self.c.locked["A"], "T")

    def test_narrow_skips_non_alpha(self):
        # Should not raise even with punctuation key
        self.c.narrow("'", {"T"})  # no-op for non-alpha


class TestLetterConstraintsSpecialWords(unittest.TestCase):
    """Test the single-letter and apostrophe helpers."""

    def test_single_letter_word_narrowed_to_a_or_i(self):
        puzzle = Puzzle(ciphertext="X IS Y")
        c = LetterConstraints()
        c.reduce_to_relevant(puzzle)
        c.handle_single_letter_words(puzzle)
        self.assertEqual(c.possible["X"], {"A", "I"})

    def test_apostrophe_suffix_s_narrowed(self):
        """XY'Z where suffix length 1 → Z must be T, S, or D."""
        puzzle = Puzzle(ciphertext="AB'C")
        c = LetterConstraints()
        c.reduce_to_relevant(puzzle)
        c.handle_apostrophe_words(puzzle)
        self.assertTrue(c.possible["C"].issubset({"T", "S", "D"}))


if __name__ == "__main__":
    unittest.main()

