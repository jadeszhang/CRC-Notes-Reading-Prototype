"""Run colonoscopy extraction on the input CSV."""

import csv

from call_model import call_model, get_client, load_prompt
from config import (
    DRY_RUN,
    ID_COLUMN,
    INPUT_CSV,
    NOTE_COLUMN,
    OUTPUT_CSV,
    OUTPUT_FIELDS,
    PROMPT_FILE,
)
from load_data import load_data
from parse_output import parse_output


def save_results(results, output_csv):
    """Save extracted results to a CSV file."""
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    with output_csv.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(results)


def run_extraction(input_csv, output_csv):
    """Load notes, call the model, parse results, and save output."""
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
    run_extraction(INPUT_CSV, OUTPUT_CSV)
