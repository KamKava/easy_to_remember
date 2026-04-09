from pathlib import Path

class DictionaryRepository:
    # Initialize with path
    def __init__(self, path="data/dictionary/plate_dictionary.txt"):
        self.path = Path(path)

    # Open dictionary file, and read each line
    def load_words(self):
        with self.path.open(encoding="utf-8") as f:
            words = [w.strip().upper() for w in f if w.strip()]
        # Convert to a set to get rid of douplicates
        return list(set(words))
