#!/usr/bin/env python3

import json
import math
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]

PASS_DIR = ROOT / "examples" / "v0.4" / "conformance" / "pass"
FAIL_DIR = ROOT / "examples" / "v0.4" / "conformance" / "fail"


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


def snapshot_index(
    snapshots: List[Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    return {
        snapshot["snapshot_id"]: snapshot
        for snapshot in snapshots
        if "snapshot_id" in snapshot
    }


def duration_minutes(
    window_start: str,
    window_end: str,
) -> float:
    start = parse_time(window_start)
    end = parse_time(window_end)
    return (end - start).total_seconds() / 60.0


def expected_trend(
    from_value: float,
    to_value: float,
    tolerance: float = 1e-12,
) -> str:
    if math.isclose(
        from_value,
        to_value,
        rel_tol=tolerance,
        abs_tol=tolerance,
    ):
        return "stable"

    if to_value > from_value:
        return "rising"

    return "falling"


def validate_field_delta(
    delta: Dict[str, Any],
    snapshots: Dict[str, Dict[str, Any]],
    errors: List[str],
) -> None:
    delta_id = delta.get("delta_id", "<unknown>")

    from_id = delta.get("from_snapshot")
    to_id = delta.get("to_snapshot")

    # ---------------------------------------------------------
    # ZN-DYN-001 — Both source snapshots must exist
    # ---------------------------------------------------------

    from_snapshot = snapshots.get(from_id)
    to_snapshot = snapshots.get(to_id)

    if from_snapshot is None:
        add_error(
            errors,
            "ZN-DYN-001",
            (
                f"Field Delta {delta_id} references missing "
                f"from_snapshot {from_id}."
            ),
        )

    if to_snapshot is None:
        add_error(
            errors,
            "ZN-DYN-001",
            (
                f"Field Delta {delta_id} references missing "
                f"to_snapshot {to_id}."
            ),
        )

    # Other source-dependent checks cannot safely continue.
    if from_snapshot is None or to_snapshot is None:
        validate_derived_trends(delta, errors)
        return

    # ---------------------------------------------------------
    # ZN-DYN-002 — Forward temporal ordering
    # ---------------------------------------------------------

    try:
        from_end = parse_time(from_snapshot["window_end"])
        to_end = parse_time(to_snapshot["window_end"])

        if to_end <= from_end:
            add_error(
                errors,
                "ZN-DYN-002",
                (
                    f"Field Delta {delta_id} is not forward in time: "
                    f"to_snapshot.window_end must be later than "
                    f"from_snapshot.window_end."
                ),
            )

    except (KeyError, TypeError, ValueError) as exc:
        add_error(
            errors,
            "ZN-DYN-002",
            (
                f"Field Delta {delta_id} has invalid snapshot "
                f"timestamps: {exc}"
            ),
        )

    # ---------------------------------------------------------
    # ZN-DYN-003 — Same-region comparison
    # ---------------------------------------------------------

    delta_region = delta.get("region")
    from_region = from_snapshot.get("region")
    to_region = to_snapshot.get("region")

    if from_region != to_region:
        add_error(
            errors,
            "ZN-DYN-003",
            (
                f"Field Delta {delta_id} compares different Regions: "
                f"{from_region} -> {to_region}."
            ),
        )

    if delta_region != from_region or delta_region != to_region:
        add_error(
            errors,
            "ZN-DYN-003",
            (
                f"Field Delta {delta_id} declares region "
                f"{delta_region}, but source snapshots use "
                f"{from_region} and {to_region}."
            ),
        )

    # ---------------------------------------------------------
    # ZN-DYN-004 — Reported deltas must match source snapshots
    # ---------------------------------------------------------

    changes = delta.get("changes", {})
    from_obs = from_snapshot.get("observations", {})
    to_obs = to_snapshot.get("observations", {})

    for metric, reported_delta in changes.items():
        if metric == "resources":
            validate_resource_delta(
                delta_id,
                reported_delta,
                from_obs.get("resources", {}),
                to_obs.get("resources", {}),
                errors,
            )
            continue

        if metric not in from_obs or metric not in to_obs:
            add_error(
                errors,
                "ZN-DYN-004",
                (
                    f"Field Delta {delta_id} reports change for "
                    f"{metric}, but that metric is missing from one "
                    f"or both source snapshots."
                ),
            )
            continue

        expected = to_obs[metric] - from_obs[metric]

        if reported_delta != expected:
            add_error(
                errors,
                "ZN-DYN-004",
                (
                    f"Field Delta {delta_id} reports "
                    f"{metric}={reported_delta}, but expected "
                    f"{expected}."
                ),
            )

    # ---------------------------------------------------------
    # Snapshot window compatibility / normalization
    # ---------------------------------------------------------

    comparison = delta.get("comparison", {})

    try:
        from_duration = duration_minutes(
            from_snapshot["window_start"],
            from_snapshot["window_end"],
        )
        to_duration = duration_minutes(
            to_snapshot["window_start"],
            to_snapshot["window_end"],
        )

        unequal_duration = not math.isclose(
            from_duration,
            to_duration,
            rel_tol=1e-9,
            abs_tol=1e-9,
        )

        compatibility = comparison.get("window_compatibility")

        if unequal_duration:
            if compatibility != "normalized":
                add_error(
                    errors,
                    "ZN-DYN-NORM-001",
                    (
                        f"Field Delta {delta_id} compares unequal "
                        f"window durations ({from_duration:g} vs "
                        f"{to_duration:g} minutes) without declaring "
                        f"window_compatibility='normalized'."
                    ),
                )

            if not comparison.get("normalization_method"):
                add_error(
                    errors,
                    "ZN-DYN-NORM-002",
                    (
                        f"Field Delta {delta_id} compares unequal "
                        f"windows without a normalization_method."
                    ),
                )

    except (KeyError, TypeError, ValueError) as exc:
        add_error(
            errors,
            "ZN-DYN-NORM-001",
            (
                f"Field Delta {delta_id} has invalid observation "
                f"window metadata: {exc}"
            ),
        )

    # ---------------------------------------------------------
    # Derived trend consistency
    # ---------------------------------------------------------

    validate_derived_trends(delta, errors)

    # ---------------------------------------------------------
    # Provenance source refs
    # ---------------------------------------------------------

    provenance = delta.get("provenance", {})
    refs = provenance.get("source_snapshot_refs")

    if refs is not None:
        expected_refs = {from_id, to_id}

        if set(refs) != expected_refs:
            add_error(
                errors,
                "ZN-DYN-PROV-001",
                (
                    f"Field Delta {delta_id} provenance "
                    f"source_snapshot_refs does not exactly match "
                    f"from_snapshot and to_snapshot."
                ),
            )


def validate_resource_delta(
    delta_id: str,
    reported_resources: Dict[str, Any],
    from_resources: Dict[str, Any],
    to_resources: Dict[str, Any],
    errors: List[str],
) -> None:
    for metric, reported_delta in reported_resources.items():
        if metric not in from_resources or metric not in to_resources:
            add_error(
                errors,
                "ZN-DYN-004",
                (
                    f"Field Delta {delta_id} reports resource "
                    f"change for {metric}, but the metric is missing "
                    f"from one or both source snapshots."
                ),
            )
            continue

        expected = to_resources[metric] - from_resources[metric]

        if not math.isclose(
            float(reported_delta),
            float(expected),
            rel_tol=1e-9,
            abs_tol=1e-9,
        ):
            add_error(
                errors,
                "ZN-DYN-004",
                (
                    f"Field Delta {delta_id} reports resource "
                    f"{metric}={reported_delta}, but expected "
                    f"{expected}."
                ),
            )


def validate_derived_trends(
    delta: Dict[str, Any],
    errors: List[str],
) -> None:
    delta_id = delta.get("delta_id", "<unknown>")
    derived = delta.get("derived", {})

    for metric_name, metric in derived.items():
        if not isinstance(metric, dict):
            continue

        if not all(
            key in metric
            for key in ("from", "to", "trend")
        ):
            continue

        expected = expected_trend(
            float(metric["from"]),
            float(metric["to"]),
        )

        reported = metric["trend"]

        if reported != expected:
            add_error(
                errors,
                "ZN-DYN-DERIVED-001",
                (
                    f"Field Delta {delta_id} derived metric "
                    f"{metric_name} reports trend={reported}, "
                    f"but from={metric['from']} and to={metric['to']} "
                    f"imply trend={expected}."
                ),
            )


def validate_region_flow(
    flow: Dict[str, Any],
    errors: List[str],
) -> None:
    flow_id = flow.get("flow_id", "<unknown>")

    source_region = flow.get("source_region")
    target_region = flow.get("target_region")

    # ---------------------------------------------------------
    # ZN-FLOW-001/002 — Directional cross-region flow
    # ---------------------------------------------------------

    if source_region == target_region:
        add_error(
            errors,
            "ZN-FLOW-002",
            (
                f"Region Flow {flow_id} uses the same Region "
                f"as source and target: {source_region}."
            ),
        )

    # ---------------------------------------------------------
    # Valid observation window
    # ---------------------------------------------------------

    try:
        start = parse_time(flow["window_start"])
        end = parse_time(flow["window_end"])

        if end <= start:
            add_error(
                errors,
                "ZN-FLOW-003",
                (
                    f"Region Flow {flow_id} has invalid time window: "
                    f"window_end must be later than window_start."
                ),
            )

    except (KeyError, TypeError, ValueError) as exc:
        add_error(
            errors,
            "ZN-FLOW-003",
            (
                f"Region Flow {flow_id} has invalid timestamps: "
                f"{exc}"
            ),
        )
        start = None
        end = None

    # ---------------------------------------------------------
    # Derived flow_rate
    # ---------------------------------------------------------

    observations = flow.get("observations", {})
    derived = flow.get("derived", {})

    flow_rate = derived.get("flow_rate")

    if (
        flow_rate is not None
        and flow_rate.get("method") == "trace_count/per_minute"
        and start is not None
        and end is not None
    ):
        trace_count = observations.get("trace_count")

        if trace_count is None:
            add_error(
                errors,
                "ZN-FLOW-DERIVED-001",
                (
                    f"Region Flow {flow_id} declares a trace-based "
                    f"flow_rate without trace_count."
                ),
            )
        else:
            minutes = (end - start).total_seconds() / 60.0

            if minutes <= 0:
                add_error(
                    errors,
                    "ZN-FLOW-DERIVED-001",
                    (
                        f"Region Flow {flow_id} cannot calculate "
                        f"flow_rate from a non-positive duration."
                    ),
                )
            else:
                expected = trace_count / minutes
                reported = flow_rate.get("value")

                if reported is None or not math.isclose(
                    float(reported),
                    float(expected),
                    rel_tol=1e-9,
                    abs_tol=1e-9,
                ):
                    add_error(
                        errors,
                        "ZN-FLOW-DERIVED-001",
                        (
                            f"Region Flow {flow_id} reports "
                            f"flow_rate={reported}, but expected "
                            f"{expected}."
                        ),
                    )

    # Optional effective_flow consistency
    effective_flow = derived.get("effective_flow")

    if (
        effective_flow is not None
        and effective_flow.get("method")
        == "receipt_count/per_minute"
        and start is not None
        and end is not None
    ):
        receipt_count = observations.get("receipt_count")

        if receipt_count is None:
            add_error(
                errors,
                "ZN-FLOW-DERIVED-002",
                (
                    f"Region Flow {flow_id} declares "
                    f"receipt-based effective_flow without "
                    f"receipt_count."
                ),
            )
        else:
            minutes = (end - start).total_seconds() / 60.0
            expected = receipt_count / minutes
            reported = effective_flow.get("value")

            if reported is None or not math.isclose(
                float(reported),
                float(expected),
                rel_tol=1e-9,
                abs_tol=1e-9,
            ):
                add_error(
                    errors,
                    "ZN-FLOW-DERIVED-002",
                    (
                        f"Region Flow {flow_id} reports "
                        f"effective_flow={reported}, but expected "
                        f"{expected}."
                    ),
                )

    # ---------------------------------------------------------
    # Provenance ordering
    # ---------------------------------------------------------

    provenance = flow.get("provenance", {})
    generated_at = provenance.get("generated_at")

    if generated_at is not None and end is not None:
        try:
            generated = parse_time(generated_at)

            if generated < end:
                add_error(
                    errors,
                    "ZN-FLOW-PROV-001",
                    (
                        f"Region Flow {flow_id} was generated before "
                        f"its observation window ended."
                    ),
                )

        except (TypeError, ValueError) as exc:
            add_error(
                errors,
                "ZN-FLOW-PROV-001",
                (
                    f"Region Flow {flow_id} has invalid "
                    f"provenance.generated_at: {exc}"
                ),
            )

    # ---------------------------------------------------------
    # Conservative provenance lower bound
    # ---------------------------------------------------------

    source_record_count = provenance.get("source_record_count")

    if source_record_count is not None:
        trace_count = observations.get("trace_count", 0)
        receipt_count = observations.get("receipt_count", 0)

        minimum = max(trace_count, receipt_count)

        if source_record_count < minimum:
            add_error(
                errors,
                "ZN-FLOW-PROV-002",
                (
                    f"Region Flow {flow_id} reports "
                    f"source_record_count={source_record_count}, "
                    f"but observed counts imply at least "
                    f"{minimum} source records."
                ),
            )


def validate_fixture(
    data: Dict[str, Any],
) -> List[str]:
    errors: List[str] = []

    snapshots_raw = data.get("snapshots", [])
    deltas = data.get("field_deltas", [])
    flows = data.get("region_flows", [])

    snapshots = snapshot_index(snapshots_raw)

    # Duplicate snapshot IDs would make lookup ambiguous.
    if len(snapshots) != len(snapshots_raw):
        add_error(
            errors,
            "ZN-DYN-SNAPSHOT-001",
            "Duplicate or missing snapshot_id detected.",
        )

    for delta in deltas:
        validate_field_delta(
            delta,
            snapshots,
            errors,
        )

    for flow in flows:
        validate_region_flow(
            flow,
            errors,
        )

    return errors


def validate_directory(
    directory: Path,
    expected_valid: bool,
) -> int:
    failures = 0

    label = "PASS" if expected_valid else "FAIL"

    print(f"\n=== v0.4 Conformance {label} examples ===")

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
    print("AI Zero Network v0.4 conformance validator")
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
            f"FAILED: {failures} v0.4 conformance "
            f"expectation(s) failed."
        )
        return 1

    print(
        "PASS: all AI Zero Network v0.4 "
        "Field Dynamics conformance fixtures "
        "behaved as expected."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
