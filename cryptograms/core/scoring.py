"""Score the quality of cryptogram solutions."""

from __future__ import annotations


def score_solution(plaintext: str) -> float:
    """
    Score a potential solution based on language characteristics.

    Returns a confidence score between 0.0 and 1.0.
    """
    # TODO: Implement scoring logic:
    # - Check against dictionary
    # - Analyze bigram/trigram frequencies
    # - Look for common words (the, and, of, etc.)
    # - Check for proper English patterns

    # Placeholder: return 0.5 for now
    score = 0.5

    # Simple check: count recognizable words
    common_words = {"THE", "AND", "OR", "OF", "TO", "IN", "A", "IS", "IT"}
    words = plaintext.upper().split()
    if words:
        matches = sum(1 for word in words if word in common_words)
        score = min(matches / len(words), 1.0)

    return score


def validate_english(text: str) -> bool:
    """Check if text looks like valid English."""
    # TODO: Implement validation logic
    # - Check vowel ratio
    # - Check for impossible letter combinations
    # - Verify word structure
    return True
