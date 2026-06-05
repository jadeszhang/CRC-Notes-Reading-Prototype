"""Prepare model outputs for saving."""

from config import OUTPUT_FIELDS


def parse_output(uid, model_output):
    """Add UID and keep output fields in the configured order."""
    parsed_output = {"UID": uid}

    for field in OUTPUT_FIELDS:
        if field == "UID":
            continue

        parsed_output[field] = model_output.get(field, "")

    return parsed_output


def parse_outputs(records):
    """Parse a list of records that already contain UID and model output."""
    parsed_records = []

    for record in records:
        parsed_records.append(
            parse_output(
                uid=record["UID"],
                model_output=record["model_output"],
            )
        )

    return parsed_records


if __name__ == "__main__":
    sample_model_output = {
        "screening_mentioned": "yes",
        "procedure_done": "yes",
        "procedure_type": "colonoscopy",
        "procedure_status": "completed",
        "date_raw": "about 7 yrs ago",
        "date_converted": "2019-01-01",
        "result": "normal_vague",
        "confidence": "medium",
        "needs_human_review": "yes",
        "explanation": "Patient reported a prior colonoscopy about 7 years ago.",
    }

    print(parse_output("T005", sample_model_output))
