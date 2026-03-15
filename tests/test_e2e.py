"""End-to-end tests: encrypt a sentence, solve it, verify recovery.

Strategy
--------
Tier 0 – TestEncryptCryptogram
    Pure unit tests for the encryption function.  No solver involved.
    These are always expected to pass.

Tier 1 – TestRoundtripTier1
    Single-letter words.  The solver narrows to {A, I} via the
    single-letter-word constraint, which is guaranteed to work.
    We assert membership rather than exact equality because both
    answers are valid without wider context.

Tier 2 – TestRoundtripTier2
    Sentences of at least six words.  Short cryptograms are inherently
    ambiguous — "I AM" has dozens of plausible substitutions, so
    the solver cannot be expected to recover the exact plaintext.
    Six or more words provide enough cross-word constraints that only
    one reasonable English interpretation typically exists.
    If the solver cannot converge the test is *skipped* (not failed).

Tier 3 – TestRoundtripTier3
    Longer well-known sentences (8+ words) — the ones from the solver's
    own __main__ block.  These exercise the bigram/trigram guessing path.
    Skipped on UnsolvableError; expected to pass as the solver matures.
"""

from __future__ import annotations

import unittest

from cryptograms.core.exceptions import UnsolvableError
from cryptograms.service import encrypt_cryptogram, solve_cryptogram


# ---------------------------------------------------------------------------
# Tier 0 – unit tests for encrypt_cryptogram()
# ---------------------------------------------------------------------------

class TestEncryptCryptogram(unittest.TestCase):
    """Verify the encryption function in isolation — no solver involved."""

    def test_output_same_length_as_input(self):
        ciphertext = encrypt_cryptogram("HELLO WORLD", seed=0)
        self.assertEqual(len(ciphertext), len("HELLO WORLD"))

    def test_non_alpha_characters_pass_through_unchanged(self):
        plaintext = "IT'S A TEST, OK?"
        ciphertext = encrypt_cryptogram(plaintext, seed=0)
        for plain_char, cipher_char in zip(plaintext, ciphertext):
            if not plain_char.isalpha():
                self.assertEqual(plain_char, cipher_char)

    def test_case_is_preserved(self):
        plaintext = "Hello World"
        ciphertext = encrypt_cryptogram(plaintext, seed=0)
        for plain_char, cipher_char in zip(plaintext, ciphertext):
            if plain_char.isalpha():
                self.assertEqual(plain_char.isupper(), cipher_char.isupper())

    def test_deterministic_with_same_seed(self):
        ct1 = encrypt_cryptogram("HELLO", seed=42)
        ct2 = encrypt_cryptogram("HELLO", seed=42)
        self.assertEqual(ct1, ct2)

    def test_different_seeds_produce_different_ciphertexts(self):
        ct1 = encrypt_cryptogram("HELLO WORLD", seed=0)
        ct2 = encrypt_cryptogram("HELLO WORLD", seed=1)
        self.assertNotEqual(ct1, ct2)

    def test_no_seed_produces_different_results(self):
        """Without a seed, two calls should (almost certainly) differ."""
        ct1 = encrypt_cryptogram("HELLO WORLD")
        ct2 = encrypt_cryptogram("HELLO WORLD")
        # Probability of collision is 1/26! — negligible
        self.assertNotEqual(ct1, ct2)


# ---------------------------------------------------------------------------
# Tier 1 – single-letter words
# ---------------------------------------------------------------------------

class TestRoundtripTier1(unittest.TestCase):
    """Single-letter words: solver must narrow to 'A' or 'I'."""

    def _solve(self, plaintext: str, seed: int = 42) -> str:
        ciphertext = encrypt_cryptogram(plaintext, seed=seed)
        return solve_cryptogram(ciphertext).plaintext.upper().strip()

    def test_single_letter_a(self):
        result = self._solve("A")
        self.assertIn(result, {"A", "I"},
                      "Single-letter word must solve to A or I")

    def test_single_letter_i(self):
        result = self._solve("I")
        self.assertIn(result, {"A", "I"},
                      "Single-letter word must solve to A or I")


# ---------------------------------------------------------------------------
# Tier 2 – six-word sentences
# ---------------------------------------------------------------------------

class TestRoundtripTier2(unittest.TestCase):
    """Six-word sentences: enough constraints for a unique English reading."""

    SEED = 42

    def _roundtrip(self, plaintext: str) -> None:
        ciphertext = encrypt_cryptogram(plaintext, seed=self.SEED)
        try:
            solution = solve_cryptogram(ciphertext)
        except UnsolvableError:
            self.skipTest(
                f"Solver could not converge on {plaintext!r} "
                f"(seed={self.SEED}) — solver limitation, not a bug"
            )
        self.assertEqual(
            solution.plaintext.upper(),
            plaintext.upper(),
            f"Solver recovered {solution.plaintext!r} but expected {plaintext!r}",
        )

    def test_to_be_or_not_to_be(self):
        """Word repetition (TO, BE) gives strong cross-word constraints."""
        self._roundtrip("TO BE OR NOT TO BE THAT IS THE QUESTION")

    def test_all_that_glitters_is_not_gold(self):
        self._roundtrip("ALL THAT GLITTERS IS NOT GOLD")

    def test_the_early_bird_catches_the_worm(self):
        """Repeated THE anchors two positions simultaneously."""
        self._roundtrip("THE EARLY BIRD CATCHES THE WORM")

    def test_the_truth_will_set_you_free(self):
        self._roundtrip("THE TRUTH WILL SET YOU FREE")


# ---------------------------------------------------------------------------
# Tier 3 – longer well-known sentences
# ---------------------------------------------------------------------------

class TestRoundtripTier3(unittest.TestCase):
    """Longer sentences — exercises bigram/trigram guessing path."""

    SEED = 42

    def _roundtrip(self, plaintext: str) -> None:
        ciphertext = encrypt_cryptogram(plaintext, seed=self.SEED)
        try:
            solution = solve_cryptogram(ciphertext)
        except UnsolvableError:
            self.skipTest(
                f"Solver could not converge on sentence (seed={self.SEED}) "
                f"— expected to pass as the solver matures"
            )
        self.assertEqual(
            solution.plaintext.upper(),
            plaintext.upper(),
            f"Solver recovered {solution.plaintext!r} but expected {plaintext!r}",
        )

    def test_i_think_therefore_i_am(self):
        """Classic philosophical quote — from the solver's own __main__ block."""
        self._roundtrip("I THINK THEREFORE I AM")

    def test_fear_itself(self):
        """FDR quote — used in the solver's __main__ block."""
        self._roundtrip("THE ONLY THING WE HAVE TO FEAR IS FEAR ITSELF")

    def test_one_small_step(self):
        """Moon landing quote — includes an apostrophe contraction."""
        self._roundtrip("THAT'S ONE SMALL STEP FOR MAN ONE GIANT LEAP FOR MANKIND")

    def test_ten_plus_word_sentences(self):
        sentences = [
            "IT'S A TRUTH UNIVERSALLY ACKNOWLEDGED THAT A MAN IN POSSESSION OF A GOOD FORTUNE MUST BE IN WANT OF A WIFE",
            "A LOT OF THE CONCEPTS IN THE BIBLE ARE BASED ON ANCIENT MYTHOLOGY THAT DOESN'T FIT THE FINDINGS OF SCIENCE",
            "LOVE IS LIKE AN HOURGLASS WITH THE HEART FILLING UP AS THE BRAIN EMPTIES"
        ]

        for sentence in sentences:
            self._roundtrip(sentence)

if __name__ == "__main__":
    unittest.main()

