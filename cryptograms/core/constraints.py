"""Constraint tracking for cryptogram letter mappings."""

from __future__ import annotations

import logging

from .models import Puzzle


logger = logging.getLogger(__name__)


class LetterConstraints:
    """Tracks possible mappings for each cipher letter."""

    def __init__(self, alphabet: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        # cipher_letter -> set of possible plaintext letters
        self.possible: dict[str, set[str]] = {c: set(alphabet) for c in alphabet}
        self.locked: dict[str, str] = {}  # Confirmed mappings

    def reduce_to_relevant(self, puzzle: Puzzle):
        """Reduce possible letters to only those appearing in the puzzle."""
        relevant_letters = set("".join(puzzle.words))
        for c in list(self.possible.keys() - relevant_letters):
            self.possible.pop(c)

    def narrow(self, cipher_letter: str, candidates: set[str]):
        """Reduce possible letters for a cipher letter."""
        if cipher_letter in self.locked:
            return  # Already locked
        if not cipher_letter.isalpha():
            return  # Non-letter characters are ignored
        logger.debug("Narrowing %s to %s", cipher_letter, candidates)
        self.possible[cipher_letter] &= candidates
        if len(self.possible[cipher_letter]) == 1:
            self.lock(cipher_letter, next(iter(self.possible[cipher_letter])))

    def lock(self, cipher_letter: str, plaintext_letter: str):
        """Lock in a mapping and propagate constraints globally."""
        logger.debug("Locking %s -> %s", cipher_letter, plaintext_letter)
        self.locked[cipher_letter] = plaintext_letter
        self.possible[cipher_letter] = {plaintext_letter}
        # Remove this plaintext letter from all other cipher letters
        for c in self.possible.keys():
            if c != cipher_letter:
                self.possible[c].discard(plaintext_letter)

    def handle_single_letter_words(self, puzzle: Puzzle):
        """Narrow single-letter cipher words to 'A' or 'I'."""
        for word in puzzle.single_letter_words:
            self.narrow(word[0], {"A", "I"})

    def handle_apostrophe_words(self, puzzle: Puzzle):
        """Apply apostrophe-contraction constraints (e.g. 's, 't, 've, 'll)."""
        for word in puzzle.apostrophe_words:
            suffix = word.split("'")[1]
            if len(suffix) == 1:
                self.narrow(word[-1], {"T", "S", "D"})
            elif len(suffix) == 2:
                self.narrow(word[-2], {"L", "R", "V"})
                self.narrow(word[-1], {"E", "L"})

