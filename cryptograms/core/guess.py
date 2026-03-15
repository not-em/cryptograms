from __future__ import annotations

import logging

from wordfreq import word_frequency

from .words import WordBank


logger = logging.getLogger(__name__)


class Guesser:
    """Guesses plaintext words from candidates using frequency, bigram, and trigram analysis."""

    def __init__(self, word_bank: WordBank):
        self.word_bank = word_bank

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def best_guess(
        self,
        candidates: list[str],
        preceding: str | None,
        following: str | None,
    ) -> tuple[str, float]:
        """Unified strategy: trigrams if both neighbours known, bigrams if one, frequency otherwise."""
        if preceding and following:
            logger.debug("best_guess strategy=trigram candidates=%d", len(candidates))
            return self.make_guess_with_trigrams(candidates, preceding=preceding, following=following)
        elif preceding or following:
            logger.debug("best_guess strategy=bigram candidates=%d", len(candidates))
            return self.make_guess_with_bigrams(candidates, preceding=preceding, following=following)
        else:
            logger.debug("best_guess strategy=frequency candidates=%d", len(candidates))
            return self.make_frequency_guess(candidates)

    def make_frequency_guess(self, candidates: list[str]) -> tuple[str, float]:
        """Rank candidates purely by wordfreq frequency."""
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

    def make_guess_with_bigrams(
        self,
        candidates: list[str],
        preceding: str | None = None,
        following: str | None = None,
    ) -> tuple[str, float]:
        """Rank candidates by bigram context, with a word-frequency floor.

        score = bigram_score * 0.7 + word_frequency * 0.3
        When bigram data is absent (sparse corpus) word frequency still separates candidates.
        """
        best_word = ""
        best_score = 0.0
        total_score = 0.0

        for word in candidates:
            bigram_score = (
                self._bigram_score(word, preceding, "preceding")
                + self._bigram_score(word, following, "following")
            )
            score = bigram_score * 0.7 + word_frequency(word.lower(), "en") * 0.3
            total_score += score
            if score > best_score:
                best_score = score
                best_word = word

        confidence = best_score / total_score if total_score > 0 else 0.0
        return best_word, confidence

    def make_guess_with_trigrams(
        self,
        candidates: list[str],
        preceding: str | None = None,
        following: str | None = None,
    ) -> tuple[str, float]:
        """Rank candidates by trigram context + bigram average + word-frequency floor.

        score = trigram * 0.6 + bigram_avg * 0.25 + word_frequency * 0.15
        Degrades gracefully: when trigrams are 0 bigrams provide signal; when both are 0
        word frequency still distinguishes candidates.
        """
        best_word = ""
        best_score = 0.0
        total_score = 0.0

        for word in candidates:
            trigram_score = self.get_trigram_score(preceding, word, following)
            bigram_score_avg = (
                self._bigram_score(word, preceding, "preceding")
                + self._bigram_score(word, following, "following")
            ) / 2
            score = (
                trigram_score * 0.6
                + bigram_score_avg * 0.25
                + word_frequency(word.lower(), "en") * 0.15
            )
            total_score += score
            if score > best_score:
                best_score = score
                best_word = word

        confidence = best_score / total_score if total_score > 0 else 0.0
        return best_word, confidence

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _bigram_score(self, word: str, context: str | None, position: str) -> float:
        """Return the Brown-corpus bigram count for the (context, word) or (word, context) pair."""
        if not context:
            return 0.0
        if position == "preceding":
            return self.word_bank.get_bigram_frequency(context, word)
        elif position == "following":
            return self.word_bank.get_bigram_frequency(word, context)
        return 0.0

    def get_trigram_score(self, first: str | None, second: str, third: str | None) -> int:
        """Return the Brown-corpus trigram count; returns 0 if any argument is absent."""
        if not first or not second or not third:
            return 0
        return self.word_bank.get_trigram_frequency(first, second, third)
