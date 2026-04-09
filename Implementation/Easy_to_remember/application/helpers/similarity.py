import Levenshtein

def levenshtein(a, b):
    # Get edit distance as int
    leven = Levenshtein.distance(a, b)
    return leven

def normalized_similarity(a, b):
    distance = levenshtein(a, b)
    max_len = max(len(a), len(b))

    # No division by zero
    if max_len == 0:
        return 1.0
    return 1 - (distance / max_len)


     
    


