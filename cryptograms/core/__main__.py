"""Demo entry point: python -m cryptograms.core"""

from cryptograms.core.exceptions import UnsolvableError
from cryptograms.core.models import Puzzle
from cryptograms.core.solver import Solver
from cryptograms.core.words import WordBank
from cryptograms.service import encrypt_cryptogram

sentences = [
    "Love is like an hourglass with the heart filling up as the brain empties",
    "I think therefore I am",
    "The only thing we have to fear is fear itself",
    "That's one small step for man one giant leap for mankind",
]

WordBank(min_length=2)  # trigger NLTK download once before the loop

for s in sentences:
    print("\n--- New Sentence ---")
    print(s)
    encrypted = encrypt_cryptogram(s, seed=42)
    try:
        solution = Solver().solve(Puzzle(ciphertext=encrypted))
        print(solution.format_summary())
    except UnsolvableError as exc:
        print(f"Solver failed: {exc}")
