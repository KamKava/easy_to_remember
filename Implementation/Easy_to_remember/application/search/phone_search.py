

class PhoneSearch:
     def get_top_suggestions(self, mode, n=5):
        # build cache key using current pattern
        cache_key = (mode.current_pattern, n)
        if cache_key in mode.search_cache:
            return mode.search_cache[cache_key]

        # If no pattern, return genetral sugggestions
        if not mode.current_pattern:
            candidates = mode.repository.get_top_rows(limit=500)
            for item in candidates:
                item.explanation = mode. explain_phone_match(item)
            ranked = sorted(candidates, key=mode.row_score, reverse=True)
            result = (ranked[:n], [])
            mode.search_cache[cache_key] = result
            return result
    
        pattern = mode.current_pattern

        # Find exact matches for numeric pattern
        exact = mode.repository.get_exact_pattern_rows(pattern, limit=n)
        for item in exact:
            item.explanation = "exact numeric pattern"

        # break pattern into smaller chunks for partial matching
        chunks = mode.get_pattern_chunks(pattern, min_len=4)
        close_candidates = mode.repository.get_close_pattern_rows(chunks, pattern, limit=1000)

        close_scored = []
        seen = set()

        # Score the close candidates by pattern similarity
        for item in close_candidates:
            score = mode.phone_pattern_similarity(pattern, item.digits)
            if score > 0:
                item.explanation = "similar numeric pattern"
                close_scored.append((score, item))
                seen.add(item.raw)

        # Sort close matches by pattern similarity score, and then by overall wor score
        close_scored.sort(key=lambda x: (x[0], mode.row_score(x[1])), reverse=True)
        ranked_close = [item for i, item in close_scored[:n]]

        # Make search broader, if not enough of close suggestions
        if len(ranked_close) < n:

            # Extra candidates
            extra_candidates = mode.repository.get_extra_rows(pattern, limit=500)

            extras_scored = []
            for item in extra_candidates:
                if item.raw in seen:
                    continue
                score = mode.phone_pattern_similarity(pattern, item.digits)
                if score > 0:
                    item.explanation = "similar numeric pattern"
                    extras_scored.append((score, item))
                    
            extras_scored.sort(key=lambda x: (x[0], mode.row_score(x[1])), reverse=True)

            # Add extra matches untill enough of suggestions
            for i, item in extras_scored:
                ranked_close.append(item)
                seen.add(item.raw)
                if len(ranked_close) >= n:
                    break

        result = (exact, ranked_close[:n])
        mode.search_cache[cache_key] = result
        return result
