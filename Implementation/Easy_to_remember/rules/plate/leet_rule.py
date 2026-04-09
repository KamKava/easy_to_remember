"""
This rule converts digits to letter , letters to digits
"""
import re
from rules.base_rule import Rule
from application.helpers.similarity import normalized_similarity

name = "leet"

# Mapping digits to letter
digit_to_letter = {
    "0" : "O",
    "1" : "I",
    "3" : "E", 
    "4" : "A",
    "5" : "S",
    "7" : "T",
    "8" : "B"
}

# Mapping letters to digits
letter_to_digit = {
    "O" : "0",
    "I" : "1",
    "E" : "3", 
    "A" : "4",
    "S" : "5",
    "T" : "7",
    "B" : "8"
}


class LeetRule(Rule):
    name = "leet_match"

    def __init__(self, target_word: str, weight: float = 3.0, min_sim: float=0.8):
        self.target = "".join(ch for ch in target_word.upper() if ch.isalpha())
        self.weight = weight
        self.min_sim = min_sim
        self.target_leet = self.letters_to_digits(self.target)

    # Convert digits into letters
    def digits_to_letters(self, s:str) -> str:
        out = []
        for ch in s.upper():
            if ch.isalpha():
                out.append(ch)
            elif ch.isdigit():
                out.append(digit_to_letter.get(ch, ""))
        return "".join(out)
    
    # Convert letters into digits
    def letters_to_digits(self, s:str) -> str:
        out = []
        for ch in s.upper():
            if ch.isalpha():
                out.append(letter_to_digit.get(ch, ch))
            elif ch.isdigit():
                out.append(ch)
        return "".join(out)
    
    # A method for search different variations
    def get_search_variations(self) -> list[str]:
        if not self.target:
            return
        variations = {self.target}

        # For each potential convertee
        for i, ch in enumerate(self.target):
            if ch in letter_to_digit:
                new_variations = set()
                for variation in variations:
                    characters = list(variation)
                    characters[i] = letter_to_digit[ch]
                    new_variations.add("".join(characters))
                variations.update(new_variations)
        # return longest variations first
        return sorted(variations, key=len, reverse=True)

    # Method that converts objects to leet strings
    def get_letter_candidates(self, raw: str) -> list[str]:
        raw = "".join(ch for ch in raw.upper() if ch.isalnum())
        if not raw:
            return []
        
        candidates = []

        plain_letters = "".join(ch for ch in raw if ch.isalpha())
        if plain_letters:
            candidates.append(plain_letters)

        # Convert digits to letters
        transformed = self.digits_to_letters(raw)
        if transformed:
            candidates.append(transformed)
            candidates.extend(re.findall(r"[A-Z]+", transformed))

        cleaned = []
        seen = set()
        for candidate in candidates:
            candidate = "".join(ch for ch in candidate if ch.isalpha())
            if candidate and candidate not in seen:
                cleaned.append(candidate)
                seen.add(candidate)

        return cleaned

    def score(self, object) -> float:
        if not self.target:
            return 0.0
        
        raw = "".join(ch for ch in getattr(object, "raw", "").upper() if ch.isalnum())
        if not raw:
            return 0.0
        
        if self.target_leet and self.target_leet in raw:
            return 1.0 * self.weight
        
        best = 0.0
        length = len(self.target)

        # If target appears inside a letter cluster
        found_letters = self.digits_to_letters(raw)
        letter_clusters = re.findall(r"[A-Z]+", found_letters)

        for c in letter_clusters:
            if self.target in c:
                return 1.0 * self.weight
            
        for c in letter_clusters:
            if len(c) < length:
                best = max(best, normalized_similarity(c, self.target))
            else:
                for i in range(0, len(c) - length +1):
                    best = max(best, normalized_similarity(c[i:i+length], self.target))

        # Compare target word with each letter
        if self.target_leet:
            target_leet_len = len(self.target_leet)
            if len(raw) < target_leet_len:
                best = max(best, normalized_similarity(raw, self.target_leet))
            else:
                for i in range(len(raw) - target_leet_len +1):
                    best = max(best, normalized_similarity(raw[i:i +target_leet_len], self.target_leet))

        if best < self.min_sim:
            return 0.0
        
        return best * self.weight


