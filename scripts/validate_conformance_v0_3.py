#!/usr/bin/env python3

import json
import math
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]

PASS_DIR = ROOT / "examples" / "v0.3" / "conformance" / "pass"
FAIL_DIR = ROOT / "examples" / "v0.3" / "conformance" / "fail"


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def parse_time(value: str) -> datetime:
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"

    return datetime.fromisoformat(value)


def add_error(
    errors: List[str],
    rule: str,
    message: str,
) -> None:
    errors.append(f"{rule}: {message}")


def validate_fixture(data: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    snapshot_id = data.get("snapshot_id")
    window_start = data.get("window_start")
    window_end = data.get("window_end")

    observations = data.get("observations", {})
    derived = data.get("derived", {})
    provenance = data.get("provenance", {})

    # ---------------------------------------------------------
    # ZN-FIELD-001 — Valid observation window
    # ---------------------------------------------------------

    try:
        start_time = parse_time(window_start)
        end_time = parse_time(window_end)

        if end_time <= start_time:
            add_error(
                errors,
                "ZN-FIELD-001",
                (
                    f"Snapshot {snapshot_id} has invalid observation "
                    f"window: window_end must be later than window_start."
                ),
            )

    except Exception as exc:
        add_error(
            errors,
            "ZN-FIELD-001",
            (
                f"Snapshot {snapshot_id} has invalid observation "
                f"timestamp: {exc}"
            ),
        )

        start_time = None
        end_time = None

    # ---------------------------------------------------------
    # Authority count consistency
    # ---------------------------------------------------------

    request_count = observations.get(
        "authority_request_count",
        0,
    )

    grant_count = observations.get(
        "authority_grant_count",
        0,
    )

    deny_count = observations.get(
        "authority_deny_count",
        0,
    )

    if grant_count + deny_count > request_count:
        add_error(
            errors,
            "ZN-FIELD-005",
            (
                f"Snapshot {snapshot_id} has "
                f"{grant_count + deny_count} authority decisions "
                f"but only {request_count} authority requests."
            ),
        )

    # ---------------------------------------------------------
    # Derived metric: authority_friction
    # ---------------------------------------------------------

    friction = derived.get("authority_friction")

    if request_count == 0:
        if friction is not None:
            add_error(
                errors,
                "ZN-FIELD-DERIVED-001",
                (
                    f"Snapshot {snapshot_id} reports "
                    f"authority_friction even though "
                    f"authority_request_count is zero."
                ),
            )

    elif friction is not None:
        method = friction.get("method")
        value = friction.get("value")

        if method == "deny_count/request_count":
            expected = deny_count / request_count

            if not math.isclose(
                value,
                expected,
                rel_tol=1e-9,
                abs_tol=1e-9,
            ):
                add_error(
                    errors,
                    "ZN-FIELD-DERIVED-002",
                    (
                        f"Snapshot {snapshot_id} reports "
                        f"authority_friction={value}, "
                        f"but expected approximately {expected}."
                    ),
                )

    # ---------------------------------------------------------
    # Provenance generated_at ordering
    # ---------------------------------------------------------

    generated_at = provenance.get("generated_at")

    if generated_at is not None and end_time is not None:
        try:
            generated_time = parse_time(generated_at)

            if generated_time < end_time:
                add_error(
                    errors,
                    "ZN-FIELD-PROV-001",
                    (
                        f"Snapshot {snapshot_id} was generated "
                        f"before its observation window ended."
                    ),
                )

        except Exception as exc:
            add_error(
                errors,
                "ZN-FIELD-PROV-001",
                (
                    f"Snapshot {snapshot_id} has invalid "
                    f"provenance.generated_at: {exc}"
                ),
            )

    # ---------------------------------------------------------
    # Provenance source_record_count consistency
    # ---------------------------------------------------------
    #
    # v0.3 intentionally avoids requiring exact equality because
    # some observation metrics may be derived from overlapping
    # source records.
    #
    # A conservative lower bound is:
    #
    #   trace_count + receipt_count
    #
    # These represent distinct record classes and therefore give
    # a useful minimum sanity check for the fixtures.
    # ---------------------------------------------------------

    source_record_count = provenance.get("source_record_count")

    if source_record_count is not None:
        trace_count = observations.get("trace_count", 0)
        receipt_count = observations.get("receipt_count", 0)

        minimum_independent_records = trace_count + receipt_count

        if source_record_count < minimum_independent_records:
            add_error(
                errors,
                "ZN-FIELD-PROV-002",
                (
                    f"Snapshot {snapshot_id} reports "
                    f"source_record_count={source_record_count}, "
                    f"but trace_count + receipt_count requires "
                    f"at least {minimum_independent_records} "
                    f"source records."
                ),
            )

    return errors


def validate_directory(
    directory: Path,
    expected_valid: bool,
) -> int:
    failures = 0

    label = "PASS" if expected_valid else "FAIL"

    print(f"\n=== v0.3 Conformance {label} examples ===")

    files = sorted(directory.glob("*.json"))

    if not files:
        print(f"[ERROR] No fixtures found in {directory}")
        return 1

    for path in files:
        try:
            data = load_json(path)
            errors = validate_fixture(data)

            is_valid = not errors

            if expected_valid and is_valid:
                print(f"[PASS] {path.relative_to(ROOT)}")

            elif expected_valid and not is_valid:
                failures += 1

                print(
                    f"[FAIL] {path.relative_to(ROOT)} "
                    f"was expected to conform"
                )

                for error in errors:
                    print(f"       - {error}")

            elif not expected_valid and not is_valid:
                print(
                    f"[PASS] {path.relative_to(ROOT)} "
                    f"correctly rejected"
                )

                for error in errors:
                    print(f"       - {error}")

            else:
                failures += 1

                print(
                    f"[FAIL] {path.relative_to(ROOT)} "
                    f"was expected to violate conformance "
                    f"but passed"
                )

        except (
            json.JSONDecodeError,
            OSError,
            TypeError,
            ValueError,
        ) as exc:
            failures += 1

            print(f"[FAIL] {path.relative_to(ROOT)}")
            print(
                f"       - Fixture could not be evaluated: {exc}"
            )

    return failures


def main() -> int:
    print("AI Zero Network v0.3 conformance validator")
    print("==========================================")

    required_paths = [
        PASS_DIR,
        FAIL_DIR,
    ]

    for path in required_paths:
        if not path.exists():
            print(
                f"[ERROR] Required path does not exist: {path}"
            )
            return 1

    failures = 0

    failures += validate_directory(
        PASS_DIR,
        expected_valid=True,
    )

    failures += validate_directory(
        FAIL_DIR,
        expected_valid=False,
    )

    print("\n=== Result ===")

    if failures:
        print(
            f"FAILED: {failures} v0.3 conformance "
            f"expectation(s) failed."
        )
        return 1

    print(
        "PASS: all AI Zero Network v0.3 "
        "conformance fixtures behaved as expected."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
