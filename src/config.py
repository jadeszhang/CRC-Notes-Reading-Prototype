"""Project configuration for colorectal cancer screening NLP extraction.

This file should contain settings only. Do not put extraction logic here.
"""

from pathlib import Path


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
PROMPTS_DIR = PROJECT_ROOT / "prompts"

INPUT_CSV = DATA_DIR / "synthetic_colo_doc_notes_test_set.csv"
OUTPUT_CSV = DATA_DIR / "output_results.csv"
PROMPT_FILE = PROMPTS_DIR / "extraction_prompt.txt"


# Input columns
ID_COLUMN = "UID"
NOTE_COLUMN = "synthetic_doc_note_fragment"


# OpenAI API settings
OPENAI_API_KEY_ENV = "OPENAI_API_KEY"
OPENAI_MODEL = "gpt-5-mini"
REQUEST_TIMEOUT_SECONDS = 60
MAX_RETRIES = 3


# Date conversion settings
REFERENCE_YEAR = 2026
DEFAULT_MONTH = 1
DEFAULT_DAY = 1
DATE_FORMAT = "%Y-%m-%d"


# Expected extraction fields
OUTPUT_FIELDS = [
    "UID",
    "screening_mentioned",
    "procedure_done",
    "procedure_type",
    "procedure_status",
    "date_raw",
    "date_converted",
    "result",
    "confidence",
    "needs_human_review",
    "explanation",
]


# Allowed label values. These should match the prompt and evaluation logic.
YES_NO_VALUES = ["yes", "no"]

PROCEDURE_TYPES = [
    "colonoscopy",
    "unknown",
]

CONFIDENCE_VALUES = ["high", "medium", "low"]
