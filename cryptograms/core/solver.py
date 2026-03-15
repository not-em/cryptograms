# cryptograms/core/pattern_solver.py
from models import Puzzle, Solution
from words import WordBank
from patterns import generate_patterns
from guess import Guesser

class Solver:
    """Solves cryptograms using word pattern matching and constraint propagation."""

    def __init__(self):
        self.word_bank = WordBank(min_length=2)
        self.constraints = LetterConstraints()
        self.candidates = WordCandidates(self.word_bank)
        self.guesser = Guesser(self.word_bank)


    def solve(self, puzzle: Puzzle):
        """Main solving entry point."""

        self.candidates.initialise_candidates(puzzle)
        self.constraints.reduce_to_relevant(puzzle)
        self.constraints.handle_single_letter_words(puzzle)
        self.constraints.handle_apostrophe_words(puzzle)
        self.candidates.narrow_candidates(puzzle, self.constraints)

        state = self.solution_state()
        count = 0

        while not self.candidates.check_solved():
            count += 1
            print(f"--- Iteration {count} ---")

            self.candidates.narrow_constraints_from_candidates(self.constraints)
            self.candidates.narrow_candidates(puzzle, self.constraints)

            if self.solution_state() == state:
                print("No progress made, attempting best guess...")
                self.make_best_guess(puzzle)
                self.candidates.narrow_constraints_from_candidates(self.constraints)

            state = self.solution_state()

        self.show_solution(puzzle)

    def solution_state(self) -> dict:
        """Get current solution state."""
        return {
            "locked_mappings": self.constraints.locked,
            "possible_mappings": self.constraints.possible,
            "word_candidates": self.candidates.possible_words,
            "solved_words": self.candidates.solved_words,
        }

    def make_best_guess(self, puzzle: Puzzle):
        """Make best guesses for all cipher words based on current candidates."""
        print("Making best guesses based on current candidates...")
        max_confidence = 0.0
        best_guess = {}

        for cipher_word, candidates in self.candidates.possible_words.items():
            print(f"Evaluating candidates for '{cipher_word}': {candidates}")
            if len(candidates) < 2:
                print(f"Skipping '{cipher_word}' with {len(candidates)} candidates.")
                continue  # No need to guess if 0 or 1 candidate
            best_word, confidence = self.guesser.make_frequency_guess(candidates)
            print(f"Best guess for '{cipher_word}': {best_word} with confidence {confidence:.2%}")
            print(confidence)
            if confidence > max_confidence:

                max_confidence = confidence
                best_guess = (cipher_word, best_word)
                print(f"Best guess so far: {cipher_word} -> {best_word} (confidence: {confidence:.2%})")


        if max_confidence > 0.8:
            print("Final best guesses to apply:", best_guess)
            self.candidates.finalise_word(*best_guess)

        else:

            print("No high-confidence guesses found with frequency analysis. Trying bigram context...")
            max_confidence = 0.0
             # Try and get a coherent guess with bigram context
            for cipher_word, candidates in self.candidates.possible_words.items():
                if len(candidates) < 2:
                    continue  # No need to guess if 0 or 1 candidate

                print("Guessing for word:", cipher_word)
                print("Candidates:", candidates)

                preceding_word = self.candidates.get_solved_word(puzzle.get_preceding_word(cipher_word))
                following_word = self.candidates.get_solved_word(puzzle.get_following_word(cipher_word))

                print("Preceding word:", preceding_word)
                print("Following word:", following_word)

                if preceding_word and following_word:
                    best_word, confidence = self.guesser.make_guess_with_trigrams(candidates, preceding=preceding_word, following=following_word)

                else:
                    best_word, confidence = self.guesser.make_guess_with_bigrams(
                        candidates,
                        preceding=preceding_word,
                        following=following_word
                    )
                print(f"Best bigram guess for '{cipher_word}': {best_word} with confidence {confidence:.2%}")
                if confidence > max_confidence:
                    max_confidence = confidence
                    best_guess = (cipher_word, best_word)

            print(best_guess)
            self.candidates.finalise_word(*best_guess)


    def show_solution(self, puzzle: Puzzle) -> str:
        """Show final solution."""
        # Map locked letters onto cyphertext string
        solution = "".join([self.constraints.locked.get(c, c) for c in puzzle.ciphertext])
        print("Final solution:", solution)
        return solution




