
"""
A class for generating phone numbers
Rules:
* Starts with 07
* Then 9 more digits
* Has a space after first 5 characters
"""
import csv
import random
from pathlib import Path

# Amount of records
NUM_RECORDS = 10000000

def uk_mobile():
    number = "07" + "".join(str(random.randint(0, 9)) for i in range(9))
    return f"{number[:5]} {number[5:]}"

# Availability status assign 70% taken, 30% available
def availability():
    return random.choices(["taken", "available"], weights=[0.7, 0.3], k=1)[0]


Path("data").mkdir(exist_ok=True)

# In csv file generate the numbers and write them in to the file
with open("data/csv/uk_phone_numbers.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["phone_number", "availability"])

    for i in range(NUM_RECORDS):
        writer.writerow([uk_mobile(), availability()])

print("Done!")
