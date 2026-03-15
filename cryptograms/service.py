"""High-level service helpers for solving cryptograms."""

from __future__ import annotations

import random
import string
from pathlib import Path

from .core.models import CipherMapping, Puzzle, Solution
from .core.solver import Solver


def solve_cryptogram(
    ciphertext: str,
    *,
    clue: str | None = None,
    locked_pairs: dict[str, str] | None = None,
) -> Solution:
    """Solve a cryptogram string using the default solver."""
    puzzle = Puzzle(ciphertext=ciphertext, clue=clue, locked_pairs=locked_pairs)
    solver = Solver()
    return solver.solve(puzzle)


def solve_file(
    path: str | Path,
    *,
    clue: str | None = None,
    locked_pairs: dict[str, str] | None = None,
) -> Solution:
    """Load a ciphertext from disk and solve it."""
    ciphertext = Path(path).read_text(encoding="utf-8")
    return solve_cryptogram(ciphertext, clue=clue, locked_pairs=locked_pairs)


def encrypt_cryptogram(
    plaintext: str,
    *,
    seed: int | None = None,
) -> tuple[str, CipherMapping]:
    """Encrypt plaintext with a random substitution cipher.

    Generates a random bijective letter substitution and applies it to the
    plaintext, preserving case and all non-alphabetic characters.

    Args:
        plaintext: The text to encrypt.
        seed: Optional integer seed for reproducible output (useful in tests).

    Returns:
        A tuple of ``(ciphertext, decode_mapping)`` where ``decode_mapping``
        is the :class:`CipherMapping` that solvers use to recover the original
        plaintext from the ciphertext.
    """
    rng = random.Random(seed)
    plain_letters = list(string.ascii_uppercase)
    cipher_letters = plain_letters.copy()
    rng.shuffle(cipher_letters)

    # Build a case-preserving translation table (plain → cipher)
    encode_map = str.maketrans(
        "".join(plain_letters) + "".join(plain_letters).lower(),
        "".join(cipher_letters) + "".join(c.lower() for c in cipher_letters),
    )
    ciphertext = plaintext.translate(encode_map)

    # CipherMapping stores cipher → plain (the decoding direction)
    decode = {c: p for p, c in zip(plain_letters, cipher_letters)}
    return ciphertext, CipherMapping(mapping=decode)

