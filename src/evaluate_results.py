"""Evaluate extraction results against the synthetic test set."""

import csv
import re

from config import (
    EVALUATION_RESULTS_PREFIX,
    ID_COLUMN,
    NOTE_COLUMN,
    OPENAI_MODEL,
    OUTPUT_DATA_DIR,
    OUTPUT_RESULTS_PREFIX,
)
from load_data import get_dataset_id, get_latest_input_csv


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
    if (
        expected_row["procedure_type"].lower() == "colonoscopy"
        and expected_row["procedure_done"] == "yes"
    ):
        return "yes"

    return "no"


def get_model_id(model_name):
    """Return a file-safe model name."""
    return re.sub(r"[^A-Za-z0-9]+", "-", model_name).strip("-").lower()


def get_output_csv(input_csv):
    """Build the extraction result path for an input dataset."""
    dataset_id = get_dataset_id(input_csv)
    model_id = get_model_id(OPENAI_MODEL)
    return OUTPUT_DATA_DIR / f"{OUTPUT_RESULTS_PREFIX}_{dataset_id}_{model_id}.csv"


def get_evaluation_csv(input_csv):
    """Build the evaluation result path for an input dataset."""
    dataset_id = get_dataset_id(input_csv)
    model_id = get_model_id(OPENAI_MODEL)
    return OUTPUT_DATA_DIR / f"{EVALUATION_RESULTS_PREFIX}_{dataset_id}_{model_id}.csv"


def save_evaluation_results(evaluation_rows, evaluation_csv):
    """Save evaluation mismatch rows to CSV."""
    evaluation_csv.parent.mkdir(parents=True, exist_ok=True)

    with evaluation_csv.open("w", encoding="utf-8", newline="") as file:
        fieldnames = ["UID", "original_text", "field", "interpreted", "actual"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(evaluation_rows)


def compare_field(uid, original_text, field, interpreted_value, actual_value):
    """Return a mismatch dictionary, or None if values match."""
    if interpreted_value == actual_value:
        return None

    return {
        "UID": uid,
        "original_text": original_text,
        "field": field,
        "interpreted": interpreted_value,
        "actual": actual_value,
    }


def evaluate_results(expected_csv=None, actual_csv=None, evaluation_csv=None):
    """Compare output results with the synthetic expected labels."""
    if expected_csv is None:
        expected_csv = get_latest_input_csv()

    if actual_csv is None:
        actual_csv = get_output_csv(expected_csv)

    if evaluation_csv is None:
        evaluation_csv = get_evaluation_csv(expected_csv)

    expected_rows = load_csv_by_uid(expected_csv)
    actual_rows = load_csv_by_uid(actual_csv)

    mismatches = []
    total_records = 0
    correct_colonoscopy_done = 0
    correct_date_raw = 0
    date_records = 0

    for uid, expected_row in expected_rows.items():
        actual_row = actual_rows.get(uid)
        original_text = expected_row[NOTE_COLUMN]

        if actual_row is None:
            mismatches.append(
                {
                    "UID": uid,
                    "original_text": original_text,
                    "field": "record",
                    "interpreted": "present",
                    "actual": "missing",
                }
            )
            continue

        total_records += 1

        expected_done = expected_colonoscopy_done(expected_row)
        actual_done = actual_row["procedure_done"]

        mismatch = compare_field(
            uid,
            original_text,
            "procedure_done",
            expected_done,
            actual_done,
        )
        if mismatch:
            mismatches.append(mismatch)
        else:
            correct_colonoscopy_done += 1

        if expected_done == "yes":
            date_records += 1
            expected_date = expected_row["date_raw"]
            actual_date = actual_row["date_raw"]

            mismatch = compare_field(
                uid,
                original_text,
                "date_raw",
                expected_date,
                actual_date,
            )
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

    save_evaluation_results(mismatches, evaluation_csv)
    print(f"Saved evaluation results to {evaluation_csv}")
    print()

    if not mismatches:
        print("No mismatches found.")
        return

    print("Mismatches:")
    for mismatch in mismatches:
        print(
            f"{mismatch['UID']} | {mismatch['field']} | "
            f"interpreted: {mismatch['interpreted']} | actual: {mismatch['actual']}"
        )


if __name__ == "__main__":
    evaluate_results()
