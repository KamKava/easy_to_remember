""" A class for cleaning the plate dictionary
Rules:
* Only alphabetic words
* Letters I and Q are not allowed
* repeated letters are removed
* length 2 - 7 characters
"""

import pandas as pd  

# Paths
input_file = "data/raw_words.csv"
output_file = "data/plate_dictionary.txt"

# Global variables
# naming the column which contains the words
word_column = "headword"
max_length = 7
not_allowed = {"I", "Q"}

# Read the csv file
print("Loading dictionary")
df = pd.read_csv(input_file)

# Check that the column exists
if word_column not in df.columns:
    print("Columns found: ", df.columns)
    raise ValueError("Adjust column name")

# Get column as strings
words = df[word_column].astype(str)
print("Total words in raw file:", len(words))

# Cleaning
# Returns true if word passes filtering rules
def valid_word(word):
    word = word.strip().upper()

    if len(word) == 0:
        return False
    if len(word) > max_length:
        return False
    if not word.isalpha():
        return False
    if any(letter in not_allowed for letter in word):
        return False
    if len(set(word)) == 1 and len(word) > 2:
        return False
    if len(word) < 2:
        return False
    return True

# Build a list from clean words        
cleaned_words = [
    w.strip().upper()
    for w in words
    if valid_word(w)
]

# No douplicates
cleaned_words = sorted(set(cleaned_words))

print("After cleaning: ", len(cleaned_words), " words.")

# Save to file
with open(output_file, "w") as f:
    for w in cleaned_words:
        f.write(w + "\n")

print("Clean dictionary saved to: ", output_file)