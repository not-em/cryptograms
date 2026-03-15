"""Tests for the cryptogram solver."""

import unittest

from cryptograms.core.models import CipherMapping, Puzzle
from cryptograms.core.solver import Solver
from cryptograms.service import solve_cryptogram


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
        """Test the solve_cryptogram function."""
        solution = solve_cryptogram("HELLO WORLD")
        self.assertIsNotNone(solution)
        self.assertIsNotNone(solution.plaintext)


if __name__ == "__main__":
    unittest.main()
