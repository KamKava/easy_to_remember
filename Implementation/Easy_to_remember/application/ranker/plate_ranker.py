# This class stores the raking logic
import re

class PlateRanker:
    
    def get_similarity_pattern(self, raw:str):
        raw =raw.strip().upper()

        letter_cluster = re.findall(r"[A-Z]+", raw)
        digit_cluster = re.findall(r"\d+", raw)

        # Choose the longest letter cluster for the meaningful part
        best_letters = max(letter_cluster, key=len) if letter_cluster else ""
        best_digits = max(digit_cluster, key=len) if digit_cluster else ""

        return {
            "letters": best_letters,
            "digits": best_digits,
            "raw": "".join(ch for ch in raw if ch.isalnum())
        }


    def get_memorable_pattern_bonus(self, plate) -> float:
        raw = "".join(ch for ch in plate.raw.upper() if ch.isalnum())
        if not raw:
            return 0.0
        
        bonus = 0.0

        # The whole plate is mirrored pattern
        if len(raw) >= 3 and raw == raw[::-1]:
            bonus += 0.8


        # If characters repeat through the whole plate
        if len(set(raw)) <= 2:
            bonus += 0.5

        # Alternating pattern
        if len(raw) >= 4:
            alternating = True
            for i in range(len(raw) -2):
                if raw[i] != raw[i + 2]:
                    alternating = False
                    break
            if alternating:
                bonus += 0.5

        return min(bonus, 2.0)

