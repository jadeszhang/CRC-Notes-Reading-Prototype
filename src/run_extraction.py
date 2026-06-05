"""Run colonoscopy extraction on the input CSV."""

import csv
import re

from call_model import call_model, get_client, load_prompt
from config import (
    DRY_RUN,
    ID_COLUMN,
    NOTE_COLUMN,
    OPENAI_MODEL,
    OUTPUT_DATA_DIR,
    OUTPUT_FIELDS,
    OUTPUT_RESULTS_PREFIX,
    PROMPT_FILE,
)
from load_data import get_dataset_id, get_latest_input_csv, load_data
from parse_output import parse_output


def save_results(results, output_csv):
    """Save extracted results to a CSV file."""
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    with output_csv.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(results)


def get_model_id(model_name):
    """Return a file-safe model name."""
    return re.sub(r"[^A-Za-z0-9]+", "-", model_name).strip("-").lower()


def get_output_csv(input_csv):
    """Build an output file path using the input dataset ID and model."""
    dataset_id = get_dataset_id(input_csv)
    model_id = get_model_id(OPENAI_MODEL)
    return OUTPUT_DATA_DIR / f"{OUTPUT_RESULTS_PREFIX}_{dataset_id}_{model_id}.csv"


def run_extraction(input_csv=None, output_csv=None):
    """Load notes, call the model, parse results, and save output."""
    if input_csv is None:
        input_csv = get_latest_input_csv()

    if output_csv is None:
        output_csv = get_output_csv(input_csv)

    notes = load_data(input_csv)
    prompt = load_prompt(PROMPT_FILE)
    client = None if DRY_RUN else get_client()
    results = []

    total_notes = len(notes)

    for index, note in enumerate(notes, start=1):
        uid = note[ID_COLUMN]
        note_text = note[NOTE_COLUMN]

        print(f"Processing {index}/{total_notes}: {uid}")
        model_output = call_model(note_text, prompt, client=client)
        results.append(parse_output(uid, model_output))

        save_results(results, output_csv)

    print(f"Saved {len(results)} results to {output_csv}")


if __name__ == "__main__":
    run_extraction()
