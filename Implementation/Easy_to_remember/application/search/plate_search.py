
from tools.repositories.plate_db_connection import PlateRepository
from tools.repositories.dictionary_repo import DictionaryRepository
from application.models.db_results import PlateResult
from application.helpers.similarity import normalized_similarity

from rules.plate.edit_distance_rule import EditDistanceRule
from rules.plate.leet_rule import LeetRule
from rules.plate.word_match_dict_rule import WordMatchRule
from rules.plate.user_letters_rule import LettersUser
from rules.plate.phonetic_rule import PhoneticRule
from rules.plate.raw_substring_rule import RawSubstrRule
from rules.plate.numeric_pattern_rule import NumericPatternRule
from rules.plate.readability_rule import ReadabilityRule


class PlateSearch:
    # Get top suggestion
    def get_top_suggestions(self, mode, n=5):
        # Build a cache key using current pattern
        cache_key = (mode.current_pattern, n, tuple(round(x, 6) for x in mode.user_vector))
        
        # Return cache key results if they exist
        if cache_key in mode.search_cache:
            result, word_scores = mode.search_cache[cache_key]
            mode.current_word_scores = word_scores
            return result

        # Extract rules
        raw_rule = next((r for r in mode.base_rules if getattr(r, "name", "") == "raw_substring"), None)
        numeric_rule = next((r for r in mode.base_rules if getattr(r, "name", "") == "numeric_pattern"), None)
        edit_rule = next((r for r in mode.base_rules if getattr(r, "name", "") == "edit_distance"), None)
        letters_rule = next((r for r in mode.base_rules if getattr(r, "name", "") == "letters_user"), None)
        leet_rule = next((r for r in mode.base_rules if getattr(r, "name", "") == "leet_match"), None)
        phonetic_rule = next((r for r in mode.base_rules if getattr(r, "name", "") == "phonetic"), None)
        
        # Check if the user is searching with rules
        has_pattern_rules = len(mode.base_rules) > 0

        # Get candidate plates, either with pattern-based search or top general plates
        if has_pattern_rules and mode.current_pattern:
            candidates = mode.repository.get_pattern_rows(mode.current_pattern, limit = 1000)
        else:
            candidates =mode.repository.get_top_rows(limit = 2000)

        pre_ranked = []

        # Score every candidate plate
        for plate in candidates:
            base_score = mode.cosine_similarity_base(plate)
            
            raw_score = raw_rule.score(plate) if raw_rule else 0.0
            numeric_score = numeric_rule.score(plate) if numeric_rule else 0.0
            letters_score = letters_rule.score(plate) if letters_rule else 0.0
            leet_score = leet_rule.score(plate) if leet_rule else 0.0
            edit_score = edit_rule.score(plate) if edit_rule else 0.0
            phonetic_score = phonetic_rule.score(plate) if phonetic_rule else 0.0

            # Text rules stronger than numeric patterns
            # Dictionary word score
            word_score = mode.word_rule.score(plate)
            if mode.current_pattern and mode.current_pattern.isalpha():
                pattern_letters = "".join(ch for ch in mode.current_pattern if ch.isalpha())
                plate_letters = "".join(ch for ch in plate.raw.upper() if ch.isalpha())

                if pattern_letters and pattern_letters not in plate_letters:
                    word_score *= 0.4

            # Readability score
            readability_score = mode.readability_rule.score(plate)

            # Explanations of picked rule to the user
            plate.explanation = mode.explain_plate_match(plate, raw_score, numeric_score, letters_score, leet_score, phonetic_score, edit_score, word_score, readability_score)



            if mode.current_pattern and any(ch.isalpha() for ch in mode.current_pattern):
                readability_score *= 1.25


            # Stronger weight for letter only searches
            final_pattern = mode.get_similarity_pattern(mode.current_pattern) if mode.current_pattern else {"letters": "", "digits": ""}
            contains_strong_letters = len(final_pattern["letters"]) >= 3

            # Generate overall match score
            if contains_strong_letters:
                match_score = max(2.4 * letters_score, 0.45 * edit_score, 2.0 *leet_score, 0.35 * raw_score, 0.15 * numeric_score, 0.25 * phonetic_score)
            else:
                match_score = max(raw_score, numeric_score, edit_score, letters_score, leet_score, phonetic_score)

            # Bonus for memorability in the plate
            memorable_pattern_bonus = mode.get_memorable_pattern_bonus(plate)

            # Combined memorability score
            memorability_score = (
                mode.score_configuration["base_score"] * base_score +
                mode.score_configuration["word_score"] * word_score +
                mode.score_configuration["readability_score"] *readability_score + 
                mode.score_configuration["memorable_bonus"] * memorable_pattern_bonus
                )

            # Final pre-ranking score
            if has_pattern_rules:
                pre_score = (
                    mode.score_configuration["pattern_match"] * match_score + 
                    mode.score_configuration["memorability"] * memorability_score
                )
            else:
                pre_score = memorability_score
           
            is_perfect = False

            #  Check if candidate is perfect
            if mode.current_pattern:
                pattern = mode.current_pattern
                digit_pattern = "".join(ch for ch in pattern if ch.isdigit()) 
                alpha_pattern = "".join(ch for ch in pattern if ch.isalpha()) 

                raw_clean = "".join(ch for ch in plate.raw.upper() if ch.isalnum())

                # Exact full raw search
                if pattern in raw_clean:
                    is_perfect = True

                # Numeric only search
                elif pattern.isdigit():
                    if digit_pattern and digit_pattern in plate.digits:
                        is_perfect = True

                # Letters only search
                elif pattern.isalpha():
                    if alpha_pattern and alpha_pattern in plate.letters:
                        is_perfect = True

                # Mixed
                else:
                    # prefer letter clusters better than mix
                    if alpha_pattern and alpha_pattern in plate.letters:
                        is_perfect = True
                    elif digit_pattern and digit_pattern in plate.digits and len(digit_pattern) >= 3:
                        is_perfect = True

            # Check for phonetic rule perfect
            if (phonetic_rule and mode.current_pattern and any(ch.isdigit() for ch in mode.current_pattern) and phonetic_score >= 0.95 * phonetic_rule.weight):
                is_perfect = True

            # Save scores for later ranking
            pre_ranked.append((pre_score, plate, is_perfect, match_score, base_score, word_score, readability_score, memorability_score))

        # Sort by pre-ranking score
        pre_ranked.sort(key=lambda x: x[0], reverse=True)
        top_candidates = pre_ranked[:200]

        mode.current_word_scores ={}
        perfect = []
        close = []
        others = []

        # Split candidate into 3 groups
        for final_score, plate, is_perfect, match_score, base_score, word_score, readability_score, memorability_score in top_candidates:
            mode.current_word_scores[plate.raw] = word_score
            if has_pattern_rules:
                if is_perfect:
                    perfect.append((final_score, plate))
                elif match_score >= 1.5:
                    close.append((final_score, plate))
                else:
                    others.append((final_score, plate))
            else:
                others.append((final_score, plate))

        # sort groups by score
        perfect.sort(key=lambda x: x[0], reverse=True)
        close.sort(key=lambda x: x[0], reverse=True)
        others.sort(key=lambda x: x[0], reverse=True)

        perfect_plates = [plate for score, plate in perfect[:n]]
        remaining = n - len(perfect_plates)

        close_plates = [plate for score, plate in close[:max(0, remaining)]]
        remaining = n - len(perfect_plates) - len(close_plates)

        rest_plates = [plate for score, plate in others[:max(0, remaining)]]

        # No duplicates
        perfect_plates = mode.no_repeated_plate_sug(perfect_plates)
        combined_other = mode.no_repeated_plate_sug(close_plates + rest_plates)

        # Prevent from plate aparing again in both sections
        perfect_keys = {
            "".join(ch for ch in plate.raw.upper() if ch.isalnum())
            for plate in perfect_plates
        }

        combined_other = [
            plate for plate in combined_other
            if "".join(ch for ch in plate.raw.upper() if ch.isalnum()) not in perfect_keys
        ]

        result = (perfect_plates, combined_other)
        mode.search_cache[cache_key] = (result, dict(mode.current_word_scores))

        return result
    
    # method for ensuring that theres no repeated plates
    def no_repeated_plate_sug(self, plates):
        seen = set()
        unique = []

        for plate in plates:
            key = "".join(ch for ch in plate.raw.upper() if ch.isalnum())
            if key not in seen:
                unique.append(plate)
                seen.add(key)

        return unique