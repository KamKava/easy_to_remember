# A class for the ranking logic

class PhoneRanker:
    # Count how many digits appear in pattern and phone number
    def phone_pattern_similarity(self, pattern, digits):
        same_digit_count = 0
        for d in set(pattern):
            same_digit_count += min(pattern.count(d), digits.count(d))

        # Find longest chunk og the pattern
        longest_chunk = 0
        for i in range(len(pattern)):
            for j in range(i + 1, len(pattern) + 1):
                chunk = pattern[i:j]
                if chunk and chunk in digits:
                    longest_chunk = max(longest_chunk, len(chunk))

        # Final similarity score combination
        return same_digit_count + longest_chunk

    # Build all possible substrings of pattern
    def get_pattern_chunks(self, pattern, min_len=4):
        chunks = set()
        for length in range(len(pattern) - 1, min_len - 1, -1):
            for i in range(len(pattern) - length + 1):
                chunks.add(pattern[i:i +length])
        
        # Return chunks sorted from longest to shortest
        return sorted(chunks, key=len, reverse=True)