class LetterConstraints:
    """Tracks possible mappings for each cipher letter."""

    def __init__(self, alphabet: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        # cipher_letter -> set of possible plaintext letters
        self.possible: dict[str, set[str]] = {
            c: set(alphabet) for c in alphabet
        }
        self.locked: dict[str, str] = {}  # Confirmed mappings

    def reduce_to_relevant(self, puzzle: Puzzle):
        """Reduce possible letters to only those appearing in the puzzle."""
        relevant_letters = set("".join(puzzle.words))
        for c in self.possible.keys() - relevant_letters:
            self.possible.pop(c)

    def narrow(self, cipher_letter: str, candidates: set[str]):
        """Reduce possible letters for a cipher letter."""
        if cipher_letter in self.locked:
            return  # Already locked
        if not cipher_letter.isalpha():
            return  # Non-letter characters are ignored
        print(f"Narrowing {cipher_letter} to {candidates}")
        if cipher_letter == "D":
            print("Debug:", self.possible[cipher_letter])
            print("Debug:", candidates)
        self.possible[cipher_letter] &= candidates
        if cipher_letter == "D":
            print("Debug:", self.possible[cipher_letter])
        if len(self.possible[cipher_letter]) == 1:
            self.lock(cipher_letter, next(iter(self.possible[cipher_letter])))

    def lock(self, cipher_letter: str, plaintext_letter: str):
        """Lock in a mapping and propagate constraints."""
        print(f"Locking {cipher_letter} -> {plaintext_letter}")
        self.locked[cipher_letter] = plaintext_letter
        self.possible[cipher_letter] = {plaintext_letter}
        # Remove this plaintext letter from other cipher letters
        for c in self.possible.keys():
            if c != cipher_letter:
                self.possible[c].discard(plaintext_letter)

    def handle_single_letter_words(self, puzzle: Puzzle):
        """Handle single-letter words ('A' and 'I')."""
        for word in puzzle.single_letter_words:
            self.narrow(word[0], {'A', 'I'})

    def handle_apostrophe_words(self, puzzle: Puzzle):
        """Handle words with apostrophes."""
        for word in puzzle.apostrophe_words:
            if len(word.split("'")[1]) == 1:
                self.narrow(word[-1], {'T', 'S', 'D'})
            elif len(word.split("'")[1]) == 2:
                self.narrow(word[-2], {'L', 'R', 'V'})
                self.narrow(word[-1], {'E', 'L'})




class WordCandidates:
    """Manages possible plaintext words for cipher words based on patterns."""

    def __init__(self, word_bank: WordBank):
        self.word_bank = word_bank
        self.guesser = Guesser(word_bank)
        self.patterns = generate_patterns(self.word_bank.words)
        self.possible_words: dict[str, list[str]] = {}
        self.solved_words: dict[str, str] = {}
        self.solved = False

    def initialise_candidates(self, puzzle: Puzzle):
        """Initialise candidates for all cipher words in the puzzle."""
        for word, pattern in puzzle.patterns.items():
            self.possible_words[word] = self.patterns.get(pattern, []).copy()

    def narrow_candidates(self, puzzle: Puzzle, constraints: LetterConstraints):
        """Narrow candidates for a cipher word based on current letter constraints."""
        for word in puzzle.words:
            possible_words = self.possible_words.get(word, [])
            narrowed = []
            for candidate in possible_words:
                if self._matches_constraints(word, candidate, constraints):
                    narrowed.append(candidate)
            self.possible_words[word] = narrowed
            print(f"Narrowed candidates for '{word}': {narrowed}")

            if len(narrowed) == 1:
                # If only one candidate remains, lock in its letters
                for c_letter, p_letter in zip(word, narrowed[0]):
                    constraints.lock(c_letter, p_letter)

                self.solved_words[word] = narrowed[0]

    @staticmethod
    def _matches_constraints(cipher_word: str, candidate: str, constraints: LetterConstraints) -> bool:
        """Check if a candidate word matches the letter constraints for a cipher word."""
        for c_letter, p_letter in zip(cipher_word, candidate):
            if not c_letter.isalpha():
                continue
            if p_letter not in constraints.possible.get(c_letter, set()):
                return False
        return True

    def narrow_constraints_from_candidates(self, constraints: LetterConstraints):
        """Narrow letter constraints based on current candidates."""
        for cipher_word, possible_words in self.possible_words.items():
            for i, c_letter in enumerate(cipher_word):
                possible_letters = {word[i] for word in possible_words}
                if c_letter == "D":
                    print("Debug Narrowing D:", possible_letters)
                    print(possible_words)
                constraints.narrow(c_letter, possible_letters)

    def finalise_word(self, cipher_word: str, plaintext_word: str):
        """Finalize a word mapping and lock in its letters."""
        self.solved_words[cipher_word] = plaintext_word
        self.possible_words[cipher_word] = [plaintext_word]

    def is_word_solved(self, cipher_word: str) -> bool:
        """Check if a cipher word has been solved."""
        return cipher_word in self.solved_words

    def get_solved_word(self, cipher_word: str) -> str:
        """Get the solved plaintext word for a cipher word."""
        print(self.solved_words)
        return self.solved_words.get(cipher_word, "")

    def check_solved(self) -> bool:
        """Check if all words have been solved."""
        solved = all(len(candidates) == 1 for candidates in self.possible_words.values())
        print("Check solved:", solved)
        return solved





if __name__ == "__main__":
    # Example usage
    wb = WordBank(min_length=2)
    # Quick cypher for testing
    crypogram = str.maketrans(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
        "ZYXWVUTSRQPONMLKJIHGFEDCBAzyxwvutsrqponmlkjihgfedcba",
    )

    sentence =  "Books are our best possessions in life they are our immortality"
    sentences = [
        # "Books are our best possessions in life they are our immortality",
        # "The quick brown fox jumps over the lazy dog",
        # "To be or not to be that is the question",
        # "All that glitters is not gold",
        # "A journey of a thousand miles begins with a single step",
        # "Fortune favors the bold",
        "I think therefore I am",
        "The only thing we have to fear is fear itself",
        "That's one small step for man one giant leap for mankind",
    ]

    for s in sentences:
        solver = Solver()
        print("\n--- New Sentence ---")
        print(s)
        encrypted = s.translate(crypogram)
        print("Encrypted:", encrypted)
        puzz = Puzzle(ciphertext=encrypted)
        solver.solve(puzz)
