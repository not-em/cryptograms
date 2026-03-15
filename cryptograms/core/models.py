"""Data models for cryptogram puzzles and solutions."""

from __future__ import annotations

import logging
import string

from dataclasses import dataclass, field

from .patterns import find_word_pattern

# Characters stripped from word edges before pattern matching.
# Apostrophe is excluded so contractions like "IT'S" are kept intact.
_PUNCT_STRIP = string.punctuation.replace("'", "")


logger = logging.getLogger(__name__)


@dataclass
class CipherMapping:
    """Represents a mapping from cipher letters to plain letters."""

    mapping: dict[str, str] = field(default_factory=dict)

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt text using this mapping."""
        result = []
        for char in ciphertext:
            if char.upper() in self.mapping:
                decrypted = self.mapping[char.upper()]
                result.append(decrypted if char.isupper() else decrypted.lower())
            else:
                result.append(char)
        return "".join(result)


@dataclass
class Puzzle:
    """Represents a cryptogram puzzle to solve."""

    ciphertext: str
    words: list[str] = field(default_factory=list)
    patterns: dict[str, str] = field(default_factory=dict)

    # Two lists for special word categories
    single_letter_words: list[str] = field(default_factory=list)
    apostrophe_words: list[str] = field(default_factory=list)

    def __init__(
        self,
        ciphertext: str,
        clue: str | None = None,
        locked_pairs: dict[str, str] | None = None,
    ):
        self.clue = clue
        self.locked_pairs: dict[str, str] = {
            k.upper(): v.upper() for k, v in (locked_pairs or {}).items()
        }

        self.original_ciphertext = ciphertext
        self.ciphertext = ciphertext.upper()
        self.words = [
            cleaned
            for raw in self.ciphertext.split()
            if (cleaned := raw.strip(_PUNCT_STRIP))
        ]

        self.patterns = {w: find_word_pattern(w) for w in self.words}

        # Single letter words
        self.single_letter_words = [word for word in self.words if len(word) == 1]

        # Apostrophe words
        self.apostrophe_words = [word for word in self.words if "'" in word]

    def get_preceding_word(self, target_word: str) -> str | None:
        """Get the word that precedes the target word in the ciphertext."""
        logger.debug("Finding preceding word for: %s", target_word)
        for i in range(1, len(self.words)):
            if self.words[i] == target_word:
                return self.words[i - 1]
        return None

    def get_following_word(self, target_word: str) -> str | None:
        """Get the word that follows the target word in the ciphertext."""
        words = self.ciphertext.split()
        for i in range(len(words) - 1):
            if words[i] == target_word:
                return words[i + 1]
        return None


@dataclass
class Solution:
    """Represents a solution to a cryptogram."""

    puzzle: Puzzle
    mapping: CipherMapping
    plaintext: str
    confidence: float = 0.0

    def format_summary(self) -> str:
        """Format the solution for display."""
        lines = [
            "=" * 60,
            "CRYPTOGRAM SOLUTION",
            "=" * 60,
            "",
            f"Ciphertext: {self.puzzle.ciphertext}",
            "",
            f"Plaintext:  {self.plaintext}",
            "",
            f"Confidence: {self.confidence:.1%}",
            "",
            "Mapping:",
        ]
        for cipher, plain in sorted(self.mapping.mapping.items()):
            lines.append(f"  {cipher} -> {plain}")
        lines.append("=" * 60)
        return "\n".join(lines)
