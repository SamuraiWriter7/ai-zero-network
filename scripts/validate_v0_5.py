#!/usr/bin/env python3

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]

BOUNDARY_GRADIENT_SCHEMA_PATH = (
    ROOT / "schemas" / "boundary-gradient-v0.5.schema.json"
)

FRONT_CANDIDATE_SCHEMA_PATH = (
    ROOT / "schemas" / "front-candidate-v0.5.schema.json"
)

PASS_DIR = ROOT / "examples" / "v0.5" / "pass"
FAIL_DIR = ROOT / "examples" / "v0.5" / "fail"


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_validator(
    schema_path: Path,
) -> Draft202012Validator:
    schema = load_json(schema_path)

    Draft202012Validator.check_schema(schema)

    return Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    )


def detect_document_type(data: dict) -> str:
    """
    Detect the v0.5 object type.

    Boundary Gradient:
      gradient_id

    Front Candidate:
      candidate_id
    """

    if "gradient_id" in data:
        return "boundary_gradient"

    if "candidate_id" in data:
        return "front_candidate"

    raise ValueError(
        "Unable to determine v0.5 document type: "
        "expected 'gradient_id' or 'candidate_id'."
    )


def format_error(error) -> str:
    if error.absolute_path:
        location = ".".join(
            str(part)
            for part in error.absolute_path
        )
    else:
        location = "<root>"

    return f"{location}: {error.message}"


def validate_document(
    path: Path,
    boundary_gradient_validator: Draft202012Validator,
    front_candidate_validator: Draft202012Validator,
):
    data = load_json(path)
    document_type = detect_document_type(data)

    if document_type == "boundary_gradient":
        validator = boundary_gradient_validator
    else:
        validator = front_candidate_validator

    errors = sorted(
        validator.iter_errors(data),
        key=lambda error: list(error.absolute_path),
    )

    return document_type, errors


def validate_pass_examples(
    boundary_gradient_validator: Draft202012Validator,
    front_candidate_validator: Draft202012Validator,
) -> int:
    failures = 0

    print("\n=== v0.5 PASS examples ===")

    files = sorted(PASS_DIR.glob("*.json"))

    if not files:
        print(
            f"[ERROR] No PASS examples found in {PASS_DIR}"
        )
        return 1

    for path in files:
        try:
            document_type, errors = validate_document(
                path,
                boundary_gradient_validator,
                front_candidate_validator,
            )

            if errors:
                failures += 1

                print(
                    f"[FAIL] {path.relative_to(ROOT)} "
                    f"({document_type}) was expected to PASS"
                )

                for error in errors:
                    print(
                        f"       - {format_error(error)}"
                    )

            else:
                print(
                    f"[PASS] {path.relative_to(ROOT)} "
                    f"({document_type})"
                )

        except (
            json.JSONDecodeError,
            OSError,
            ValueError,
        ) as exc:
            failures += 1

            print(
                f"[FAIL] {path.relative_to(ROOT)}"
            )
            print(
                f"       - {exc}"
            )

    return failures


def validate_fail_examples(
    boundary_gradient_validator: Draft202012Validator,
    front_candidate_validator: Draft202012Validator,
) -> int:
    failures = 0

    print("\n=== v0.5 FAIL examples ===")

    files = sorted(FAIL_DIR.glob("*.json"))

    if not files:
        print(
            f"[ERROR] No FAIL examples found in {FAIL_DIR}"
        )
        return 1

    for path in files:
        try:
            document_type, errors = validate_document(
                path,
                boundary_gradient_validator,
                front_candidate_validator,
            )

            if errors:
                print(
                    f"[PASS] {path.relative_to(ROOT)} "
                    f"({document_type}) correctly rejected"
                )

                for error in errors:
                    print(
                        f"       - {format_error(error)}"
                    )

            else:
                failures += 1

                print(
                    f"[FAIL] {path.relative_to(ROOT)} "
                    f"({document_type}) was expected to FAIL "
                    f"but validated successfully"
                )

        except (
            json.JSONDecodeError,
            OSError,
            ValueError,
        ) as exc:
            print(
                f"[PASS] {path.relative_to(ROOT)} "
                f"correctly rejected"
            )
            print(
                f"       - {exc}"
            )

    return failures


def main() -> int:
    print("AI Zero Network v0.5 schema validator")
    print("=====================================")

    required_paths = [
        BOUNDARY_GRADIENT_SCHEMA_PATH,
        FRONT_CANDIDATE_SCHEMA_PATH,
        PASS_DIR,
        FAIL_DIR,
    ]

    for path in required_paths:
        if not path.exists():
            print(
                f"[ERROR] Required path does not exist: "
                f"{path}"
            )
            return 1

    try:
        boundary_gradient_validator = load_validator(
            BOUNDARY_GRADIENT_SCHEMA_PATH
        )

        front_candidate_validator = load_validator(
            FRONT_CANDIDATE_SCHEMA_PATH
        )

    except Exception as exc:
        print(
            f"[ERROR] Failed to load v0.5 schema: "
            f"{exc}"
        )
        return 1

    failures = 0

    failures += validate_pass_examples(
        boundary_gradient_validator,
        front_candidate_validator,
    )

    failures += validate_fail_examples(
        boundary_gradient_validator,
        front_candidate_validator,
    )

    print("\n=== Result ===")

    if failures:
        print(
            f"FAILED: {failures} v0.5 schema validation "
            f"expectation(s) failed."
        )
        return 1

    print(
        "PASS: all AI Zero Network v0.5 "
        "Boundary Gradient and Front Candidate "
        "examples behaved as expected."
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
