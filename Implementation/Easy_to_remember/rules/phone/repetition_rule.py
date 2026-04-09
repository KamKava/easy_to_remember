from rules.base_rule import Rule 
from collections import Counter

# Catch repetative characters
class RepetitionRule(Rule):
    name="repetition"

    def score(self, object):
        raw = "".join(ch for ch in getattr(object, "raw", "").upper() if ch.isalnum())

        if not raw:
            return 0.0
        
        counts = Counter(raw)
        max_repeat = max(counts.values())
        # Return repetition score
        return max_repeat / len(raw)