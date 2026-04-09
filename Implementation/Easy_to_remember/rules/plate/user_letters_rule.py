# Checks if users letter pattern matches letter groups in the object
from rules.base_rule import Rule

class LettersUser(Rule):
    name = "letters_user"

    def __init__(self, pattern: str, weight: float = 3.0):
        self.pattern = "".join(ch for ch in pattern.upper() if ch.isalpha())
        self.weight = weight

    def score(self, object) -> float:
        if not self.pattern:
            return 0.0
        # get letter cluster method called
        if not hasattr(object, "get_letter_clusters"):
            return 0.0
        
        # Read the objects letter clusters
        clusters = object.get_letter_clusters()
        if not clusters:
            return 0.0
        
        # Exact full match gives max score
        if any(self.pattern == c for c in clusters):
            return 1.0 * self.weight
        
        # Partial score for appearing in cluster
        for cluster in clusters:
            if self.pattern in cluster:
                return 0.7 * self.weight
            
        return 0.0