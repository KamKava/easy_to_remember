# Representation phone numbers

class PhoneNumber:
    def __init__(self, raw: str):
        # Original phone number
        self.raw = raw.strip()
        # Keep only digits
        self.digits = "".join(ch for ch in self.raw if ch.isdigit())
        