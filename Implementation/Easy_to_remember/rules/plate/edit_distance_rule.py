# This rule observes how similar the object is to a target
from rules.base_rule import Rule
from application.helpers.similarity import normalized_similarity
import re
from rules.plate.leet_rule import LeetRule


class EditDistanceRule(Rule):
    name = "edit_distance"

    def __init__(self, target_word, weight = 3.0, min_similarity=0.8):
        self.target_word = "".join(ch for ch in target_word.upper() if ch.isalnum())
        self.weight = weight
        self.min_similarity = min_similarity

    def candidate_strings(self, object):
        raw = getattr(object, "raw", "").upper()
        if not raw:
            return []
        
        candidates = []

        # Convert digits into letters
        leet_rule = LeetRule(self.target_word, weight=1.0)
        leet_full = leet_rule.digits_to_letters(raw)
        # Add leet version of a word and words from it made by letters
        if leet_full:
            candidates.append(leet_full)
            candidates.extend(re.findall(r"[A-Z]+", leet_full))

        # Letter only
        letters = "".join(ch for ch in raw if ch.isalpha())
        if letters:
            candidates.append(letters)

        # Add letter only groups
        candidates.extend(re.findall(r"[A-Z]+", raw))

        # Only include raw alphanumeric if target has digits
        if any(ch.isdigit() for ch in self.target_word):
            raw_clean = "".join(ch for ch in raw if ch.isalnum())
            if raw_clean:
                candidates.append(raw_clean)
        # Keep only letters        
        cleaned = []
        seen = set()
        for candidate in candidates:
            candidate = "".join(ch for ch in candidate if ch.isalnum())
            if candidate and candidate not in seen:
                cleaned.append(candidate)
                seen.add(candidate)
        return cleaned

    # Compare target to candidates and their substring
    def score(self, object):
        if not self.target_word:
            return 0.0
        
        candidates = self.candidate_strings(object)
        if not candidates:
            return 0.0
        
        best = 0.0
        target_len = len(self.target_word)

        for candidate in candidates:
            # If candidate is shorter, then compare it whole
            if len(candidate) < target_len:
                best = max(best, normalized_similarity(candidate, self.target_word))
            else:
                #If candidate is longer, compare ebery substring
                for i in range(len(candidate) - target_len +1):
                    chunk = candidate[i:i + target_len]
                    best = max(best, normalized_similarity(chunk, self.target_word))
        # Skip the weak matches
        if best < self.min_similarity:
            return 0.0

        # Return score multiplied with the rule weight
        return best * self.weight
        
        
