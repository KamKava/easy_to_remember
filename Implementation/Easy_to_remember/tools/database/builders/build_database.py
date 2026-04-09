"""
This class created SWLite tables from csv files
"""

import csv
import sqlite3
from pathlib import Path

from application.models.phone_object import PhoneNumber 
from application.models.plate_object import Plate
from rules.phone.symmetry_rule import SymmetryRule
from rules.phone.repetition_rule import RepetitionRule
from rules.phone.sequence_rule import SequenceRule
from rules.phone.unique_digit_rule import UniqueDigitsRule
from rules.phone.alternation_rule import AlternatingDigitRule
from rules.plate.leet_rule import LeetRule

def build_phone_db(csv_path="data/csv/uk_phone_numbers.csv", db_path="data/db/numbers.db"):
    # Connect to database
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # Bulk inserts
    cursor.execute("PRAGMA journal_mode = MEMORY")
    cursor.execute("PRAGMA synchronous = OFF")
    cursor.execute("PRAGMA temp_store = MEMORY")

    # Remove table if it is created already
    cursor.execute("DROP TABLE IF EXISTS phone_numbers")
    cursor.execute("""
        CREATE TABLE phone_numbers (
            id INTEGER PRIMARY KEY,
            raw TEXT NOT NULL,
            digits TEXT NOT NULL,
            availability TEXT NOT NULL,
            symmetry REAL,
            repetition REAL,
            sequence_score REAL,
            unique_digits REAL,
            alternating REAL,
            base_score REAL
        ) 
    """)

    # Create rule objects
    symmetry = SymmetryRule()
    repetition = RepetitionRule()
    sequence = SequenceRule()
    unique = UniqueDigitsRule()
    alternating = AlternatingDigitRule()

    # Open csv file
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = []
        # Build a phone number object and fill the rows
        for i, row in enumerate(reader, start=1):
            object = PhoneNumber(row["phone_number"])
            availability = row.get("availability", "available").strip().lower()

            # Calculate scores with rules for each
            s1 = symmetry.score(object)
            s2 = repetition.score(object)
            s3 = sequence.score(object)
            s4 = unique.score(object)
            s5 = alternating.score(object)

            # Final weighted score
            base_score = 0.25 * s1 + 0.20 * s2 + 0.20 * s3 + 0.20 * s4 + 0.15 * s5

            # Store in memory before bach insert
            rows.append((object.raw, object.digits, availability, s1, s2, s3, s4, s5, base_score))

            # Baches of 100 000
            if len(rows) >= 100000:
                cursor.executemany("""
                    INSERT INTO phone_numbers(raw, digits, availability, symmetry, repetition, sequence_score, unique_digits, alternating, base_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, rows)
                connection.commit()
                rows.clear()
                print(f"Inserted {i:,} phone rows.")
        # After looping is done, insert remaining rows
        if rows:
            cursor.executemany("""
                INSERT INTO phone_numbers(raw, digits, availability, symmetry, repetition, sequence_score, unique_digits, alternating, base_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)          
            """, rows)
            connection.commit()

    # Create indexes
    cursor.execute("CREATE INDEX idx_phone_digits ON phone_numbers(digits)")
    cursor.execute("CREATE INDEX idx_phone_base_score ON phone_numbers(base_score)")
    cursor.execute("CREATE INDEX idx_phone_availability ON phone_numbers(availability)")
  
    # Disconnect
    connection.commit()
    connection.close()  

# Build plates SQLite table
def build_plates_db(csv_path="data/csv/uk_number_plates.csv", db_path="data/db/plates.db"):
    # Connect
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # Bulk inserts
    cursor.execute("PRAGMA journal_mode = MEMORY")
    cursor.execute("PRAGMA synchronous = OFF")
    cursor.execute("PRAGMA temp_store = MEMORY")

    # Remove a table if there is one already
    cursor.execute("DROP TABLE IF EXISTS plate_numbers")
    # Create a new one
    cursor.execute("""
        CREATE TABLE plate_numbers (
            id INTEGER PRIMARY KEY,
            raw TEXT NOT NULL,
            digits TEXT NOT NULL,
            letters TEXT NOT NULL,
            leet_normalized TEXT NOT NULL,
            availability TEXT NOT NULL,
            symmetry REAL,
            repetition REAL,
            sequence_score REAL,
            unique_digits REAL,
            alternating REAL,
            base_score REAL
        ) 
    """)

    # Coring rule objects
    symmetry = SymmetryRule()
    repetition = RepetitionRule()
    sequence = SequenceRule()
    alternating = AlternatingDigitRule()

    # Leet converter
    leet_converter = LeetRule("", weight=1.0)

    # Open csv
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = []
        # Place plate objects in each row
        for i, row in enumerate(reader, start=1):
            object = Plate(row["plate"])
            availability = row.get("availability", "available").strip().lower()

            # Each rule scores
            s1 = symmetry.score(object)
            s2 = repetition.score(object)
            s3 = sequence.score(object)
            s4 = alternating.score(object)

            # Final weighted score
            base_score = 0.30 * s1 + 0.25 * s2 + 0.25 * s3 + 0.20 * s4

            # No spaces, and all uppercase
            raw_clean = "".join(ch for ch in object.raw.upper() if ch.isalnum())
            leet_normalized = leet_converter.digits_to_letters(raw_clean)

            # Store in memory before bach insert
            rows.append((object.raw, object.digits, object.letters, leet_normalized, availability, s1, s2, s3, s4, base_score))

            # Insert in baches of 100 000 rows
            if len(rows) >= 100000:
                cursor.executemany("""
                    INSERT INTO plate_numbers(raw, digits, letters, leet_normalized, availability, symmetry, repetition, sequence_score, alternating, base_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, rows)
                connection.commit()
                rows.clear()
                print(f"Instead {i:,} plate rows")

        # Remaining rows after last bach
        if rows:
            cursor.executemany("""
                INSERT INTO plate_numbers(raw, digits, letters, leet_normalized, availability, symmetry, repetition, sequence_score, alternating, base_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)          
            """, rows)  
            connection.commit()

    # Create indexes
    cursor.execute("CREATE INDEX idx_plate_digits ON plate_numbers(digits)")
    cursor.execute("CREATE INDEX idx_plate_letters ON plate_numbers(letters)")
    cursor.execute("CREATE INDEX idx_plate_leet_norm ON plate_numbers(leet_normalized)")
    cursor.execute("CREATE INDEX idx_plate_base_score ON plate_numbers(base_score)")
    cursor.execute("CREATE INDEX idx_plate_availability ON plate_numbers(availability)")

    connection.commit()
    connection.close()  

if __name__ == "__main__":
    Path("data").mkdir(exist_ok=True)
    # Build the databases
    build_phone_db()
    build_plates_db()
    print("Databases built successfully.")           