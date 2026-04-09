import re

from rules.plate.leet_rule import LeetRule
from application.helpers.similarity import normalized_similarity
from rules.plate.raw_substring_rule import RawSubstrRule
from rules.plate.numeric_pattern_rule import NumericPatternRule
from rules.plate.user_letters_rule import LettersUser
from rules.plate.edit_distance_rule import EditDistanceRule
from rules.plate.phonetic_rule import PhoneticRule

class PlatePatterns:
    def update_from_user_pattern(self, mode, pattern: str):
        # Store users search pattern
        mode.current_pattern = pattern.upper()
        mode.search_cache = {}

        # Clean the pattern and split into digits and letters
        cleaned = "".join(ch for ch in pattern.upper() if ch.isalnum())
        digits_part = "".join(ch for ch in cleaned if ch.isdigit())
        letters_part = "".join(ch for ch in cleaned if ch.isalpha())

        final_pattern = cleaned

        # Rules always used for plate matching
        mode.base_rules = [
            RawSubstrRule(final_pattern, weight=2.8),
            EditDistanceRule(final_pattern, weight=1.2, min_similarity=0.84)
        ]

        # Add num rule if the pattern has digits
        if digits_part:
            mode.base_rules.append(NumericPatternRule(digits_part, exact_weight=0.6, partial_weight=0.4))
        
        # Add letter rules, if pattern has letters
        if letters_part:
            mode.base_rules.append(LettersUser(letters_part, weight=4.2))
            mode.base_rules.append(LeetRule(letters_part, weight=3.8))
            mode.base_rules.append(PhoneticRule(final_pattern, weight=1.5))

    def update_from_similar_item(self, mode, pattern: str):
        mode.current_pattern = pattern.upper()
        mode.search_cache = {}

        # Try matching dictionary word
        best_word = mode.get_best_similarity_word(pattern)

        # If found, use it
        if best_word:
            letters_part = best_word
            digits_part = ""
            final_pattern = best_word
        # If not split pattern into digits and letters
        else:
            sim_pattern = mode.get_similarity_pattern(pattern)
            letters_part = sim_pattern["letters"]
            digits_part = sim_pattern["digits"]
            final_pattern = letters_part if letters_part else mode.current_pattern

        mode.base_rules =[
            RawSubstrRule(final_pattern, weight=2.8),
            EditDistanceRule(final_pattern, weight=1.4, min_similarity=0.78)
        ]

        # Add num rule if digits exists
        if digits_part:
            mode.base_rules.append(NumericPatternRule(digits_part, exact_weight=0.4, partial_weight=0.2))

        # Add letter and leet rules if letters exists
        if letters_part:
            mode.base_rules.append(LettersUser(letters_part, weight=4.6))
            mode.base_rules.append(LeetRule(letters_part, weight=4.0))

    def get_similarity_pattern(self, raw:str):
        raw =raw.strip().upper()

        # Find groups of letter and digits
        letter_cluster = re.findall(r"[A-Z]+", raw)
        digit_cluster = re.findall(r"\d+", raw)

        # Choose the longest letter cluster for the meaningful part
        best_letters = max(letter_cluster, key=len) if letter_cluster else ""
        best_digits = max(digit_cluster, key=len) if digit_cluster else ""

        # Return most meaningful parts
        return {
            "letters": best_letters,
            "digits": best_digits,
            "raw": "".join(ch for ch in raw if ch.isalnum())
        }


    def get_best_similarity_word(self, mode, raw: str):
        raw_clean = "".join(ch for ch in raw.upper() if ch.isalnum())
        if not raw_clean:
            return None
        
        # Convert leet digits into letters
        leet_rule = LeetRule("", weight=1.0)
        normalized = leet_rule.digits_to_letters(raw_clean)

        # Build candidate strings for matching
        candidates = []
        candidates.append(normalized)
        candidates.extend(re.findall(r"[A-Z]+", normalized))

        best_word = None
        best_score = 0.0

        # Fist search for meaning, substr dictionary matches
        for candidate in candidates:
            for word in mode.dictionary:
                if len(word) < 3:
                    continue
                if word in candidate:
                    score = len(word)
                    if score> best_score:
                        best_score = score
                        best_word = word
        # Return if exact dictionary match was found
        if best_word:
            return best_word
        
        # Second round of matching, approximate using similarity
        for candidate in candidates:
            if len(candidate) < 3:
                continue
            for word in mode.dictionary:
                if len(word) < 3:
                    continue

                # Compare full candidate to dictionary word
                norm_sim = normalized_similarity(candidate, word)
                score = norm_sim* len(word)
                if norm_sim >= 0.72 and score > best_score:
                    best_score = score
                    best_word = word

                # Conpare the subsrtrings of longer candidates
                if len(candidate) > len(word):
                    for i in range(len(candidate) - len(word) + 1):
                        chunk = candidate[i:i +len(word)]
                        norm_sim = normalized_similarity(chunk, word)
                        score = norm_sim * len(word)
                        if norm_sim >= 0.72 and score > best_score:
                            best_score = score
                            best_word = word

        # return best matching word or nothing if not found
        return best_word


