# This class if for dealing with explanations to the user

class Explanations:

    def explain_phone_match(self, mode, item):
        digits = getattr(item, "digits", "")

        # If user have done an input, check exact match
        if mode.current_pattern:
            if mode.current_pattern in digits:
                return "exact numeric pattern"

        # labels for phone scoring features    
        feature_names = [
            "symmetry",
            "repeated digits",
            "sequence",
            "few unique digits",
            "alternating pattern"
        ]

        # if base feature scores exist, return name and the strongest feature
        if hasattr(item, "base_features") and item.base_features:
            top_feature = max(range(len(item.base_features)), key=lambda i: item.base_features[i])
            return feature_names[top_feature]
        # Default else
        return "high memorability score"

    # If user searched for pattern, give the explanation accordingly
    def explain_plate_match(self, mode, plate, raw_score, numeric_score, letters_score, leet_score, phonetic_score, edit_score, word_score, readability_score):
        if mode.current_pattern:
            pattern = mode.current_pattern
            raw_clean = "".join(ch for ch in plate.raw.upper() if ch.isalnum())
            digit_pattern = "".join(ch for ch in pattern if ch.isdigit())
            alpha_pattern = "".join(ch for ch in pattern if ch.isalpha())

            # Check first for bes matches
            if pattern in raw_clean:
                return "exact pattern match"
            if alpha_pattern and alpha_pattern in plate.letters:
                return "letter pattern match"
            if digit_pattern and digit_pattern in plate.digits:
                return "digit pattern match"
            
            # If no exact match, compare other matching rules
            scored_rules = {
                "leet match": leet_score,
                "phonetic match": phonetic_score,
                "edit distance match": edit_score,
                "letter similarity": letters_score,
                "numeric similarity": numeric_score,
                "raw substring match": raw_score,
            }

            # Return strongest  matching rule label
            best_label = max(scored_rules, key=scored_rules.get)
            if scored_rules[best_label] > 0:
                return best_label
        
        # No active query, use memorability

        scored_memorability = {
            "dictionary word match": word_score,
            "readability": readability_score,
            "symmetry": plate.base_features[0] if len(plate.base_features) >0 else 0.0,
            "repetition": plate.base_features[1] if len(plate.base_features) > 1 else 0.0,
            "sequence": plate.base_features[2] if len(plate.base_features) > 2 else 0.0,
            "alternating pattern": plate.base_features[3] if len(plate.base_features) > 3 else 0.0,
        }
        # Return the explanation
        best_label = max(scored_memorability, key=scored_memorability.get)
        return best_label if scored_memorability[best_label] > 0 else "high memorability score"
