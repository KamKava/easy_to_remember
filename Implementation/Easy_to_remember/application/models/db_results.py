# Classes for turning database rows into objects
import re

class PhoneResult:
    def __init__(self, row):
        self.raw = row["raw"]
        self.digits = row["digits"]
        self.availability = row["availability"]
        self.features = []
        # Core memorability features scores
        self.base_features = [
            row["symmetry"],
            row["repetition"],
            row["sequence_score"],
            row["unique_digits"],
            row["alternating"]
        ]

class PlateResult:
    def __init__(self, row):
        self.raw = row["raw"]
        self.digits = row["digits"]
        self.letters = row["letters"]
        self.leet_normalized = row["leet_normalized"]
        self.availability = row["availability"]
        self.features = []
        # Core memorability features scores
        self.base_features = [
            row["symmetry"],
            row["repetition"],
            row["sequence_score"],
            row["alternating"]
        ]

    # method for retrieving letter sequence
    def get_letter_sequence(self):
        return self.letters
    
    # Method for retrieving letter clusters
    def get_letter_clusters(self):
        return re.findall(r"[A-Z]+", self.raw)
    
    #Method for getting digit sequence
    def get_digit_sequence(self):
        return self.digits