# This class is managing the phone mode in the application
# It connects searching, ranking, scoring, explanations, and database
from tools.repositories.phone_db_connection import PhoneRepository
from application.search.phone_search import PhoneSearch
from application.explanations.explanations import Explanations
from application.scorer.phone_scorer import PhoneScorer
from application.ranker.phone_ranker import PhoneRanker

class PhoneMode:

    def __init__(self, repository=None):
        print("Phone mode selected ")

        self.repository = repository or PhoneRepository()
        self.search = PhoneSearch()
        self.explanation = Explanations()
        self.scorer = PhoneScorer()
        self.ranker = PhoneRanker()

        self.current_pattern = None
        self.search_cache = {}

        # Weights for different scoring features
        self.rule_weights = {
            "symmetry": 1.0,
            "repetition": 1.0,
            "sequence_score": 1.0,
            "unique_digits": 1.0,
            "alternating": 1.0
        }

    # Close database connection
    def close(self):
        self.repository.close()

    # Mark the phone number as taken
    def mark_taken(self, phone):
        self.repository.mark_taken(phone.raw)
        self.search_cache = {}

    # Calculate score for one phone number row
    def row_score(self, item):
        return self.scorer.row_score(self, item)
  
    # Update from pattern
    def update_from_pattern(self, pattern):
        self.current_pattern = pattern
        self.search_cache = {}

    # return top phone number suggestions
    def get_top_suggestions(self, n=5):
        return self.search.get_top_suggestions(self, n)

    # Break the pattern into smaller chunks for partial matching
    def get_pattern_chunks(self, pattern, min_len=4):
        return self.ranker.get_pattern_chunks(pattern, min_len)

    # Compare similarity of a digit string to searched pattern
    def phone_pattern_similarity(self, pattern, digits):
        return self.ranker.phone_pattern_similarity(pattern, digits)

    # Return explanations which rule is strongest in the decision making
    def explain_phone_match(self, item):
        return self.explanation.explain_phone_match(self, item)
