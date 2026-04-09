from rules.base_rule import Rule

class SymmetryRule(Rule):
    name = "symmetry"

    def score(self, object):
        raw = "".join(ch for ch in getattr(object, "raw", "").upper() if ch.isalnum())
        # Length of the cleaned string
        n = len(raw)

        if n <= 1:
            return 0.0
        # Counting matches
        matches = 0
        pairs = n // 2

        # Compare two characters from opposite sizes 
        for i in range(pairs):
            if raw[i] == raw[n - i - 1]:
                matches += 1
        # Return matching mirrored pains 
        return matches / pairs if pairs > 0 else 0.0
