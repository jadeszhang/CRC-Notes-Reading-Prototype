"""Load input notes for colonoscopy extraction."""

import csv
import re

from config import ID_COLUMN, INPUT_DATA_DIR, NOTE_COLUMN


def get_latest_input_csv(input_data_dir=INPUT_DATA_DIR):
    """Return the most recently modified CSV in the input data folder."""
    csv_files = list(input_data_dir.glob("*.csv"))
    csv_files.sort(key=lambda path: path.stat().st_mtime, reverse=True)

    return csv_files[0]


def get_dataset_id(input_csv):
    """Extract dataset ID from a file name like sample_dataset_001.csv."""
    match = re.search(r"(dataset_\d+)", input_csv.stem)

    if match:
        return match.group(1)

    return input_csv.stem


def load_data(input_csv=None):
    """Load UID and note text from the input CSV."""
    if input_csv is None:
        input_csv = get_latest_input_csv()

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
    notes = load_data()

    for note in notes:
        print(note)
        print()
