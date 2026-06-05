"""Call the OpenAI model for colonoscopy extraction."""

import json
import os

from config import (
    CONFIDENCE_VALUES,
    DATE_FORMAT,
    DEFAULT_DAY,
    DEFAULT_MONTH,
    DRY_RUN,
    OPENAI_API_KEY_ENV,
    OPENAI_MODEL,
    OUTPUT_FIELDS,
    PROCEDURE_TYPES,
    PROMPT_FILE,
    REFERENCE_YEAR,
    REQUEST_TIMEOUT_SECONDS,
    MAX_RETRIES,
    YES_NO_VALUES,
)


def load_prompt(prompt_file):
    """Load the extraction prompt from a text file."""
    return prompt_file.read_text(encoding="utf-8")


def get_client():
    """Create the OpenAI client."""
    from openai import OpenAI

    return OpenAI(
        api_key=os.getenv(OPENAI_API_KEY_ENV),
        timeout=REQUEST_TIMEOUT_SECONDS,
        max_retries=MAX_RETRIES,
    )


def get_output_schema():
    """Define the JSON structure we want the model to return."""
    return {
        "type": "object",
        "properties": {
            "screening_mentioned": {"type": "string", "enum": YES_NO_VALUES},
            "procedure_done": {"type": "string", "enum": YES_NO_VALUES},
            "procedure_type": {"type": "string", "enum": PROCEDURE_TYPES},
            "procedure_status": {"type": "string"},
            "date_raw": {"type": "string"},
            "date_converted": {"type": "string"},
            "result": {"type": "string"},
            "confidence": {"type": "string", "enum": CONFIDENCE_VALUES},
            "needs_human_review": {"type": "string", "enum": YES_NO_VALUES},
            "explanation": {"type": "string"},
        },
        "required": [field for field in OUTPUT_FIELDS if field != "UID"],
        "additionalProperties": False,
    }


def call_model(note_text, prompt_text, client=None):
    """Send one note sentence to the model and return extracted fields."""
    if DRY_RUN:
        return {
            "screening_mentioned": "no",
            "procedure_done": "no",
            "procedure_type": "unknown",
            "procedure_status": "dry_run",
            "date_raw": "",
            "date_converted": "",
            "result": "unknown",
            "confidence": "low",
            "needs_human_review": "yes",
            "explanation": "Dry run enabled; no API call was made.",
        }

    if client is None:
        client = get_client()

    user_input = {
        "note_text": note_text,
        "reference_year": REFERENCE_YEAR,
        "default_month": DEFAULT_MONTH,
        "default_day": DEFAULT_DAY,
        "date_format": DATE_FORMAT,
    }

    response = client.responses.create(
        model=OPENAI_MODEL,
        instructions=prompt_text,
        input=json.dumps(user_input),
        text={
            "format": {
                "type": "json_schema",
                "name": "colonoscopy_extraction",
                "schema": get_output_schema(),
                "strict": True,
            }
        },
    )

    return json.loads(response.output_text)


if __name__ == "__main__":
    prompt = load_prompt(PROMPT_FILE)
    sample_note = 'last colonoscopy about 7 yrs ago, "ok" per patient'
    result = call_model(sample_note, prompt)
    print(result)
