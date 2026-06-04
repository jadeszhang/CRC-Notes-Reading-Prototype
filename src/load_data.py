"""Load input notes for colonoscopy extraction."""

import csv

from config import ID_COLUMN, INPUT_CSV, NOTE_COLUMN


def load_data(input_csv):
    """Load UID and note text from the input CSV."""
    records = []

    with input_csv.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            records.append(
                {
                    ID_COLUMN: row[ID_COLUMN],
                    NOTE_COLUMN: row[NOTE_COLUMN],
                }
            )

    return records


if __name__ == "__main__":
    notes = load_data(INPUT_CSV)

    for note in notes:
        print(note)
        print()
