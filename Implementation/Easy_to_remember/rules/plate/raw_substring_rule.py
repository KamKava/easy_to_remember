# Rule checks if cleaned pattern appears
from rules.base_rule import Rule

class RawSubstrRule(Rule):
    name = "raw_substring"

    def __init__(self, pattern: str, weight: float = 3.0):
        self.pattern = "".join(ch for ch in pattern.upper() if ch.isalnum())
        self.weight = weight

    # No score if there is no pattern
    def score(self, object) -> float:
        if not self.pattern:
            return 0.0
        
        raw = "".join(ch for ch in getattr(object, "raw", "").upper() if ch.isalnum())
        if not raw:
            return 0.0
        
        if self.pattern in raw:
            return self.weight
        
        return 0.0