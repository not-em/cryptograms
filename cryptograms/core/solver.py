# cryptograms/core/solver.py
from __future__ import annotations

import logging

from .candidates import WordCandidates
from .constraints import LetterConstraints
from .guess import Guesser
from .models import CipherMapping, Puzzle, Solution
from .words import WordBank


logger = logging.getLogger(__name__)


class Solver:
    """Solves cryptograms using word pattern matching and constraint propagation."""

    def __init__(self):
        self.word_bank = WordBank(min_length=2)
        self.constraints = LetterConstraints()
        self.candidates = WordCandidates(self.word_bank)
        self.guesser = Guesser(self.word_bank)

    def solve(self, puzzle: Puzzle) -> Solution:
        """Main solving entry point."""
        # Apply any pre-locked pairs before narrowing begins
        for cipher_letter, plain_letter in puzzle.locked_pairs.items():
            self.constraints.lock(cipher_letter, plain_letter)

        self.candidates.initialise_candidates(puzzle)
        self.constraints.reduce_to_relevant(puzzle)
        self.constraints.handle_single_letter_words(puzzle)
        self.constraints.handle_apostrophe_words(puzzle)
        self.candidates.narrow_candidates(puzzle, self.constraints)

        from .exceptions import UnsolvableError

        state = self.solution_state()
        count = 0
        max_iterations = 100

        while not self.candidates.check_solved():
            count += 1
            if count > max_iterations:
                raise UnsolvableError(
                    f"Solver did not converge after {max_iterations} iterations."
                )
            logger.debug("Iteration %s", count)

            self.candidates.narrow_constraints_from_candidates(self.constraints)
            self.candidates.narrow_candidates(puzzle, self.constraints)

            if self.solution_state() == state:
                logger.debug("No progress made; attempting best guess")
                self.make_best_guess(puzzle)
                self.candidates.narrow_constraints_from_candidates(self.constraints)

            state = self.solution_state()

        self.show_solution(puzzle)
        return self._build_solution(puzzle)

    def _build_solution(self, puzzle: Puzzle) -> Solution:
        """Construct and return a Solution dataclass from current solver state."""
        mapping = CipherMapping(mapping=dict(self.constraints.locked))
        # Decrypt the *original* ciphertext so case and punctuation are preserved.
        # CipherMapping.decrypt() looks up each letter's uppercase form in the
        # mapping, mirrors the original's case, and passes non-alpha chars through.
        plaintext = mapping.decrypt(puzzle.original_ciphertext)
        from .scoring import score_solution
        confidence = score_solution(plaintext, self.word_bank)
        return Solution(
            puzzle=puzzle,
            mapping=mapping,
            plaintext=plaintext,
            confidence=confidence,
        )

    def solution_state(self) -> tuple:
        """Return an immutable snapshot of progress for stall detection."""
        return (
            frozenset(self.constraints.locked.items()),
            tuple(sorted(len(v) for v in self.candidates.possible_words.values())),
        )

    def make_best_guess(self, puzzle: Puzzle):
        """Pick and apply the single highest-confidence guess across all unsolved cipher words."""
        max_confidence = 0.0
        best_guess = None

        for cipher_word, candidates in self.candidates.possible_words.items():
            if len(candidates) < 2:
                continue

            preceding_word = self.candidates.get_solved_word(puzzle.get_preceding_word(cipher_word))
            following_word = self.candidates.get_solved_word(puzzle.get_following_word(cipher_word))

            best_word, confidence = self.guesser.best_guess(candidates, preceding_word, following_word)
            if confidence > max_confidence:
                max_confidence = confidence
                best_guess = (cipher_word, best_word)

        if best_guess:
            self.candidates.finalise_word(*best_guess)

    def show_solution(self, puzzle: Puzzle) -> None:
        """Emit the final solution to debug logs."""
        solution = "".join([self.constraints.locked.get(c, c) for c in puzzle.ciphertext])
        logger.debug("Final solution: %s", solution)

