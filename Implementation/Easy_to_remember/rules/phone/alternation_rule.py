from rules.base_rule import Rule

class AlternatingDigitRule(Rule):
    name = "alternating"

    # Get digits from object, else use empty string
    def score(self, object):
        digits = getattr(object, "digits", "")
        # The pattern must be at least 4 digits long
        if len(digits) < 4:
            return 0.0
        
        alternating_pairs = 0
        total_checks = len(digits) - 2

        # Compare the digit (i) with (i+2)
        for i in range(total_checks):
            if digits[i] == digits[i + 2]:
                alternating_pairs += 1

        # Return proportion of matches
        return alternating_pairs / total_checks if total_checks > 0 else 0.0