"""Utilities for encoding words and generating encodings for pattern matching."""


def find_word_pattern(word: str) -> str:
    """
    Encode a word into a pattern based on letter occurrences.

    Each unique letter is assigned a number based on its first occurrence.
    For example, "HELLO" -> "12334".
    """
    letter_to_number = {}
    pattern = []
    next_number = 1

    for char in word:
        if not char.isalpha():
            pattern.append(char)
            continue
        if char not in letter_to_number:
            letter_to_number[char] = str(next_number)
            next_number += 1
        pattern.append(letter_to_number[char])

    return "".join(pattern)


def generate_patterns(words: list[str]) -> dict[str, list[str]]:
    """
    Generate a mapping from encoded patterns to words.

    This is useful for matching cipher words to dictionary words based on their patterns.
    """
    patterns: dict[str, list[str]] = {}

    for word in words:
        pattern = find_word_pattern(word)
        if pattern not in patterns:
            patterns[pattern] = []
        patterns[pattern].append(word)

    return patterns
