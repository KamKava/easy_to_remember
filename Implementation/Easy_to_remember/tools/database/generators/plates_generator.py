#Different type of licences have been produced in different
#amounts. Weights are given to showcase the uneven amounts.
# New style (2001 - present) - 70%
# Prefix (1983 - 2001) - 20%
# Suffix (1963 - 1983) - 8%
# Dateless (pre-1963) - 2%

import csv
import random
import string
from pathlib import Path

plate_records = 100000

# Letters IOQUZ are mostly not used in uk number plates, so they will not be used.
LETTERS = [c for c in string.ascii_uppercase if c not in "IOQUZ"]

AVAILABLE_LETTERS = list("ABCDEFGHJKLMNPRSTVWXY")

# Set availability to 30% of dataset entries, and 70% for taken
def availability():
    return random.choices(["taken", "available"], weights=[0.7, 0.3], k=1)[0]

# Dateless plates
def dateless_plate():
    letters = "".join(random.choices(LETTERS, k=random.randint(1, 3)))
    digits = "".join(str(random.randint(0, 9)) for _ in range(random.randint(1, 4)))
    return f"{digits} {letters}" if random.random() < 0.5 else f"{letters} {digits}"

# Suffix plates
def suffix_plate():
    area = "".join(random.choices(AVAILABLE_LETTERS, k=3))
    number = random.randint(1, 999)
    suffix = random.choice(AVAILABLE_LETTERS)
    return f"{area} {number} {suffix}"

# Prefix plates
def prefix_plate():
    prefix = random.choice(AVAILABLE_LETTERS)
    number = random.randint(1, 999)
    area = "".join(random.choices(LETTERS, k=3))
    return f"{prefix} {number} {area}"

# New style plates
def new_style_plate():
    area = "".join(random.choices(LETTERS, k=2))
    year = random.choice([f"{y:02d}" for y in range (1, 100)])
    random_letters = "".join(random.choices(LETTERS, k=3))
    return f"{area} {year} {random_letters}"


# Generate a plate and use weights
def generate_plate():
    plate_type = random.choices(
        ["new", "prefix", "suffix", "dateless"],
        weights = [70, 20, 8, 2],
        k = 1
    )[0]

    if plate_type == "new":
        return new_style_plate(), "new"
    if plate_type == "prefix":
        return prefix_plate(), "prefix"
    if plate_type == "suffix":
        return suffix_plate(), "suffix"
    return dateless_plate(), "dateless"


Path("data").mkdir(exist_ok=True)

# Write the data into the csv file
with open("data/csv/uk_number_plates.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["plate", "type", "availability"])

    for i in range(plate_records):
        plate, plate_type = generate_plate()
        writer.writerow([plate, plate_type, availability()])
        if i % 1000000 == 0:
            print(i)

print("Done!")