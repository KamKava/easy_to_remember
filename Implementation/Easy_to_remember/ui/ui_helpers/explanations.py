from application.modes.plate_mode import PlateMode

class Explanations:
    # Describe rules
    def describe_object(self, mode, item):
        if hasattr(item, "explanation"):
            return item.explanation
        if isinstance(mode, PlateMode):
            return self.explain_plate_item(mode, item)
        return self.explain_phone_item(mode, item)
    
    # Phone number top rule picked
    def explain_phone_item(self, mode, item):
        digits = getattr(item, "digits", "")

        sequence = "0123456789"
        for i in range(len(sequence) - 2):
            if sequence[i:i+3] in digits:
                return "sequence"
            
        if getattr(mode, "current_pattern", None) and self.mode_setting.current_pattern in digits:
            return "matches your pattern"
        
        if len(digits) >= 4 and any (digits[i] == digits[i + 2] for i in range(len(digits) - 2)):
            return "alternating pattern"
        
        if len(digits) > 1 and digits == digits[::-1]:
            return "symmetry"
        
        if digits and len(set(digits)) <= max(2, len(digits) //2):
            return "few unique digits"
        
        if digits and max(digits.count(d) for d in set(digits)) >= 3:
            return "repeated digits"
        
        return "high memorability score"

    # Car plate top rule picked
    def explain_plate_item(self, mode, item):
        raw = getattr(item, "raw", "")
        digits = getattr(item, "digits", "")
        letters = getattr(item, "letters", "")

        pattern = getattr(mode, "current_pattern", None)
        if pattern:
            pattern = pattern.upper()
            raw_clean = "".join(ch for ch in raw.upper() if ch.isalnum())

            digit_pattern = "".join(ch for ch in pattern if ch.isdigit())
            alpha_pattern = "".join(ch for ch in pattern if ch.isalpha())

            # Exact match
            if pattern in raw_clean:
                return "exact pattern match"
            
            # Numeric search
            if pattern.isdigit():
                if digit_pattern and digit_pattern in digits:
                    return "digit pattern match"

                sequence = "0123456789"
                for i in range (len(sequence) - 2):
                    if sequence[i:i+3] in digits:
                        return "sequence"
                    
                if digits and max(digits.count(d) for d in set(digits)) >= 3:
                    return "repeated digits"
                
                cleaned = "".join(ch for ch in raw if ch.isalnum())
                if len(cleaned) <= 4:
                    return "short plate"
                
                return "numeric similarity"

            # Letter only search
            if pattern.isalpha():
                if alpha_pattern and alpha_pattern in letters:
                    return "letter pattern match"
                
                cleaned = "".join(ch for ch in raw if ch.isalnum())
                if len(cleaned) <= 4:
                    return "short plate"
                return "similar pattern"
            
            # Mixed search

            if alpha_pattern and alpha_pattern in letters and digit_pattern and digit_pattern in digits:
                return "mixed pattern match"

            if digit_pattern and digit_pattern in digits:
                return "digit pattern match"
            if alpha_pattern and alpha_pattern in letters:
                return "letter pattern match"
            
            cleaned = "".join(ch for ch in raw if ch.isalnum())
            if len(cleaned) <= 4:
                return "short plate"
            
            if hasattr(self.mode_setting, "get_word_match_score"):
                word_score = mode.get_word_match_score(item)
                if word_score >= 5.0:
                    return "dictionary word match"
                elif word_score >= 3:
                    return "meaningful word pattern"
                elif word_score >= 1.2:
                    return "partial word similarity"

            return "similar pattern"
        


        # No user search yet
        sequence = "0123456789"
        for i in range (len(sequence) - 2):
            if sequence[i:i+3] in digits:
                return "sequence"

        if digits and max(digits.count(d) for d in set(digits)) >= 3:
            return "repeated digits"
                
        cleaned = "".join(ch for ch in raw if ch.isalnum())
        if len(cleaned) <= 4:
            return "short plate"
    
        if hasattr(mode, "get_word_match_score"):
            word_score = mode.get_word_match_score(item)
            if word_score >= 5.0:
                return "dictionary word match"
            elif word_score >= 3:
                return "meaningful word pattern"
            elif word_score >= 1.2:
                return "partial word similarity"

        # If multiple letter groups
        if len(letters) >=3:
            return "letter pattern"

        return "high memorability score"
