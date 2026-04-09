# This rule checks semantic meaning. If the word appears on the 
# dictionary too.
from rules.base_rule import Rule
import re
from application.helpers.similarity import normalized_similarity

# Mapping
leet_map = {
    "0" : "O",
    "1" : "I",
    "3" : "E", 
    "4" : "A",
    "5" : "S",
    "7" : "T",
    "8" : "B"
}

class WordMatchRule(Rule):
    name = "word_match"

    def __init__(self, dictionary_words: list[str], exact_weight: float = 5.0, sub_weight: float = 3.5, approx_weight: float = 1.5, min_similarity: float = 0.8):

        norm_dic = [
            "".join(ch for ch in w.upper() if ch.isalpha())
            for w in dictionary_words
            if w.strip()
            ]
        self.words = sorted(set(w for w in norm_dic if w), key=len, reverse=True)
        self.word_set = set(self.words)
        self.max_word_len = max((len(w) for w in self.words), default=0)
        self.exact_weight = exact_weight
        self.sub_weight = sub_weight
        self.approx_weight = approx_weight
        self.min_similarity = min_similarity

        self.words_by_length = {}
        for w in self.words:
            self.words_by_length.setdefault(len(w), []).append(w)

    # Convert digits in a string into letters
    def leet_changer(self, s:str) -> str:
        out = []
        for ch in s.upper():
            if ch.isalpha():
                out.append(ch)
            elif ch.isdigit():
                out.append(leet_map.get(ch, ""))
        return "".join(out)

    # get raw text from object
    def get_candidates(self, object) -> list[str]:
        raw = getattr(object, "raw", "").upper()
        if not raw:
            return []
        
        candidates = []

        # Letter clusters together and full
        clusters = re.findall(r"[A-Z]+", raw)
        candidates.extend(clusters)

        # Letter cluster full, but need few characters skipped
        full_letters = "".join(ch for ch in raw if ch.isalpha())
        if full_letters:
            candidates.append(full_letters)

        # Leet conversion needed, then split to clusters
        leet_full = self.leet_changer(raw)
        if leet_full:
            candidates.append(leet_full)
            candidates.extend(re.findall(r"[A-Z]+", leet_full))

        # Remove douplicates
        cleaned = []
        seen = set()
        for c in candidates:
            c = "".join(ch for ch in c.upper() if ch.isalpha())
            if c and c not in seen:
                cleaned.append(c)
                seen.add(c)

        return cleaned

    # Longer words = higher bonus
    def length_of_word(self, word_len: int) -> float:
        if word_len >= 6:
            return 1.0
        elif word_len == 5:
            return 0.9
        elif word_len == 4:
            return 0.75
        elif word_len == 3:
            return 0.55
        else:
            return 0.0

    # make strings from objects
    def score(self, object) -> float:
        candidates = self.get_candidates(object)
        if not candidates:
            return 0.0
        best = 0.0

        # Dictionary check candidates
        for c in candidates:
            candidate_len = len(c)

            # Exact word from dictionary
            if c in self.word_set and len(c) >= 3:
                length_bonus = self.length_of_word(len(c))
                best = max(best, self.exact_weight * length_bonus)


            # The word is present in a candidate plate
            for word_len, words_of_len in self.words_by_length.items():
                if word_len < 3:
                    continue

                length_bonus = self.length_of_word(word_len)
                if length_bonus == 0:
                    continue

                if candidate_len >= word_len:
                    for i in range(candidate_len - word_len + 1):
                        chunk = c[i:i + word_len]

                        # Exact or substring  dictionary match
                        if chunk in words_of_len:
                            if chunk == c:
                                best = max(best, self.exact_weight * length_bonus)
                            else:
                                best = max(best, self.sub_weight * length_bonus)

                        # Approximate match with similarity
                        if self.approx_weight > 0:
                            for w in words_of_len:
                                similar = normalized_similarity(chunk, w)
                                if similar >= self.min_similarity:
                                    best = max(best, similar * self.approx_weight * length_bonus)

                # if candidate is shorter than dictionary word compare full candidate approx
                elif self.approx_weight > 0:
                    for w in words_of_len:
                        similar = normalized_similarity(c, w)
                        if similar >= self.min_similarity:
                            best = max(best, similar * self.approx_weight * length_bonus)

        return best

        