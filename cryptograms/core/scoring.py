"""Score the quality of cryptogram solutions."""

from __future__ import annotations

import string

# Strip these from word edges before frequency/bigram lookup.
# Apostrophe is excluded so contractions like "it's" are kept intact.
_PUNCT_STRIP = string.punctuation.replace("'", "")


def score_solution(plaintext: str, word_bank=None) -> float:
    """Score a candidate plaintext on word validity and bigram coherence.

    Returns a float in [0.0, 1.0]:

    * **1.0** — every word is recognised by wordfreq *and* every consecutive
      word pair appears in the Brown corpus.
    * **0.0** — no valid words, or single-word input with zero wordfreq coverage.

    The two components and their weights:

    * ``word_coverage`` (0.4) — fraction of alpha tokens whose
      ``word_frequency(w, 'en') > 1e-7``.  Catches completely nonsensical
      letter sequences that don't form English words at all.

    * ``bigram_hit_rate`` (0.6) — fraction of consecutive word pairs that
      appear at least once in the Brown corpus.  Detects unnatural sequences
      such as "A THANK THEREFORE" where ``(A, THANK)`` is absent from the
      corpus, even though both words are individually valid.

    Note: two solutions whose individual words are all valid but differ only
    by a single common substitution (e.g. THING vs THINK) may score
    identically here if both bigrams appear in Brown.  A log-probability
    or KenLM scorer would separate those cases; this implementation is
    intentionally lightweight and dependency-free beyond what is already
    loaded.

    Args:
        plaintext: The decoded plaintext to evaluate.
        word_bank:  Optional pre-loaded :class:`~cryptograms.core.words.WordBank`
                    instance.  When called from inside the solver, pass
                    ``self.word_bank`` to avoid reconstructing the corpus data.
                    If *None*, a new ``WordBank`` is created (construction is
                    fast; corpus data is loaded lazily on first property access).
    """
    from wordfreq import word_frequency

    # Tokenize: strip edge punctuation, keep apostrophes, skip non-word tokens
    words = [
        cleaned.lower() for w in plaintext.split()
        if (cleaned := w.strip(_PUNCT_STRIP)) and cleaned.replace("'", "").isalpha()
    ]

    if not words:
        return 0.0

    # --- 1. Word coverage -------------------------------------------------
    n_valid = sum(1 for w in words if word_frequency(w, "en") > 1e-7)
    word_coverage = n_valid / len(words)

    if len(words) < 2:
        return word_coverage

    # --- 2. Bigram hit rate -----------------------------------------------
    if word_bank is None:
        from .words import WordBank
        word_bank = WordBank(min_length=1)

    pairs = list(zip(words, words[1:]))
    n_present = sum(
        1 for w1, w2 in pairs
        if word_bank.get_bigram_frequency(w1.upper(), w2.upper()) > 0
    )
    bigram_hit_rate = n_present / len(pairs)

    # --- Combined score ---------------------------------------------------
    return 0.4 * word_coverage + 0.6 * bigram_hit_rate


def validate_english(text: str) -> bool:
    """Check if text looks like valid English."""
    # TODO: Implement validation logic
    return True
