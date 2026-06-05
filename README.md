# CRC Notes Reading Prototype

This project is a small Python prototype for extracting colonoscopy information from short doctor-note fragments.

The main question is:

> Did the patient already have a colonoscopy? If yes, when?

The pipeline reads a CSV of note fragments, sends each note to the OpenAI API with a structured extraction prompt, saves model outputs to CSV, and evaluates those outputs against a synthetic labeled dataset.

## What We Built

- A sample synthetic dataset with 50 note fragments
- A prompt for colonoscopy-focused extraction
- A Python pipeline that loads data, calls the model, parses output, saves progress, and evaluates results
- Output files named by dataset ID and model name so different model runs can be compared
- Evaluation files that show the original note text, interpreted label, and model output side by side

## Project Structure

```text
CRC Notes Reading Prototype/
|
|-- input_data/
|   `-- sample_dataset_001.csv
|
|-- output_data/
|   |-- output_results_dataset_001_gpt-5-2.csv
|   |-- output_results_dataset_001_gpt-5-mini.csv
|   |-- evaluation_result_dataset_001_gpt-5-2.csv
|   `-- evaluation_result_dataset_001_gpt-5-mini.csv
|
|-- prompts/
|   `-- extraction_prompt.txt
|
|-- src/
|   |-- config.py
|   |-- load_data.py
|   |-- call_model.py
|   |-- parse_output.py
|   |-- run_extraction.py
|   `-- evaluate_results.py
|
`-- README.md
```

## Input Data

Input CSV files should go in `input_data/`.

The current sample file is:

```text
input_data/sample_dataset_001.csv
```

Required columns:

- `UID`
- `synthetic_doc_note_fragment`

The loader reads the latest CSV in `input_data/` by default, unless another file path is passed manually.

## Output Fields

The model returns these fields:

- `UID`
- `screening_mentioned`
- `procedure_done`
- `procedure_type`
- `procedure_status`
- `date_raw`
- `date_converted`
- `result`
- `confidence`
- `needs_human_review`
- `explanation`

For this prototype, `procedure_done` means whether colonoscopy was completed. Non-colonoscopy screening tests such as FIT or Cologuard may count as screening mentions, but they do not count as completed colonoscopy.

## Date Conversion Rule

The project keeps both:

- `date_raw`: the original date phrase from the note
- `date_converted`: the converted calendar date in `YYYY-MM-DD`

Approximate dates use default values from `src/config.py`.

Example:

```text
about 7 yrs ago -> 2019-01-01
```

This uses `REFERENCE_YEAR = 2026` and defaults unknown month/day to January 1.

## Model Settings

Model configuration lives in:

```text
src/config.py
```

Current model:

```python
OPENAI_MODEL = "gpt-5.2"
```

Other tested model:

```python
OPENAI_MODEL = "gpt-5-mini"
```

Output filenames include the model name, for example:

```text
output_results_dataset_001_gpt-5-2.csv
output_results_dataset_001_gpt-5-mini.csv
```

## Setup

Install the OpenAI Python package:

```powershell
pip install openai
```

Set your API key as an environment variable:

```powershell
$env:OPENAI_API_KEY = "your_api_key_here"
```

Do not paste the API key into the code.

## Run Extraction

From the project folder:

```powershell
python src/run_extraction.py
```

The script:

1. Finds the latest CSV in `input_data/`
2. Loads the extraction prompt
3. Calls the configured OpenAI model for each note
4. Saves results after every record
5. Writes a model-specific output CSV in `output_data/`

Saving after every record helps avoid wasting API budget if the script stops halfway.

## Run Evaluation

After extraction:

```powershell
python src/evaluate_results.py
```

The evaluator compares model output against the synthetic labels and writes a model-specific evaluation CSV.

Evaluation output columns:

- `UID`
- `original_text`
- `field`
- `interpreted`
- `actual`

`interpreted` means the simplified label derived from the synthetic dataset.  
`actual` means the model output.

## Current Evaluation Summary

For `sample_dataset_001.csv`, both saved model runs currently show:

```text
Evaluated records: 50
Colonoscopy done accuracy: 47/50
Date raw accuracy: 17/18
```

Current mismatches are saved in:

```text
output_data/evaluation_result_dataset_001_gpt-5-2.csv
output_data/evaluation_result_dataset_001_gpt-5-mini.csv
```

## Notes

- This is a prototype, not a clinical decision tool.
- The current focus is colonoscopy completion and colonoscopy date extraction.
- Real clinical notes may need additional preprocessing, stronger validation, and human review rules.
- Future datasets can be added to `input_data/` using names like `sample_dataset_002.csv`.
