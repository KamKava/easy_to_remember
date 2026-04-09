# This rule is for matching number phonetic meaning simmilar to words

from rules.base_rule import Rule
from application.helpers.similarity import normalized_similarity

class PhoneticRule(Rule):

    name = "phonetic"

    # Word to digit dictionary
    word_to_digit = {
        "ATE": "8",
        "EIGHT": "8",
        "FOR": "4",
        "FOUR": "4",
        "TO": "2",
        "TOO": "2",
        "TWO": "2",
        "ONE": "1",
        "WON": "1",
    }

    # Shorter words first
    replacements = sorted(word_to_digit.items(), key=lambda x: len(x[0]), reverse=True)


    def __init__(self, target_word, weight=2.0, min_similar=0.75):
        self.weight = weight
        self.target = self.clean(target_word)
        self.min_similar = min_similar
        self.target_variations = self.get_search_variations(max_variations=20)

    # make string upper and skip gaps
    def clean(self, text):
        return "".join(ch for ch in str(text).upper() if ch.isalnum())
    
    # Word to digit
    def get_search_variations(self, max_variations=80):
        text = self.target

        # Empty list if no target text
        if not text:
            return []

        variations = {text}
        queue = [text]
        seen = {text}

        # Creation of new variants using queue
        while queue and len(variations) < max_variations:
            current = queue.pop(0)

            # Try word to digit replacements
            for word, digit in self.replacements:
                start = 0
                while True:
                    idx = current.find(word, start)
                    if idx == -1:
                        break
                    
                    # Replace a found word with a digit
                    new_text = current[:idx] + digit + current[idx + len(word):]
                    # Add new variation if unique
                    if new_text not in seen:
                        seen.add(new_text)
                        variations.add(new_text)
                        queue.append(new_text)

                        if len(variations) >= max_variations:
                            break
                    # Move forward
                    start = idx +1

                # Sort the variations by length
                if len(variations) >= max_variations:
                    break
        return sorted(variations, key=len)

     # Compare raw text against every phonetic variation
    def score(self, object):

        raw = getattr(object, "raw", "")
        raw = self.clean(raw)
        # Return max score
        if not raw or not self.target_variations:
            return 0.0
        
        best = 0.0

        # Full variation is found in text
        for target_variation in self.target_variations:
            if target_variation in raw:
                return 1.0 * self.weight
            
            # Compare raw string
            target_len = len(target_variation)
                
            # Ignore weak matches    
            if len(raw) < target_len:
                similarity = normalized_similarity(raw, target_variation)
                best = max(best, similarity)
            else:
                # Compare every substring
                for i in range(len(raw) - target_len +1):
                    chunk = raw[i:i + target_len]
                    similarity = normalized_similarity(chunk, target_variation)
                    best = max(best, similarity)

        if best < self.min_similar:
            return 0.0
        
        return best * self.weight
