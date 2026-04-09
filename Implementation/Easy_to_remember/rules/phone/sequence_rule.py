from rules.base_rule import Rule

class SequenceRule(Rule):
    name = "sequence"

    # Check three digit sequences
    def score(self, object):
        digits = object.digits
        seq = "0123456789"
        for i in range(len(seq) - 3):
            if seq[i:i+3] in digits:
                return 1.0
        return 0.0