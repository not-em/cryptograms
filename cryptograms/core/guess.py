from cryptograms.core.words import WordBank


from words import WordBank


class Guesser:
    # Need to guess a word from a list of words using letter frequency analysis
    # If one word is much more likely than the others, return that one with a confidence score

    def __init__(self, word_bank : WordBank):
        self.word_bank = word_bank



    def make_frequency_guess(self, candidates: list[str]) -> tuple[str, float]:
        best_word = ""
        best_score = 0.0

        total_frequency = sum(self.word_bank.get_frequency(word) for word in candidates)

        for word in candidates:
            freq = self.word_bank.get_frequency(word)
            if freq > best_score:
                best_score = freq
                best_word = word

        confidence = best_score / total_frequency if total_frequency > 0 else 0.0

        return best_word, confidence

    # Now also use trigram frequency analysis to improve confidence
    def make_guess_with_bigrams(self, candidates: list[str], preceding: str = None, following: str = None) -> tuple[str, float]:
        best_word = ""
        best_score = 0.0
        total_score = 0.0


        for word in candidates:
            print(f"Evaluating candidate word: {word}")
            score = self._bigram_score(word, preceding, "preceding") + self._bigram_score(word, following, "following")
            print(f"Word: {word}, Score: {score:.6f}")
            total_score += score
            if score > best_score:
                best_score = score
                best_word = word

        confidence = best_score / total_score if total_score > 0 else 0.0

        return best_word, confidence

    def make_guess_with_trigrams(self, candidates: list[str], preceding: str = None, following: str = None) -> tuple[str, float]:
        best_word = ""
        best_score = 0.0
        total_score = 0.0


        for word in candidates:
            print(f"Evaluating candidate trigram: {preceding} {word} {following}")
            score = self.get_trigram_score(preceding, word, following)
            print(f"Word: {word}, Score: {score:.6f}")
            total_score += score
            if score > best_score:
                best_score = score
                best_word = word

        confidence = best_score / total_score if total_score > 0 else 0.0

        return best_word, confidence

    def _bigram_score(self, word: str, context: str = None, position: str = "preceding") -> float:
        """Calculate a bonus score based on trigram frequency in context."""
        # Implement a simple heuristic for trigram scoring
        if context is None:
            return 0.0
        score = 0.0
        if position == "preceding":
            score += self.word_bank.get_bigram_frequency(context, word)
        elif position == "following":
            score += self.word_bank.get_bigram_frequency(word, context)

        print(f"Bigram Score for '{word}' with context '{context}' ({position}): {score:.6f}")
        return score

    def get_trigram_score(self, first: str, second: str, third: str) -> int:
        return self.word_bank.get_trigram_frequency(first, second, third)
