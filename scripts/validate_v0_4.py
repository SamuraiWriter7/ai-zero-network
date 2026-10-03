#!/usr/bin/env python3

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]

FIELD_DELTA_SCHEMA_PATH = ROOT / "schemas" / "field-delta-v0.4.schema.json"
REGION_FLOW_SCHEMA_PATH = ROOT / "schemas" / "region-flow-v0.4.schema.json"

PASS_DIR = ROOT / "examples" / "v0.4" / "pass"
FAIL_DIR = ROOT / "examples" / "v0.4" / "fail"


def load_json(path: Path) -> dict:
    """Load JSON from a file."""
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_validator(schema_path: Path) -> Draft202012Validator:
    """Load and validate a Draft 2020-12 JSON Schema."""
    schema = load_json(schema_path)

    Draft202012Validator.check_schema(schema)

    return Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    )


def detect_document_type(data: dict) -> str:
    """
    Detect whether the document is a Field Delta or Region Flow.

    Field Delta:
      delta_id

    Region Flow:
      flow_id
    """
    if "delta_id" in data:
        return "field_delta"

    if "flow_id" in data:
        return "region_flow"

    raise ValueError(
        "Unable to determine v0.4 document type: "
        "expected 'delta_id' or 'flow_id'."
    )


def format_error(error) -> str:
    """Format a jsonschema error for readable CLI output."""
    if error.absolute_path:
        location = ".".join(str(part) for part in error.absolute_path)
    else:
        location = "<root>"

    return f"{location}: {error.message}"


def validate_document(
    path: Path,
    field_delta_validator: Draft202012Validator,
    region_flow_validator: Draft202012Validator,
):
    """
    Validate one v0.4 example using the appropriate schema.

    Returns:
      (document_type, errors)
    """
    data = load_json(path)
    document_type = detect_document_type(data)

    if document_type == "field_delta":
        validator = field_delta_validator
    else:
        validator = region_flow_validator

    errors = sorted(
        validator.iter_errors(data),
        key=lambda error: list(error.absolute_path),
    )

    return document_type, errors


def validate_pass_examples(
    field_delta_validator: Draft202012Validator,
    region_flow_validator: Draft202012Validator,
) -> int:
    """
    Every JSON file in examples/v0.4/pass MUST validate.
    """
    failures = 0

    print("\n=== v0.4 PASS examples ===")

    files = sorted(PASS_DIR.glob("*.json"))

    if not files:
        print(f"[ERROR] No PASS examples found in {PASS_DIR}")
        return 1

    for path in files:
        try:
            document_type, errors = validate_document(
                path,
                field_delta_validator,
                region_flow_validator,
            )

            if errors:
                failures += 1

                print(
                    f"[FAIL] {path.relative_to(ROOT)} "
                    f"({document_type}) was expected to PASS"
                )

                for error in errors:
                    print(f"       - {format_error(error)}")

            else:
                print(
                    f"[PASS] {path.relative_to(ROOT)} "
                    f"({document_type})"
                )

        except (json.JSONDecodeError, OSError, ValueError) as exc:
            failures += 1

            print(f"[FAIL] {path.relative_to(ROOT)}")
            print(f"       - {exc}")

    return failures


def validate_fail_examples(
    field_delta_validator: Draft202012Validator,
    region_flow_validator: Draft202012Validator,
) -> int:
    """
    Every JSON file in examples/v0.4/fail MUST be rejected.
    """
    failures = 0

    print("\n=== v0.4 FAIL examples ===")

    files = sorted(FAIL_DIR.glob("*.json"))

    if not files:
        print(f"[ERROR] No FAIL examples found in {FAIL_DIR}")
        return 1

    for path in files:
        try:
            document_type, errors = validate_document(
                path,
                field_delta_validator,
                region_flow_validator,
            )

            if errors:
                print(
                    f"[PASS] {path.relative_to(ROOT)} "
                    f"({document_type}) correctly rejected"
                )

                for error in errors:
                    print(f"       - {format_error(error)}")

            else:
                failures += 1

                print(
                    f"[FAIL] {path.relative_to(ROOT)} "
                    f"({document_type}) was expected to FAIL "
                    f"but validated successfully"
                )

        except (json.JSONDecodeError, OSError, ValueError) as exc:
            print(
                f"[PASS] {path.relative_to(ROOT)} "
                f"correctly rejected"
            )
            print(f"       - {exc}")

    return failures


def main() -> int:
    print("AI Zero Network v0.4 schema validator")
    print("=====================================")

    required_paths = [
        FIELD_DELTA_SCHEMA_PATH,
        REGION_FLOW_SCHEMA_PATH,
        PASS_DIR,
        FAIL_DIR,
    ]

    for path in required_paths:
        if not path.exists():
            print(f"[ERROR] Required path does not exist: {path}")
            return 1

    try:
        field_delta_validator = load_validator(
            FIELD_DELTA_SCHEMA_PATH
        )

        region_flow_validator = load_validator(
            REGION_FLOW_SCHEMA_PATH
        )

    except Exception as exc:
        print(f"[ERROR] Failed to load v0.4 schema: {exc}")
        return 1

    failures = 0

    failures += validate_pass_examples(
        field_delta_validator,
        region_flow_validator,
    )

    failures += validate_fail_examples(
        field_delta_validator,
        region_flow_validator,
    )

    print("\n=== Result ===")

    if failures:
        print(
            f"FAILED: {failures} v0.4 schema validation "
            f"expectation(s) failed."
        )
        return 1

    print(
        "PASS: all AI Zero Network v0.4 "
        "Field Delta and Region Flow examples "
        "behaved as expected."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
