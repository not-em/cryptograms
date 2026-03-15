"""Tests for the cryptogram solver."""

from pathlib import Path
import tempfile
import unittest

from cryptograms.core.models import CipherMapping, Puzzle
from cryptograms.core.solver import Solver
from cryptograms.service import solve_cryptogram, solve_file


class TestCipherMapping(unittest.TestCase):
    """Test the CipherMapping class."""

    def test_decrypt_simple(self):
        """Test basic decryption."""
        mapping = CipherMapping(mapping={"A": "H", "B": "E", "C": "L", "D": "O"})
        result = mapping.decrypt("ABCCD")
        self.assertEqual(result, "HELLO")

    def test_preserve_case(self):
        """Test that case is preserved."""
        mapping = CipherMapping(mapping={"A": "H", "B": "I"})
        result = mapping.decrypt("Ab")
        self.assertEqual(result, "Hi")


class TestSolver(unittest.TestCase):
    """Test the cryptogram solver."""

    def test_solve_creates_solution(self):
        """Test that solver produces a solution."""
        puzzle = Puzzle(ciphertext="ABC DEF")
        solver = Solver()
        solution = solver.solve(puzzle)

        self.assertIsNotNone(solution)
        self.assertIsNotNone(solution.plaintext)
        self.assertIsNotNone(solution.mapping)

    def test_locked_pairs_respected(self):
        """Test that locked pairs are used in solution."""
        puzzle = Puzzle(ciphertext="ABCD", locked_pairs={"A": "T"})
        solver = Solver()
        solution = solver.solve(puzzle)

        self.assertEqual(solution.mapping.mapping.get("A"), "T")


class TestService(unittest.TestCase):
    """Test the high-level service API."""

    def test_solve_cryptogram(self):
        """Test solve_cryptogram wires clue and locked_pairs into Puzzle/Solver."""
        solution = solve_cryptogram("A", clue="single-letter", locked_pairs={"A": "A"})
        self.assertIsNotNone(solution)
        self.assertIsNotNone(solution.plaintext)
        self.assertEqual(solution.puzzle.clue, "single-letter")
        self.assertEqual(solution.mapping.mapping.get("A"), "A")

    def test_solve_file(self):
        """Test solve_file forwards clue and locked_pairs."""
        with tempfile.TemporaryDirectory() as temp_dir:
            puzzle_path = Path(temp_dir) / "puzzle.txt"
            puzzle_path.write_text("A", encoding="utf-8")

            solution = solve_file(
                puzzle_path,
                clue="from-file",
                locked_pairs={"A": "A"},
            )

        self.assertIsNotNone(solution)
        self.assertEqual(solution.puzzle.clue, "from-file")
        self.assertEqual(solution.mapping.mapping.get("A"), "A")


if __name__ == "__main__":
    unittest.main()
