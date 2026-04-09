import math

class PlateScorer:
    # Cosine similarity
    def cosine_similarity_base(self, mode, item):
        features = item.base_features
        dot = sum(f * u for f, u in zip(features, mode.user_vector))
        norm_object = math.sqrt(sum(f * f for f in features))
        norm_user = math.sqrt(sum(u * u for u in mode.user_vector))

        if norm_object == 0 or norm_user == 0:
            return 0.0
        
        return dot / (norm_object * norm_user)

    def get_memorable_pattern_bonus(self, plate) -> float:
        raw = "".join(ch for ch in plate.raw.upper() if ch.isalnum())
        if not raw:
            return 0.0
        
        bonus = 0.0

        # The whole plate is mirrored pattern
        if len(raw) >= 3 and raw == raw[::-1]:
            bonus += 0.8


        # If characters repeat through the whole plate
        if len(set(raw)) <= 2:
            bonus += 0.5

        # Alternating pattern
        if len(raw) >= 4:
            alternating = True
            for i in range(len(raw) -2):
                if raw[i] != raw[i + 2]:
                    alternating = False
                    break
            if alternating:
                bonus += 0.5

        return min(bonus, 2.0)




