

class PhoneScorer:
    # Total score for a phone number in combination of base
    # feature scores with rule weights
    def row_score(self, mode, item):
        return (
            mode.rule_weights["symmetry"] * item.base_features[0] + 
            mode.rule_weights["repetition"] * item.base_features[1] +
            mode.rule_weights["sequence_score"] * item.base_features[2] +
            mode.rule_weights["unique_digits"] * item.base_features[3] +
            mode.rule_weights["alternating"] * item.base_features[4]
        )

    # Build all possible substrings of a pattern >=4
    def get_pattern_chunks(self, pattern, min_len=4):
        chunks = set()
        for length in range(len(pattern) - 1, min_len - 1, -1):
            for i in range(len(pattern) - length + 1):
                chunks.add(pattern[i:i +length])
        return sorted(chunks, key=len, reverse=True)

    # Count how many digits appear in both pattern and phone number
    def phone_pattern_similarity(self, pattern, digits):
        same_digit_count = 0
        for d in set(pattern):
            same_digit_count += min(pattern.count(d), digits.count(d))

        # Find longest continous chunk of pattern
        longest_chunk = 0
        for i in range(len(pattern)):
            for j in range(i + 1, len(pattern) + 1):
                chunk = pattern[i:j]
                if chunk and chunk in digits:
                    longest_chunk = max(longest_chunk, len(chunk))

        # Final similar score sums number of matching digits, length of the longest matching chunk
        return same_digit_count + longest_chunk
