# Class for connecting to the plate database
import sqlite3
from application.models.db_results import PlateResult
from rules.plate.leet_rule import LeetRule
from rules.plate.phonetic_rule import PhoneticRule

class PlateRepository:
    def __init__(self, db_path="data/db/plates.db"):
        # Connect
        self.connection = sqlite3.connect(db_path)
        # Return rows as objects
        self.connection.row_factory = sqlite3.Row
    
    # Mark plate as taken after uses pick
    def mark_taken(self, raw):
        cursor = self.connection.cursor()
        cursor.execute("""
            UPDATE plate_numbers
            SET availability = 'taken'
            WHERE raw = ? AND availability = 'available'
        """, (raw,))
        self.connection.commit()

    # Close db connection
    def close(self):
        self.connection.close()

    # Return highest scoring plates
    def get_top_rows(self, limit=2000):
        cursor = self.connection.cursor()
        rows = cursor.execute("""
            SELECT raw, digits, letters, leet_normalized, availability, symmetry, repetition, sequence_score, alternating
            FROM plate_numbers
            WHERE availability = 'available'
            ORDER BY base_score DESC
            limit ? 
        """, (limit,)).fetchall()

        # Convert each row into a PlateResult object
        return [PlateResult(row) for row in rows]
    
    # Seach for plates matching the users pattern
    def get_pattern_rows(self, pattern, limit=3000):
        cursor = self.connection.cursor()
        
        # only letters and digits
        cleaned = "".join(ch for ch in pattern.upper() if ch.isalnum())
        # Separation for digits and letters
        digit_pattern = "".join(ch for ch in cleaned if ch.isdigit())
        alpha_pattern = "".join(ch for ch in cleaned if ch.isalpha())

        # Store the rows that are matching
        matched_rows = []
        seen = set()

        # Add rows if they are unique
        def add_rows(rows):
            nonlocal matched_rows, seen
            for row in rows:
                if row["raw"] not in seen:
                    matched_rows.append(row)
                    seen.add(row["raw"])
                if len(matched_rows) >= limit:
                    break
        print("alpha_pattern: ", alpha_pattern)
        
        # Extraction of raw match
        if cleaned:
            rows = cursor.execute("""
                SELECT raw, digits, letters, leet_normalized, availability, symmetry, repetition, sequence_score, alternating
                FROM plate_numbers
                WHERE availability = 'available'
                    AND REPLACE(REPLACE(raw, ' ', ''), '-', '') like ?
                ORDER BY base_score DESC
                LIMIT ? 
            """, (f"%{cleaned}%", limit)).fetchall()
            add_rows(rows)
            print("exact raw rows: ", len(matched_rows))


        # Exact alpha letters and match them to the column
        if alpha_pattern and not digit_pattern and len(matched_rows) < limit:
            rows = cursor.execute(f"""
                SELECT raw, digits, letters, leet_normalized, availability, symmetry, repetition, sequence_score, alternating
                FROM plate_numbers
                WHERE availability = 'available'
                    AND letters LIKE ?
                ORDER BY base_score DESC
                LIMIT ? 
            """, (f"%{alpha_pattern}%", limit)).fetchall()
            add_rows(rows)
            print("exact alpha rows: ", len(matched_rows))

        # Letter chunks if not enough
        if alpha_pattern and not digit_pattern and len(matched_rows) < limit:
            chunks = self.get_alpha_chunks(alpha_pattern, min_len=3)
            print(" alpha chunks: ", chunks[:3])
            
            for chunk in chunks[:3]:
                rows = cursor.execute(f"""
                    SELECT raw, digits, letters, leet_normalized, availability, symmetry, repetition, sequence_score, alternating
                    FROM plate_numbers
                    WHERE availability = 'available'
                        AND letters LIKE ?
                    ORDER BY base_score DESC
                    LIMIT ? 
                """, (f"%{chunk}%", limit)).fetchall()
                add_rows(rows)
                if len(matched_rows) >= limit:
                    break
                print("chunk rows: ", len(matched_rows))
        
        # Leet normalized search
        if alpha_pattern and not digit_pattern and len(matched_rows) < limit:
                rows = cursor.execute(f"""
                    SELECT raw, digits, letters, leet_normalized, availability, symmetry, repetition, sequence_score, alternating
                    FROM plate_numbers
                    WHERE availability = 'available'
                        AND leet_normalized LIKE ?
                    ORDER BY base_score DESC
                    LIMIT ? 
                """, (f"%{alpha_pattern}%", limit)).fetchall()
                add_rows(rows)
                print("exact leet normalized rows: ", len(matched_rows))

        # Generating the leet variations 
        if alpha_pattern and not digit_pattern and len(matched_rows) < limit:
            leet_rule = LeetRule(alpha_pattern, weight=1.0)
            leet_variations = leet_rule.get_search_variations()
            print("leet variations: ", leet_variations)
            
            for variation in leet_variations:
                rows = cursor.execute(f"""
                    SELECT raw, digits, letters, leet_normalized, availability, symmetry, repetition, sequence_score, alternating
                    FROM plate_numbers
                    WHERE availability = 'available'
                        AND raw LIKE ?
                    ORDER BY base_score DESC
                    LIMIT ? 
                """, (f"%{variation}%", limit)).fetchall()
                add_rows(rows)
                if len(matched_rows) >= limit:
                    break
                print("raw leet rows: ", len(matched_rows))

        # Generating phonetic variations
        if cleaned and len(matched_rows) < limit:
            phonetic_rule = PhoneticRule(cleaned, weight=1.0)
            phonetic_variations = phonetic_rule.get_search_variations(max_variations=12)

            local_limit = 100

            for variation in phonetic_variations:
                rows = cursor.execute("""
                    SELECT raw, digits, letters, leet_normalized, availability, symmetry, repetition, sequence_score, alternating
                    FROM plate_numbers
                    WHERE availability = 'available'
                        AND REPLACE(REPLACE(raw, ' ', ''), '-', '') LIKE ?
                    ORDER BY base_score DESC
                    LIMIT ? 
                """, (f"%{variation}%", local_limit)).fetchall()
                add_rows(rows)
                if len(matched_rows) >= limit:
                    break

            print("after phonetic rows: ", len(matched_rows))

        # If digits present, search in the digits column
        if digit_pattern and len(matched_rows) < limit:
            digit_limit = 100 if alpha_pattern else limit
            rows = cursor.execute(f"""
                SELECT raw, digits, letters, leet_normalized, availability, symmetry, repetition, sequence_score, alternating
                FROM plate_numbers
                WHERE availability = 'available'
                    AND digits LIKE ?
                ORDER BY base_score DESC
                LIMIT ? 
            """, (f"%{digit_pattern}%", digit_limit)).fetchall()
            add_rows(rows)
            print("digit rows: ", len(matched_rows))

        # If not enough match rows
        if len(matched_rows) <limit:
            # Ensuring that alphabetic queries would not be filled with unrelated numerical dominant suggestions
            if alpha_pattern and len(alpha_pattern) >= 4:
                chunks = self.get_alpha_chunks(alpha_pattern, min_len=3)
            
                for chunk in chunks[:6]:
                    rows = cursor.execute("""
                        SELECT raw, digits, letters, leet_normalized, availability, symmetry, repetition, sequence_score, alternating
                        FROM plate_numbers
                        WHERE availability = 'available'
                            AND letters like ?
                        ORDER BY base_score DESC
                        LIMIT ? 
                    """, (f"%{chunk}%", 100)).fetchall()
                    add_rows(rows)

                    if len(matched_rows) >=20:
                        break

            # If still missing enough results, give this
            if len(matched_rows) < 5:
                rows = cursor.execute("""
                    SELECT raw, digits, letters, leet_normalized, availability, symmetry, repetition, sequence_score, alternating
                    FROM plate_numbers
                    WHERE availability = 'available'
                    ORDER BY base_score DESC
                    LIMIT ? 
                """, (20,)).fetchall()
                add_rows(rows)
        # Convert database rows into PlateResult
        return [PlateResult(row) for row in matched_rows]

    # Keep only letters
    def get_alpha_chunks(self, text, min_len=3):
        text = "".join(ch for ch in text.upper() if ch.isalpha())
        chunks = set()

        # Create letter chunks longer than 3
        for length in range(len(text), min_len - 1, -1):
            for i in range(len(text) - length + 1):
                chunks.add(text[i:i+ length])
        # Return sorted chunks
        return sorted(chunks, key=len, reverse=True)

