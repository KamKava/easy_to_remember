# Class for connecting to the database for phone numbers
import sqlite3
from application.models.db_results import PhoneResult


class PhoneRepository:

    def __init__(self, db_path="data/db/numbers.db"):
        # Connect
        self.connection = sqlite3.connect(db_path)
        # Return objects
        self.connection.row_factory = sqlite3.Row

    # Close connection
    def close(self):
        self.connection.close()

    # Mark as taken method after user selection
    def mark_taken(self, raw):
        cursor = self.connection.cursor()
        cursor.execute("""
            UPDATE phone_numbers
            SET availability = 'taken'
            WHERE raw = ? AND availability = 'available'
        """, (raw,),)
        self.connection.commit()

    # Get the highest scoring numbers
    def get_top_rows(self, limit=500):
        cursor = self.connection.cursor()
        rows = cursor.execute("""
            SELECT raw, digits, availability, symmetry, repetition, sequence_score, unique_digits, alternating
            FROM phone_numbers
            WHERE availability = 'available'
            ORDER BY base_score DESC
            LIMIT ? 
        """, (limit,)).fetchall()

        # Convert rows into PhoneResult objects
        return [PhoneResult(row) for row in rows]
    
    # Find exact match phone numbers
    def get_exact_pattern_rows(self, pattern, limit):
        cursor = self.connection.cursor()
        rows = cursor.execute("""
            SELECT raw, digits, availability, symmetry, repetition, sequence_score, unique_digits, alternating
            FROM phone_numbers
            WHERE availability = 'available'
                AND digits LIKE ?
            ORDER BY base_score DESC
            LIMIT ? 
        """, (f"%{pattern}%", limit)).fetchall()

        # Convert rows into PhoneResult objects
        return [PhoneResult(row) for row in rows]
    
    # Find phone numbers which have similar chunks
    def get_close_pattern_rows(self, chunks, pattern, limit=1000):
        cursor = self.connection.cursor()

        # If no chunks
        if not chunks:
            return []
        
        # Create conditions up to 10 chunks
        clauses = ["digits LIKE ?" for i in chunks[:10]]
        params = [f"%{chunk}%" for chunk in chunks[:10]]
        where_sql = " OR ".join(clauses)

        rows = cursor.execute(f"""
            SELECT raw, digits, availability, symmetry, repetition, sequence_score, unique_digits, alternating
            FROM phone_numbers
            WHERE availability = 'available'
                AND digits NOT LIKE ?
                AND ({where_sql})
            ORDER BY base_score DESC
            LIMIT ? 
        """, (f"%{pattern}%", *params, limit)).fetchall()

        # Convert rows into PhoneResult objects
        return [PhoneResult(row) for row in rows]
    
    # Get extra high scoring phone numbers 
    def get_extra_rows(self, pattern, limit=5000):
        cursor = self.connection.cursor()
        rows = cursor.execute("""
            SELECT raw, digits, availability, symmetry, repetition, sequence_score, unique_digits, alternating
            FROM phone_numbers
            WHERE availability = 'available'
                AND digits NOT LIKE ?
            ORDER BY base_score DESC
            LIMIT ? 
        """, (f"%{pattern}%", limit)).fetchall()

        # Convert rows into PhoneResult objects
        return [PhoneResult(row) for row in rows]

