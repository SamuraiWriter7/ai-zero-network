#!/usr/bin/env python3

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]

AUTHORITY_SCHEMA_PATH = ROOT / "schemas" / "authority-v0.2.schema.json"

PASS_DIR = ROOT / "examples" / "v0.2" / "pass"
FAIL_DIR = ROOT / "examples" / "v0.2" / "fail"


def load_json(path: Path) -> dict:
    """Load a JSON document."""
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_validator(schema_path: Path) -> Draft202012Validator:
    """
    Load and validate the Authority v0.2 schema,
    then return a Draft 2020-12 validator.
    """
    schema = load_json(schema_path)

    Draft202012Validator.check_schema(schema)

    return Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    )


def format_error(error) -> str:
    """Return a compact human-readable validation error."""
    if error.absolute_path:
        location = ".".join(str(part) for part in error.absolute_path)
    else:
        location = "<root>"

    return f"{location}: {error.message}"


def validate_file(
    path: Path,
    validator: Draft202012Validator,
):
    """
    Validate one Authority Record.
    Returns a sorted list of schema errors.
    """
    data = load_json(path)

    return sorted(
        validator.iter_errors(data),
        key=lambda error: list(error.absolute_path),
    )


def validate_pass_examples(
    validator: Draft202012Validator,
) -> int:
    """
    Every file in examples/v0.2/pass MUST validate successfully.
    """
    failures = 0

    print("\n=== v0.2 PASS examples ===")

    files = sorted(PASS_DIR.glob("*.json"))

    if not files:
        print(f"[ERROR] No PASS examples found in {PASS_DIR}")
        return 1

    for path in files:
        try:
            errors = validate_file(path, validator)

            if errors:
                failures += 1

                print(
                    f"[FAIL] {path.relative_to(ROOT)} "
                    f"was expected to PASS"
                )

                for error in errors:
                    print(f"       - {format_error(error)}")
            else:
                print(
                    f"[PASS] {path.relative_to(ROOT)}"
                )

        except (json.JSONDecodeError, OSError, ValueError) as exc:
            failures += 1

            print(f"[FAIL] {path.relative_to(ROOT)}")
            print(f"       - {exc}")

    return failures


def validate_fail_examples(
    validator: Draft202012Validator,
) -> int:
    """
    Every file in examples/v0.2/fail MUST be rejected by the schema.
    """
    failures = 0

    print("\n=== v0.2 FAIL examples ===")

    files = sorted(FAIL_DIR.glob("*.json"))

    if not files:
        print(f"[ERROR] No FAIL examples found in {FAIL_DIR}")
        return 1

    for path in files:
        try:
            errors = validate_file(path, validator)

            if errors:
                print(
                    f"[PASS] {path.relative_to(ROOT)} "
                    f"correctly rejected"
                )

                for error in errors:
                    print(f"       - {format_error(error)}")

            else:
                failures += 1

                print(
                    f"[FAIL] {path.relative_to(ROOT)} "
                    f"was expected to FAIL "
                    f"but validated successfully"
                )

        except (json.JSONDecodeError, OSError, ValueError) as exc:
            # A malformed JSON file is rejected, but keep the reason visible.
            print(
                f"[PASS] {path.relative_to(ROOT)} "
                f"correctly rejected"
            )
            print(f"       - {exc}")

    return failures


def main() -> int:
    print("AI Zero Network v0.2 Authority schema validator")
    print("===============================================")

    required_paths = [
        AUTHORITY_SCHEMA_PATH,
        PASS_DIR,
        FAIL_DIR,
    ]

    for path in required_paths:
        if not path.exists():
            print(f"[ERROR] Required path does not exist: {path}")
            return 1

    try:
        validator = load_validator(AUTHORITY_SCHEMA_PATH)
    except Exception as exc:
        print(f"[ERROR] Failed to load Authority v0.2 schema: {exc}")
        return 1

    failures = 0

    failures += validate_pass_examples(validator)
    failures += validate_fail_examples(validator)

    print("\n=== Result ===")

    if failures:
        print(
            f"FAILED: {failures} v0.2 validation "
            f"expectation(s) failed."
        )
        return 1

    print(
        "PASS: all AI Zero Network v0.2 Authority "
        "examples behaved as expected."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
