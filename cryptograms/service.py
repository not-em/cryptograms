"""High-level service helpers for solving cryptograms."""

from __future__ import annotations

from pathlib import Path

from .core.models import Puzzle, Solution
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
