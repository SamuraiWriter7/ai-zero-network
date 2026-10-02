#!/usr/bin/env python3

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]

TRACE_SCHEMA_PATH = ROOT / "schemas" / "trace-v0.1.schema.json"
RECEIPT_SCHEMA_PATH = ROOT / "schemas" / "receipt-v0.1.schema.json"

PASS_DIR = ROOT / "examples" / "v0.1" / "pass"
FAIL_DIR = ROOT / "examples" / "v0.1" / "fail"


def load_json(path: Path) -> dict:
    """Load a JSON file."""
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_validator(schema_path: Path) -> Draft202012Validator:
    """Create a Draft 2020-12 validator with format checking enabled."""
    schema = load_json(schema_path)

    Draft202012Validator.check_schema(schema)

    return Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    )


def detect_document_type(data: dict) -> str:
    """
    Detect whether an example is a Trace or Receipt.

    Receipt is identified by receipt_id.
    Trace is identified by trace_id without receipt_id.
    """
    if "receipt_id" in data:
        return "receipt"

    if "trace_id" in data:
        return "trace"

    raise ValueError(
        "Unable to determine document type: "
        "expected 'trace_id' or 'receipt_id'."
    )


def validate_document(
    path: Path,
    trace_validator: Draft202012Validator,
    receipt_validator: Draft202012Validator,
):
    """Validate one example and return document type and errors."""
    data = load_json(path)
    document_type = detect_document_type(data)

    if document_type == "trace":
        validator = trace_validator
    else:
        validator = receipt_validator

    errors = sorted(
        validator.iter_errors(data),
        key=lambda error: list(error.absolute_path),
    )

    return document_type, errors


def format_error(error) -> str:
    """Return a readable validation error."""
    if error.absolute_path:
        location = ".".join(str(part) for part in error.absolute_path)
    else:
        location = "<root>"

    return f"{location}: {error.message}"


def validate_pass_examples(
    trace_validator: Draft202012Validator,
    receipt_validator: Draft202012Validator,
) -> int:
    """
    Every example in pass/ MUST validate successfully.
    """
    failures = 0

    print("\n=== PASS examples ===")

    files = sorted(PASS_DIR.glob("*.json"))

    if not files:
        print(f"[ERROR] No PASS examples found in {PASS_DIR}")
        return 1

    for path in files:
        try:
            document_type, errors = validate_document(
                path,
                trace_validator,
                receipt_validator,
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
    trace_validator: Draft202012Validator,
    receipt_validator: Draft202012Validator,
) -> int:
    """
    Every example in fail/ MUST be rejected by its schema.
    """
    failures = 0

    print("\n=== FAIL examples ===")

    files = sorted(FAIL_DIR.glob("*.json"))

    if not files:
        print(f"[ERROR] No FAIL examples found in {FAIL_DIR}")
        return 1

    for path in files:
        try:
            document_type, errors = validate_document(
                path,
                trace_validator,
                receipt_validator,
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
            # A malformed or unclassifiable file is also rejected.
            print(
                f"[PASS] {path.relative_to(ROOT)} "
                f"correctly rejected"
            )
            print(f"       - {exc}")

    return failures


def main() -> int:
    print("AI Zero Network v0.1 validator")
    print("==============================")

    required_paths = [
        TRACE_SCHEMA_PATH,
        RECEIPT_SCHEMA_PATH,
        PASS_DIR,
        FAIL_DIR,
    ]

    for path in required_paths:
        if not path.exists():
            print(f"[ERROR] Required path does not exist: {path}")
            return 1

    try:
        trace_validator = load_validator(TRACE_SCHEMA_PATH)
        receipt_validator = load_validator(RECEIPT_SCHEMA_PATH)
    except Exception as exc:
        print(f"[ERROR] Failed to load schema: {exc}")
        return 1

    failures = 0

    failures += validate_pass_examples(
        trace_validator,
        receipt_validator,
    )

    failures += validate_fail_examples(
        trace_validator,
        receipt_validator,
    )

    print("\n=== Result ===")

    if failures:
        print(f"FAILED: {failures} validation expectation(s) failed.")
        return 1

    print("PASS: all v0.1 examples behaved as expected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
