# This class represents car plates
import re

class Plate:
    def __init__(self, raw: str):
        self.raw = raw.strip().upper()
        
        # Conponents
        self.letters = "".join(c for c in self.raw if c.isalpha())
        self.digits = "".join(c for c in self.raw if c.isdigit())

    # Returns all letters no matter the position
    def get_letter_sequence(self) -> str:
        return self.letters
    
    # method for fetching letter clusters
    def get_letter_clusters(self) -> list[str]:
        return re.findall(r"[A-Z]+", self.raw)
    
    # Returns all the digits in the plate
    def get_digit_sequence(self) -> str:
        return self.digits