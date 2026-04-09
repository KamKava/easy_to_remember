# This class is for validating the inputs
import re

class InputValidator:
    @staticmethod
    def validate_phone_pattern(pattern: str):
        cleaned = pattern.replace(" ", "").strip()

        if not cleaned:
            return False, "Please enter numbers."
        if not cleaned.isdigit():
            return False, "The system only accepts digits."
        if len(cleaned) > 11:
            return False, "The numeric pattern is too long."
        if len(cleaned) < 2:
            return False, "Please enter at least 2 numbers."

        return True, cleaned
    
    @staticmethod
    def validate_plate_pattern(pattern: str):
        cleaned = pattern.strip().upper().replace(" ", "").strip()

        if not cleaned:
            return False, "Please enter desired pattern."
        if not re.fullmatch(r"[A-Z0-9]+", cleaned):
            return False, "The system only accepts only letters and digits."
        if len(cleaned) > 8:
            return False, "The pattern is too long, it takes less than 8 digits."
        if len(cleaned) < 2:
            return False, "Please enter at least 2 characters."

        return True, cleaned
    
    @staticmethod
    def normalize_key(raw: str):
        return "".join(ch for ch in raw.upper() if ch.isalnum())