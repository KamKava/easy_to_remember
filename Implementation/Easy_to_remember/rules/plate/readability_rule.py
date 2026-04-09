import re
from rules.base_rule import Rule

class ReadabilityRule(Rule):
    name = "readability"

    def __init__(self, weight: float = 2.0):
        self.weight = weight

    def score(self, object) -> float:
        raw = "".join(ch for ch in getattr(object, "raw", "").upper() if ch.isalnum())
        if not raw:
            return 0.0
        
        score = 0.0

        # Shorter plates are prefereble
        length = len(raw)
        if length <= 4:
            score += 0.8
        elif length <= 6:
            score += 0.6
        else: 
            score += 0.3

        # The less switches - the better
        groups = re.findall(r"[A-Z]+|\d+", raw)
        if len(groups) == 1:
            score += 0.7
        elif len(groups) ==2:
            score += 0.6
        elif len(groups) == 3:
            score += 0.4
        else:
            score += 0.1

        # Less unique characters are prefereble
        unique_ratio = len(set(raw)) / len(raw)
        if unique_ratio <= 0.5:
            score += 0.5
        elif unique_ratio <= 0.75:
            score += 0.3
        else:
            score += 0.1

        # Extra credit for having longer chunks matching in letters
        letter_groups = re.findall(r"[A-Z]+", raw)
        longest_letter_group = max((len(g) for g in letter_groups), default=0)
        
        # Count letters and digits
        letter_count = sum(1 for ch in raw if ch.isalpha())
        digit_count = sum(1 for ch in raw if ch.isdigit())

        if longest_letter_group >=4:
            score += 0.8
        elif longest_letter_group == 3:
            score += 0.6
        elif longest_letter_group ==2:
            score += 0.3

        # exclude plates consisting of mostly digits
        if letter_count == 0:
            score -= 0.7
        elif digit_count > letter_count:
            score -= 0.2

        # Normalize score 0 - 1 and multiply by the weight
        normalized = max(0.0, min(score / 3.0, 1.0))
        return normalized * self.weight
