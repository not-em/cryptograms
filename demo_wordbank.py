"""Demo script showing how to use the WordBank class for cryptogram solving."""

from cryptograms.core.words import WordBank


def main():
    print("=" * 70)
    print("WordBank Demo - Cryptogram Solver Helper")
    print("=" * 70)
    print()

    # Initialize WordBank (loads data lazily)
    print("Creating WordBank instance...")
    bank = WordBank(min_length=1)
    print()

    # Demo 1: Get words by length
    print("1. Getting words by length:")
    for length in [1, 2, 3, 5]:
        words = bank.get_words_by_length(length)
        print(f"   {length}-letter words: {len(words):,} words")
        if length <= 2:
            # Show examples for short words
            examples = list(words)[:10]
            print(f"      Examples: {', '.join(examples)}")
    print()

    # Demo 2: Simple words (for solving)
    print("2. Simple words to try first:")
    simple = bank.get_simple_words()
    print(f"   Found {len(simple)} simple words")
    print(f"   First 15: {', '.join(simple[:15])}")
    print()

    # Demo 3: Word frequency analysis
    print("3. Most common words by length:")
    for length in [2, 3, 4, 5]:
        top_words = bank.get_words_by_length_sorted(length, limit=5)
        print(f"   {length}-letter words:")
        for word in top_words:
            freq = bank.get_frequency(word)
            print(f"      '{word}' - frequency: {freq:.6f}")
    print()

    # Demo 4: Words with apostrophes
    print("4. Words with apostrophes (contractions):")
    apostrophe_words = bank.get_words_with_apostrophes()
    print(f"   Found {len(apostrophe_words)} words with apostrophes")
    # Sort by frequency and show top 10
    sorted_apos = sorted(
        apostrophe_words[:100],
        key=lambda w: bank.get_frequency(w),
        reverse=True
    )[:10]
    print(f"   Most common: {', '.join(sorted_apos)}")
    print()

    # Demo 5: Word validation
    print("5. Validating words:")
    test_words = ["hello", "world", "cryptogram", "xyz123", "the", "asdfgh"]
    for word in test_words:
        is_valid = bank.is_valid_word(word)
        status = "✓" if is_valid else "✗"
        freq = bank.get_frequency(word) if is_valid else 0.0
        print(f"   {status} '{word}' - Valid: {is_valid}, Freq: {freq:.6f}")
    print()

    # Demo 6: Pattern matching simulation
    print("6. Simulating pattern matching for cryptogram solving:")
    print("   Suppose we have a 3-letter cipher word with pattern (0,1,2)")
    print("   Looking for 3-letter words...")
    three_letter = bank.get_words_by_length_sorted(3, limit=20)
    print(f"   Top 20 candidates by frequency:")
    for i, word in enumerate(three_letter, 1):
        freq = bank.get_frequency(word)
        print(f"      {i:2}. '{word}' - {freq:.6f}")
    print()

    print("=" * 70)
    print("Demo complete!")
    print()
    print("Usage in your solver:")
    print("  bank = WordBank()")
    print("  candidates = bank.get_words_by_length(5)")
    print("  simple_words = bank.get_simple_words()")
    print("  freq = bank.get_frequency('hello')")
    print("=" * 70)


if __name__ == "__main__":
    main()
