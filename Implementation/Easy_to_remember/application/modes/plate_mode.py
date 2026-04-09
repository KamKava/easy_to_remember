

from application.helpers.plate_patterns import PlatePatterns
from application.scorer.plate_scorer import PlateScorer
from application.search.plate_search import PlateSearch
from application.explanations.explanations import Explanations
from tools.repositories.plate_db_connection import PlateRepository
from tools.repositories.dictionary_repo import DictionaryRepository

from rules.plate.word_match_dict_rule import WordMatchRule
from rules.plate.readability_rule import ReadabilityRule


class PlateMode:

    def __init__(self, plate_repo=None, dictionary_repo=None):
        print("Start plate mode")
        
        self.repository = plate_repo or PlateRepository()
        self.dictionary_repo = dictionary_repo or DictionaryRepository()
        self.dictionary = self.dictionary_repo.load_words()
        self.explanation = Explanations()
        self.scorer = PlateScorer()
        self.plate_pattern = PlatePatterns()

        self.word_rule = WordMatchRule(
            self.dictionary, 
            exact_weight=5.0,
            sub_weight=3.0,
            approx_weight=0.0,
            min_similarity=0.85
        )

        self.search = PlateSearch()
        self.readability_rule = ReadabilityRule(weight=2.0)
        self.current_pattern = None
        self.search_cache = {}
        self.base_rules = []
        self.current_word_scores ={}

        self.score_configuration = {
            "base_score": 0.20,
            "word_score": 0.40,
            "readability_score": 0.28,
            "memorable_bonus": 0.12,
            "pattern_match": 0.55,
            "memorability": 0.45
        }

        self.user_vector = [0.3, 0.3, 0.3, 0.3, 0.3]

    def close(self):
        self.repository.close()

    def cosine_similarity_base(self, item):
        return self.scorer.cosine_similarity_base(self, item)


    def mark_taken(self, plate):
        self.repository.mark_taken(plate.raw)
        self.search_cache = {}


    def update_from_user_pattern(self, pattern: str):
       return self.plate_pattern.update_from_user_pattern(self, pattern)


    def update_from_similar_item(self, pattern: str):
        return self.plate_pattern.update_from_similar_item(self, pattern)


    def update_from_pattern(self, pattern: str):
        return self.update_from_user_pattern(pattern)

    # Return top suggestions
    def get_top_suggestions(self, n=5):
        return self.search.get_top_suggestions(self, n)

    # Remove repeating plates
    def no_repeated_plate_sug(self, plates):
        return self.search.no_repeated_plate_sug(plates)

    # get meaningful letter and digit pattern
    def get_similarity_pattern(self, raw:str):
        return self.plate_pattern.get_similarity_pattern(raw)

    # Return best matching dictionary word
    def get_best_similarity_word(self, raw: str):
        return self.plate_pattern.get_best_similarity_word(self, raw)

    # Generate a shot explanation
    def explain_plate_match(self, plate, raw_score, numeric_score, letters_score, leet_score, phonetic_score, edit_score, word_score, readability_score):
        return self.explanation.explain_plate_match(self, plate, raw_score, numeric_score, letters_score, leet_score, phonetic_score, edit_score, word_score, readability_score)
    
    # Return extra bonus score
    def get_memorable_pattern_bonus(self, plate) -> float:
        return self.scorer.get_memorable_pattern_bonus(plate)

    # Return word match score
    def get_word_match_score(self, plate):
        return self.current_word_scores.get(plate.raw, 0.0)



