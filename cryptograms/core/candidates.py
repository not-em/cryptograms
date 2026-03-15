"""Candidate word management for cryptogram solving."""

from __future__ import annotations

import logging

from .constraints import LetterConstraints
from .guess import Guesser
from .models import Puzzle
from .patterns import generate_patterns
from .words import WordBank


logger = logging.getLogger(__name__)


class WordCandidates:
    """Manages possible plaintext words for cipher words based on patterns."""

    def __init__(self, word_bank: WordBank):
        self.word_bank = word_bank
        self.guesser = Guesser(word_bank)
        self.patterns = generate_patterns(list(self.word_bank.words))
        self.possible_words: dict[str, list[str]] = {}
        self.solved_words: dict[str, str] = {}
        self.solved = False

    def initialise_candidates(self, puzzle: Puzzle):
        """Initialise candidates for all cipher words in the puzzle."""
        for word, pattern in puzzle.patterns.items():
            self.possible_words[word] = self.patterns.get(pattern, []).copy()

    def narrow_candidates(self, puzzle: Puzzle, constraints: LetterConstraints):
        """Narrow candidates for each cipher word based on current letter constraints."""
        for word in puzzle.words:
            possible_words = self.possible_words.get(word, [])
            narrowed = [
                candidate
                for candidate in possible_words
                if self._matches_constraints(word, candidate, constraints)
            ]
            self.possible_words[word] = narrowed
            logger.debug("Narrowed candidates for %s: %s", word, narrowed)

            if len(narrowed) == 1:
                # Only one candidate left — lock all its letter mappings
                for c_letter, p_letter in zip(word, narrowed[0]):
                    constraints.lock(c_letter, p_letter.upper())
                self.solved_words[word] = narrowed[0]

    @staticmethod
    def _matches_constraints(
        cipher_word: str, candidate: str, constraints: LetterConstraints
    ) -> bool:
        """Return True if every cipher letter in candidate is still a live possibility."""
        for c_letter, p_letter in zip(cipher_word, candidate):
            if not c_letter.isalpha():
                continue
            if p_letter.upper() not in constraints.possible.get(c_letter, set()):
                return False
        return True

    def narrow_constraints_from_candidates(self, constraints: LetterConstraints):
        """Tighten letter constraints using the union of letters across current candidates."""
        for cipher_word, possible_words in self.possible_words.items():
            for i, c_letter in enumerate(cipher_word):
                possible_letters = {word[i].upper() for word in possible_words}
                constraints.narrow(c_letter, possible_letters)

    def finalise_word(self, cipher_word: str, plaintext_word: str):
        """Force a word mapping and lock in its letter assignments."""
        self.solved_words[cipher_word] = plaintext_word
        self.possible_words[cipher_word] = [plaintext_word]

    def is_word_solved(self, cipher_word: str) -> bool:
        """Return True if this cipher word has been resolved to a single plaintext word."""
        return cipher_word in self.solved_words

    def get_solved_word(self, cipher_word: str) -> str | None:
        """Return the solved plaintext word, or None if not yet solved."""
        return self.solved_words.get(cipher_word)

    def check_solved(self) -> bool:
        """Return True when every cipher word has exactly one remaining candidate."""
        solved = all(len(candidates) == 1 for candidates in self.possible_words.values())
        logger.debug("Check solved: %s", solved)
        return solved

