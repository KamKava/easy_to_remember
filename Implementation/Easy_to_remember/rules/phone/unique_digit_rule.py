from rules.base_rule import Rule

class UniqueDigitsRule(Rule):
    name = "unique_digits"

    def score(self, object):
        raw = "".join(ch for ch in getattr(object, "raw", "").upper() if ch.isalnum())

        if not raw:
            return 0.0
        
        # Count unique characters
        unique = len(set(raw))
        # Return score on how much repeating was detected
        return 1 - (unique / len(raw))