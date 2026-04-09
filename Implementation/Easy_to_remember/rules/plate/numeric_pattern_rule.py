from rules.base_rule import Rule

class NumericPatternRule(Rule):
    name = "numeric_pattern"

    def __init__(self, pattern: str, exact_weight: float = 2.0, partial_weight: float = 1.0):
        self.pattern = "".join(ch for ch in pattern if ch.isdigit())
        self.exact_weight = exact_weight
        self.partial_weight = partial_weight

    def score(self, object) -> float:
        if not self.pattern:
            return 0.0

        # Get digits from the object    
        digits = getattr(object, "digits", "")
        if not digits:
            return 0.0

        # If pattern present in digits, return exact match score
        if self.pattern in digits:
            return self.exact_weight

        # Overlap for weaker simmilarity
        best = 0
        for i in range(len(self.pattern)):
            for j in range(i + 1, len(self.pattern) + 1):
                chunk = self.pattern[i:j]
                if chunk and chunk in digits:
                    best = max(best, len(chunk))
        # if no partial match
        if best ==0:
            return 0.0
        # Return score on how mutch of the pattern mathed
        return (best / len(self.pattern)) * self.partial_weight             