#!/usr/bin/env python3

import json
import math
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]

PASS_DIR = ROOT / "examples" / "v0.5" / "conformance" / "pass"
FAIL_DIR = ROOT / "examples" / "v0.5" / "conformance" / "fail"


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


def build_gradient_index(
    gradients: List[Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    return {
        gradient["gradient_id"]: gradient
        for gradient in gradients
        if "gradient_id" in gradient
    }


def validate_gradient(
    gradient: Dict[str, Any],
    errors: List[str],
) -> None:
    gradient_id = gradient.get(
        "gradient_id",
        "<unknown>",
    )

    region_a = gradient.get("region_a")
    region_b = gradient.get("region_b")

    # ---------------------------------------------------------
    # ZN-GRAD-001 — Two distinct Regions
    # ---------------------------------------------------------

    if region_a == region_b:
        add_error(
            errors,
            "ZN-GRAD-001",
            (
                f"Boundary Gradient {gradient_id} compares "
                f"the same Region on both sides: {region_a}."
            ),
        )

    # ---------------------------------------------------------
    # Observation window
    # ---------------------------------------------------------

    try:
        window_start = parse_time(
            gradient["window_start"]
        )
        window_end = parse_time(
            gradient["window_end"]
        )

        if window_end <= window_start:
            add_error(
                errors,
                "ZN-GRAD-003",
                (
                    f"Boundary Gradient {gradient_id} has "
                    f"an invalid comparison window."
                ),
            )

    except (KeyError, TypeError, ValueError) as exc:
        add_error(
            errors,
            "ZN-GRAD-003",
            (
                f"Boundary Gradient {gradient_id} has "
                f"invalid timestamps: {exc}"
            ),
        )
        window_end = None

    # ---------------------------------------------------------
    # ZN-GRAD-004 — Reconstruct gradient
    # ---------------------------------------------------------

    try:
        value_a = float(gradient["value_a"])
        value_b = float(gradient["value_b"])
        reported = float(gradient["gradient"])
        method = gradient["method"]

        if method == "absolute_difference":
            expected = abs(value_a - value_b)

        elif method == "directional_difference":
            expected = value_a - value_b

        else:
            add_error(
                errors,
                "ZN-GRAD-004",
                (
                    f"Boundary Gradient {gradient_id} uses "
                    f"unsupported method {method!r}."
                ),
            )
            expected = None

        if expected is not None and not math.isclose(
            reported,
            expected,
            rel_tol=1e-9,
            abs_tol=1e-9,
        ):
            add_error(
                errors,
                "ZN-GRAD-004",
                (
                    f"Boundary Gradient {gradient_id} reports "
                    f"gradient={reported}, but expected "
                    f"{expected}."
                ),
            )

    except (KeyError, TypeError, ValueError) as exc:
        add_error(
            errors,
            "ZN-GRAD-004",
            (
                f"Boundary Gradient {gradient_id} cannot "
                f"be reconstructed: {exc}"
            ),
        )

    # ---------------------------------------------------------
    # Provenance time ordering
    # ---------------------------------------------------------

    provenance = gradient.get("provenance", {})
    generated_at = provenance.get("generated_at")

    if generated_at is not None and window_end is not None:
        try:
            generated_time = parse_time(generated_at)

            if generated_time < window_end:
                add_error(
                    errors,
                    "ZN-GRAD-PROV-001",
                    (
                        f"Boundary Gradient {gradient_id} was "
                        f"generated before its comparison "
                        f"window ended."
                    ),
                )

        except (TypeError, ValueError) as exc:
            add_error(
                errors,
                "ZN-GRAD-PROV-001",
                (
                    f"Boundary Gradient {gradient_id} has "
                    f"invalid provenance.generated_at: {exc}"
                ),
            )


def validate_candidate(
    candidate: Dict[str, Any],
    gradient_index: Dict[str, Dict[str, Any]],
    errors: List[str],
) -> None:
    candidate_id = candidate.get(
        "candidate_id",
        "<unknown>",
    )

    refs = candidate.get("gradient_refs", [])

    referenced_gradients: List[Dict[str, Any]] = []

    # ---------------------------------------------------------
    # ZN-FRONT-001 — Gradient evidence must exist
    # ---------------------------------------------------------

    for gradient_id in refs:
        gradient = gradient_index.get(gradient_id)

        if gradient is None:
            add_error(
                errors,
                "ZN-FRONT-001",
                (
                    f"Front Candidate {candidate_id} references "
                    f"missing Boundary Gradient {gradient_id}."
                ),
            )
            continue

        referenced_gradients.append(gradient)

    if not referenced_gradients:
        return

    candidate_boundary = candidate.get("boundary_id")
    candidate_region_a = candidate.get("region_a")
    candidate_region_b = candidate.get("region_b")

    # ---------------------------------------------------------
    # Boundary and Region consistency
    # ---------------------------------------------------------

    for gradient in referenced_gradients:
        gradient_id = gradient.get("gradient_id")

        if gradient.get("boundary_id") != candidate_boundary:
            add_error(
                errors,
                "ZN-FRONT-BOUNDARY-001",
                (
                    f"Front Candidate {candidate_id} uses "
                    f"Boundary Gradient {gradient_id} from "
                    f"boundary {gradient.get('boundary_id')}, "
                    f"but candidate boundary is "
                    f"{candidate_boundary}."
                ),
            )

        if (
            gradient.get("region_a") != candidate_region_a
            or gradient.get("region_b") != candidate_region_b
        ):
            add_error(
                errors,
                "ZN-FRONT-BOUNDARY-002",
                (
                    f"Front Candidate {candidate_id} Region pair "
                    f"does not match Boundary Gradient "
                    f"{gradient_id}."
                ),
            )

    # ---------------------------------------------------------
    # Candidate analysis window consistency
    # ---------------------------------------------------------

    try:
        candidate_start = parse_time(
            candidate["window_start"]
        )
        candidate_end = parse_time(
            candidate["window_end"]
        )

        if candidate_end <= candidate_start:
            add_error(
                errors,
                "ZN-FRONT-TIME-001",
                (
                    f"Front Candidate {candidate_id} has "
                    f"an invalid analysis window."
                ),
            )

    except (KeyError, TypeError, ValueError) as exc:
        add_error(
            errors,
            "ZN-FRONT-TIME-001",
            (
                f"Front Candidate {candidate_id} has "
                f"invalid timestamps: {exc}"
            ),
        )
        candidate_start = None
        candidate_end = None

    if candidate_start is not None and candidate_end is not None:
        for gradient in referenced_gradients:
            try:
                gradient_start = parse_time(
                    gradient["window_start"]
                )
                gradient_end = parse_time(
                    gradient["window_end"]
                )

                if (
                    gradient_start != candidate_start
                    or gradient_end != candidate_end
                ):
                    add_error(
                        errors,
                        "ZN-FRONT-TIME-002",
                        (
                            f"Front Candidate {candidate_id} "
                            f"window does not match Boundary "
                            f"Gradient "
                            f"{gradient.get('gradient_id')}."
                        ),
                    )

            except (KeyError, TypeError, ValueError):
                pass

    # ---------------------------------------------------------
    # Classification method
    # ---------------------------------------------------------

    method = candidate.get("method")

    if method == "single_metric_threshold_v1":
        validate_single_threshold(
            candidate,
            referenced_gradients,
            errors,
        )

    elif method == "multi_metric_threshold_v1":
        validate_multi_threshold(
            candidate,
            referenced_gradients,
            errors,
        )

    elif method == "gradient_weighted_score_v1":
        validate_weighted_score(
            candidate,
            referenced_gradients,
            errors,
        )

    else:
        add_error(
            errors,
            "ZN-FRONT-003",
            (
                f"Front Candidate {candidate_id} uses "
                f"unsupported classifier method {method!r}."
            ),
        )

    # ---------------------------------------------------------
    # Provenance
    # ---------------------------------------------------------

    provenance = candidate.get("provenance", {})

    source_gradient_refs = provenance.get(
        "source_gradient_refs"
    )

    if source_gradient_refs is not None:
        if set(source_gradient_refs) != set(refs):
            add_error(
                errors,
                "ZN-FRONT-PROV-001",
                (
                    f"Front Candidate {candidate_id} provenance "
                    f"source_gradient_refs does not exactly "
                    f"match gradient_refs."
                ),
            )

    generated_at = provenance.get("generated_at")

    if generated_at is not None and candidate_end is not None:
        try:
            generated_time = parse_time(generated_at)

            if generated_time < candidate_end:
                add_error(
                    errors,
                    "ZN-FRONT-PROV-002",
                    (
                        f"Front Candidate {candidate_id} was "
                        f"generated before its analysis window "
                        f"ended."
                    ),
                )

        except (TypeError, ValueError) as exc:
            add_error(
                errors,
                "ZN-FRONT-PROV-002",
                (
                    f"Front Candidate {candidate_id} has "
                    f"invalid provenance.generated_at: {exc}"
                ),
            )


def metric_gradient_map(
    gradients: List[Dict[str, Any]],
) -> Dict[str, float]:
    result: Dict[str, float] = {}

    for gradient in gradients:
        metric = gradient.get("metric")

        if metric is None:
            continue

        result[metric] = float(
            gradient.get("gradient", 0)
        )

    return result


def validate_single_threshold(
    candidate: Dict[str, Any],
    gradients: List[Dict[str, Any]],
    errors: List[str],
) -> None:
    candidate_id = candidate.get(
        "candidate_id",
        "<unknown>",
    )

    thresholds = candidate.get("thresholds", {})

    if len(thresholds) != 1:
        add_error(
            errors,
            "ZN-FRONT-004",
            (
                f"Front Candidate {candidate_id} using "
                f"single_metric_threshold_v1 must declare "
                f"exactly one threshold."
            ),
        )
        return

    values = metric_gradient_map(gradients)

    metric, threshold = next(iter(thresholds.items()))

    if metric not in values:
        add_error(
            errors,
            "ZN-FRONT-THRESHOLD-001",
            (
                f"Front Candidate {candidate_id} declares "
                f"threshold for {metric}, but no referenced "
                f"gradient provides that metric."
            ),
        )
        return

    actual = abs(values[metric])

    if actual < float(threshold):
        add_error(
            errors,
            "ZN-FRONT-THRESHOLD-002",
            (
                f"Front Candidate {candidate_id} does not meet "
                f"threshold for {metric}: gradient={actual}, "
                f"threshold={threshold}."
            ),
        )


def validate_multi_threshold(
    candidate: Dict[str, Any],
    gradients: List[Dict[str, Any]],
    errors: List[str],
) -> None:
    candidate_id = candidate.get(
        "candidate_id",
        "<unknown>",
    )

    thresholds = candidate.get("thresholds", {})
    values = metric_gradient_map(gradients)

    if not thresholds:
        add_error(
            errors,
            "ZN-FRONT-004",
            (
                f"Front Candidate {candidate_id} has no "
                f"threshold configuration."
            ),
        )
        return

    for metric, threshold in thresholds.items():
        if metric not in values:
            add_error(
                errors,
                "ZN-FRONT-THRESHOLD-001",
                (
                    f"Front Candidate {candidate_id} declares "
                    f"threshold for {metric}, but no referenced "
                    f"gradient provides it."
                ),
            )
            continue

        actual = abs(values[metric])

        if actual < float(threshold):
            add_error(
                errors,
                "ZN-FRONT-THRESHOLD-002",
                (
                    f"Front Candidate {candidate_id} does not "
                    f"meet threshold for {metric}: "
                    f"gradient={actual}, "
                    f"threshold={threshold}."
                ),
            )


def validate_weighted_score(
    candidate: Dict[str, Any],
    gradients: List[Dict[str, Any]],
    errors: List[str],
) -> None:
    candidate_id = candidate.get(
        "candidate_id",
        "<unknown>",
    )

    weights = candidate.get("weights", {})
    values = metric_gradient_map(gradients)

    # ---------------------------------------------------------
    # Weight normalization
    # ---------------------------------------------------------

    total_weight = sum(
        float(weight)
        for weight in weights.values()
    )

    if not math.isclose(
        total_weight,
        1.0,
        rel_tol=1e-9,
        abs_tol=1e-9,
    ):
        add_error(
            errors,
            "ZN-FRONT-WEIGHT-001",
            (
                f"Front Candidate {candidate_id} weights sum "
                f"to {total_weight}, expected 1.0."
            ),
        )

    # ---------------------------------------------------------
    # Every weighted metric must exist
    # ---------------------------------------------------------

    calculated_score = 0.0

    for metric, weight in weights.items():
        if metric not in values:
            add_error(
                errors,
                "ZN-FRONT-WEIGHT-002",
                (
                    f"Front Candidate {candidate_id} assigns "
                    f"weight to {metric}, but no referenced "
                    f"gradient provides that metric."
                ),
            )
            continue

        calculated_score += (
            abs(values[metric]) * float(weight)
        )

    # ---------------------------------------------------------
    # Referenced gradient metrics should all participate
    # ---------------------------------------------------------

    referenced_metrics = set(values)
    weighted_metrics = set(weights)

    unused_metrics = (
        referenced_metrics - weighted_metrics
    )

    if unused_metrics:
        add_error(
            errors,
            "ZN-FRONT-WEIGHT-003",
            (
                f"Front Candidate {candidate_id} references "
                f"gradient metric(s) without weights: "
                f"{sorted(unused_metrics)}."
            ),
        )

    # ---------------------------------------------------------
    # Reconstruct weighted score
    # ---------------------------------------------------------

    reported_score = candidate.get("score")

    if reported_score is None:
        add_error(
            errors,
            "ZN-FRONT-SCORE-001",
            (
                f"Front Candidate {candidate_id} does not "
                f"declare a score."
            ),
        )
        return

    if not math.isclose(
        float(reported_score),
        calculated_score,
        rel_tol=1e-9,
        abs_tol=1e-9,
    ):
        add_error(
            errors,
            "ZN-FRONT-SCORE-001",
            (
                f"Front Candidate {candidate_id} reports "
                f"score={reported_score}, but expected "
                f"{calculated_score}."
            ),
        )


def validate_fixture(
    data: Dict[str, Any],
) -> List[str]:
    errors: List[str] = []

    gradients = data.get("gradients", [])
    candidates = data.get("front_candidates", [])

    gradient_index = build_gradient_index(
        gradients
    )

    # Duplicate or missing gradient IDs make references ambiguous.
    if len(gradient_index) != len(gradients):
        add_error(
            errors,
            "ZN-GRAD-ID-001",
            "Duplicate or missing gradient_id detected.",
        )

    for gradient in gradients:
        validate_gradient(
            gradient,
            errors,
        )

    candidate_ids = set()

    for candidate in candidates:
        candidate_id = candidate.get("candidate_id")

        if candidate_id in candidate_ids:
            add_error(
                errors,
                "ZN-FRONT-ID-001",
                (
                    f"Duplicate candidate_id detected: "
                    f"{candidate_id}."
                ),
            )

        candidate_ids.add(candidate_id)

        validate_candidate(
            candidate,
            gradient_index,
            errors,
        )

    return errors


def validate_directory(
    directory: Path,
    expected_valid: bool,
) -> int:
    failures = 0

    label = "PASS" if expected_valid else "FAIL"

    print(
        f"\n=== v0.5 Conformance {label} examples ==="
    )

    files = sorted(directory.glob("*.json"))

    if not files:
        print(
            f"[ERROR] No fixtures found in {directory}"
        )
        return 1

    for path in files:
        try:
            data = load_json(path)
            errors = validate_fixture(data)

            is_valid = not errors

            if expected_valid and is_valid:
                print(
                    f"[PASS] {path.relative_to(ROOT)}"
                )

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

            print(
                f"[FAIL] {path.relative_to(ROOT)}"
            )
            print(
                f"       - Fixture could not be evaluated: "
                f"{exc}"
            )

    return failures


def main() -> int:
    print(
        "AI Zero Network v0.5 conformance validator"
    )
    print(
        "=========================================="
    )

    required_paths = [
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
            f"FAILED: {failures} v0.5 conformance "
            f"expectation(s) failed."
        )
        return 1

    print(
        "PASS: all AI Zero Network v0.5 "
        "Boundary Gradient and Front Candidate "
        "conformance fixtures behaved as expected."
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
