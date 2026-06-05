"""Evaluate extraction results against the synthetic test set."""

import csv

from config import ID_COLUMN, INPUT_CSV, OUTPUT_CSV


def load_csv_by_uid(csv_path):
    """Load a CSV into a dictionary keyed by UID."""
    rows_by_uid = {}

    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            rows_by_uid[row[ID_COLUMN]] = row

    return rows_by_uid


def expected_colonoscopy_done(expected_row):
    """Convert the synthetic labels into the simplified colonoscopy-only target."""
    if expected_row["procedure_type"].lower() == "colonoscopy":
        return expected_row["procedure_done"]

    return "no"


def compare_field(uid, field, expected_value, actual_value):
    """Return a mismatch dictionary, or None if values match."""
    if expected_value == actual_value:
        return None

    return {
        "UID": uid,
        "field": field,
        "expected": expected_value,
        "actual": actual_value,
    }


def evaluate_results(expected_csv, actual_csv):
    """Compare output results with the synthetic expected labels."""
    expected_rows = load_csv_by_uid(expected_csv)
    actual_rows = load_csv_by_uid(actual_csv)

    mismatches = []
    total_records = 0
    correct_colonoscopy_done = 0
    correct_date_raw = 0
    date_records = 0

    for uid, expected_row in expected_rows.items():
        actual_row = actual_rows.get(uid)

        if actual_row is None:
            mismatches.append(
                {
                    "UID": uid,
                    "field": "record",
                    "expected": "present",
                    "actual": "missing",
                }
            )
            continue

        total_records += 1

        expected_done = expected_colonoscopy_done(expected_row)
        actual_done = actual_row["procedure_done"]

        mismatch = compare_field(uid, "procedure_done", expected_done, actual_done)
        if mismatch:
            mismatches.append(mismatch)
        else:
            correct_colonoscopy_done += 1

        if expected_done == "yes":
            date_records += 1
            expected_date = expected_row["date_raw"]
            actual_date = actual_row["date_raw"]

            mismatch = compare_field(uid, "date_raw", expected_date, actual_date)
            if mismatch:
                mismatches.append(mismatch)
            else:
                correct_date_raw += 1

    print(f"Evaluated records: {total_records}")
    print(
        "Colonoscopy done accuracy: "
        f"{correct_colonoscopy_done}/{total_records}"
    )
    print(f"Date raw accuracy: {correct_date_raw}/{date_records}")
    print()

    if not mismatches:
        print("No mismatches found.")
        return

    print("Mismatches:")
    for mismatch in mismatches:
        print(
            f"{mismatch['UID']} | {mismatch['field']} | "
            f"expected: {mismatch['expected']} | actual: {mismatch['actual']}"
        )


if __name__ == "__main__":
    evaluate_results(INPUT_CSV, OUTPUT_CSV)
