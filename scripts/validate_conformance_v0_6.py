#!/usr/bin/env python3

import json
import math
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]

PASS_DIR = ROOT / "examples" / "v0.6" / "conformance" / "pass"
FAIL_DIR = ROOT / "examples" / "v0.6" / "conformance" / "fail"


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


def build_circulation_index(
    circulations: List[Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    return {
        circulation["circulation_id"]: circulation
        for circulation in circulations
        if "circulation_id" in circulation
    }


def validate_circulation(
    circulation: Dict[str, Any],
    errors: List[str],
) -> None:
    circulation_id = circulation.get(
        "circulation_id",
        "<unknown>",
    )

    # ---------------------------------------------------------
    # ZN-CIRC-001 — Bounded observation window
    # ---------------------------------------------------------

    try:
        window_start = parse_time(
            circulation["window_start"]
        )
        window_end = parse_time(
            circulation["window_end"]
        )

        if window_end <= window_start:
            add_error(
                errors,
                "ZN-CIRC-001",
                (
                    f"Circulation {circulation_id} has an invalid "
                    f"observation window."
                ),
            )

    except (KeyError, TypeError, ValueError) as exc:
        add_error(
            errors,
            "ZN-CIRC-001",
            (
                f"Circulation {circulation_id} has invalid "
                f"timestamps: {exc}"
            ),
        )
        window_start = None
        window_end = None

    # ---------------------------------------------------------
    # ZN-CIRC-002 — At least two distinct Regions
    # ---------------------------------------------------------

    region_refs = circulation.get("region_refs", [])

    if len(set(region_refs)) < 2:
        add_error(
            errors,
            "ZN-CIRC-002",
            (
                f"Circulation {circulation_id} must involve at "
                f"least two distinct Regions."
            ),
        )

    region_set = set(region_refs)

    # ---------------------------------------------------------
    # Cycle evidence
    # ---------------------------------------------------------

    cycles = circulation.get("cycles")

    if cycles is not None:
        reconstructed_cycle_count = 0

        cycle_ids = set()

        for cycle in cycles:
            cycle_id = cycle.get(
                "cycle_id",
                "<unknown>",
            )

            if cycle_id in cycle_ids:
                add_error(
                    errors,
                    "ZN-CIRC-CYCLE-001",
                    (
                        f"Circulation {circulation_id} contains "
                        f"duplicate cycle_id {cycle_id}."
                    ),
                )

            cycle_ids.add(cycle_id)

            path = cycle.get("path", [])

            # -------------------------------------------------
            # ZN-CIRC-003 — Path must return to origin
            # -------------------------------------------------

            if len(path) < 3:
                add_error(
                    errors,
                    "ZN-CIRC-003",
                    (
                        f"Cycle {cycle_id} in circulation "
                        f"{circulation_id} has an insufficient "
                        f"path."
                    ),
                )

            elif path[0] != path[-1]:
                add_error(
                    errors,
                    "ZN-CIRC-003",
                    (
                        f"Cycle {cycle_id} does not return to "
                        f"its origin: {path[0]} != {path[-1]}."
                    ),
                )

            # Must contain at least two distinct Regions
            # excluding the repeated closing node.
            interior_regions = (
                set(path[:-1])
                if len(path) >= 2
                else set(path)
            )

            if len(interior_regions) < 2:
                add_error(
                    errors,
                    "ZN-CIRC-002",
                    (
                        f"Cycle {cycle_id} does not involve "
                        f"at least two distinct Regions."
                    ),
                )

            # -------------------------------------------------
            # Cycle path must stay within region_refs
            # -------------------------------------------------

            unknown_regions = set(path) - region_set

            if unknown_regions:
                add_error(
                    errors,
                    "ZN-CIRC-REGION-001",
                    (
                        f"Cycle {cycle_id} contains Region(s) "
                        f"not declared in region_refs: "
                        f"{sorted(unknown_regions)}."
                    ),
                )

            occurrence_count = cycle.get(
                "occurrence_count",
                1,
            )

            reconstructed_cycle_count += (
                occurrence_count
            )

        # -----------------------------------------------------
        # FAIL-CIRC-004 — cycle_count reconstruction
        # -----------------------------------------------------

        reported_cycle_count = circulation.get(
            "cycle_count"
        )

        if (
            reported_cycle_count is not None
            and reported_cycle_count
            != reconstructed_cycle_count
        ):
            add_error(
                errors,
                "ZN-CIRC-COUNT-001",
                (
                    f"Circulation {circulation_id} reports "
                    f"cycle_count={reported_cycle_count}, but "
                    f"cycle evidence reconstructs "
                    f"{reconstructed_cycle_count}."
                ),
            )

    # ---------------------------------------------------------
    # Derived return_rate
    # ---------------------------------------------------------

    derived = circulation.get("derived", {})
    return_rate = derived.get("return_rate")

    if (
        return_rate is not None
        and return_rate.get("method")
        == "return_count/per_minute"
        and window_start is not None
        and window_end is not None
    ):
        minutes = (
            window_end - window_start
        ).total_seconds() / 60.0

        if minutes <= 0:
            add_error(
                errors,
                "ZN-CIRC-DERIVED-001",
                (
                    f"Circulation {circulation_id} cannot "
                    f"calculate return_rate from a "
                    f"non-positive duration."
                ),
            )
        else:
            expected = (
                circulation.get("return_count", 0)
                / minutes
            )

            reported = return_rate.get("value")

            if reported is None or not math.isclose(
                float(reported),
                float(expected),
                rel_tol=1e-9,
                abs_tol=1e-9,
            ):
                add_error(
                    errors,
                    "ZN-CIRC-DERIVED-001",
                    (
                        f"Circulation {circulation_id} reports "
                        f"return_rate={reported}, but expected "
                        f"{expected}."
                    ),
                )

    # ---------------------------------------------------------
    # Provenance time ordering
    # ---------------------------------------------------------

    provenance = circulation.get(
        "provenance",
        {},
    )

    generated_at = provenance.get(
        "generated_at"
    )

    if (
        generated_at is not None
        and window_end is not None
    ):
        try:
            generated_time = parse_time(
                generated_at
            )

            if generated_time < window_end:
                add_error(
                    errors,
                    "ZN-CIRC-PROV-001",
                    (
                        f"Circulation {circulation_id} was "
                        f"generated before its observation "
                        f"window ended."
                    ),
                )

        except (TypeError, ValueError) as exc:
            add_error(
                errors,
                "ZN-CIRC-PROV-001",
                (
                    f"Circulation {circulation_id} has "
                    f"invalid provenance.generated_at: "
                    f"{exc}"
                ),
            )


def validate_vortex_candidate(
    candidate: Dict[str, Any],
    circulation_index: Dict[str, Dict[str, Any]],
    errors: List[str],
) -> None:
    candidate_id = candidate.get(
        "candidate_id",
        "<unknown>",
    )

    refs = candidate.get(
        "circulation_refs",
        [],
    )

    referenced: List[Dict[str, Any]] = []

    # ---------------------------------------------------------
    # ZN-VORTEX-001 — Evidence must exist
    # ---------------------------------------------------------

    for circulation_id in refs:
        circulation = circulation_index.get(
            circulation_id
        )

        if circulation is None:
            add_error(
                errors,
                "ZN-VORTEX-001",
                (
                    f"Vortex Candidate {candidate_id} "
                    f"references missing circulation "
                    f"{circulation_id}."
                ),
            )
            continue

        referenced.append(circulation)

    if not referenced:
        return

    # ---------------------------------------------------------
    # Candidate window validity
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
                "ZN-VORTEX-TIME-001",
                (
                    f"Vortex Candidate {candidate_id} "
                    f"has an invalid analysis window."
                ),
            )

    except (KeyError, TypeError, ValueError) as exc:
        add_error(
            errors,
            "ZN-VORTEX-TIME-001",
            (
                f"Vortex Candidate {candidate_id} "
                f"has invalid timestamps: {exc}"
            ),
        )

        candidate_start = None
        candidate_end = None

    # ---------------------------------------------------------
    # Evidence window consistency
    # ---------------------------------------------------------

    if (
        candidate_start is not None
        and candidate_end is not None
    ):
        for circulation in referenced:
            circulation_id = circulation.get(
                "circulation_id"
            )

            try:
                circulation_start = parse_time(
                    circulation["window_start"]
                )

                circulation_end = parse_time(
                    circulation["window_end"]
                )

                if (
                    circulation_start != candidate_start
                    or circulation_end != candidate_end
                ):
                    add_error(
                        errors,
                        "ZN-VORTEX-TIME-002",
                        (
                            f"Vortex Candidate {candidate_id} "
                            f"window does not match circulation "
                            f"{circulation_id}."
                        ),
                    )

            except (
                KeyError,
                TypeError,
                ValueError,
            ):
                pass

    # ---------------------------------------------------------
    # Core Region consistency
    # ---------------------------------------------------------

    core_regions = candidate.get(
        "core_regions"
    )

    if core_regions is not None:
        available_regions = set()

        for circulation in referenced:
            available_regions.update(
                circulation.get(
                    "region_refs",
                    [],
                )
            )

        unknown_core_regions = (
            set(core_regions)
            - available_regions
        )

        if unknown_core_regions:
            add_error(
                errors,
                "ZN-VORTEX-REGION-001",
                (
                    f"Vortex Candidate {candidate_id} "
                    f"declares core Region(s) not present "
                    f"in referenced circulation evidence: "
                    f"{sorted(unknown_core_regions)}."
                ),
            )

    # ---------------------------------------------------------
    # Classification method
    # ---------------------------------------------------------

    method = candidate.get("method")

    if method == "cycle_density_threshold_v1":
        validate_cycle_density_threshold(
            candidate,
            referenced,
            errors,
        )

    elif method == "persistent_circulation_score_v1":
        validate_persistent_score(
            candidate,
            errors,
        )

    elif method == "multi_signal_vortex_candidate_v1":
        validate_multi_signal_score(
            candidate,
            errors,
        )

    else:
        add_error(
            errors,
            "ZN-VORTEX-003",
            (
                f"Vortex Candidate {candidate_id} uses "
                f"unsupported classifier method "
                f"{method!r}."
            ),
        )

    # ---------------------------------------------------------
    # Provenance refs
    # ---------------------------------------------------------

    provenance = candidate.get(
        "provenance",
        {},
    )

    source_refs = provenance.get(
        "source_circulation_refs"
    )

    if source_refs is not None:
        if set(source_refs) != set(refs):
            add_error(
                errors,
                "ZN-VORTEX-PROV-001",
                (
                    f"Vortex Candidate {candidate_id} "
                    f"provenance source_circulation_refs "
                    f"does not exactly match "
                    f"circulation_refs."
                ),
            )

    # ---------------------------------------------------------
    # Provenance time
    # ---------------------------------------------------------

    generated_at = provenance.get(
        "generated_at"
    )

    if (
        generated_at is not None
        and candidate_end is not None
    ):
        try:
            generated_time = parse_time(
                generated_at
            )

            if generated_time < candidate_end:
                add_error(
                    errors,
                    "ZN-VORTEX-PROV-002",
                    (
                        f"Vortex Candidate {candidate_id} "
                        f"was generated before its analysis "
                        f"window ended."
                    ),
                )

        except (TypeError, ValueError) as exc:
            add_error(
                errors,
                "ZN-VORTEX-PROV-002",
                (
                    f"Vortex Candidate {candidate_id} "
                    f"has invalid provenance.generated_at: "
                    f"{exc}"
                ),
            )


def validate_cycle_density_threshold(
    candidate: Dict[str, Any],
    circulations: List[Dict[str, Any]],
    errors: List[str],
) -> None:
    candidate_id = candidate.get(
        "candidate_id",
        "<unknown>",
    )

    thresholds = candidate.get(
        "thresholds",
        {},
    )

    if "cycle_density" not in thresholds:
        add_error(
            errors,
            "ZN-VORTEX-004",
            (
                f"Vortex Candidate {candidate_id} using "
                f"cycle_density_threshold_v1 must "
                f"declare cycle_density threshold."
            ),
        )
        return

    threshold = float(
        thresholds["cycle_density"]
    )

    densities = []

    for circulation in circulations:
        derived = circulation.get(
            "derived",
            {},
        )

        metric = derived.get(
            "cycle_density"
        )

        if metric is not None:
            densities.append(
                float(metric["value"])
            )

    if not densities:
        add_error(
            errors,
            "ZN-VORTEX-THRESHOLD-001",
            (
                f"Vortex Candidate {candidate_id} "
                f"requires cycle_density evidence, "
                f"but none is available."
            ),
        )
        return

    # For v0.6, every referenced circulation used by a
    # threshold classifier should satisfy the threshold.
    for value in densities:
        if value < threshold:
            add_error(
                errors,
                "ZN-VORTEX-THRESHOLD-002",
                (
                    f"Vortex Candidate {candidate_id} "
                    f"does not meet cycle_density threshold: "
                    f"value={value}, threshold={threshold}."
                ),
            )


def validate_persistent_score(
    candidate: Dict[str, Any],
    errors: List[str],
) -> None:
    """
    v0.6 does not yet define one canonical formula for
    persistent_circulation_score_v1.

    Therefore this validator checks that the score exists and is
    non-negative, while leaving exact reconstruction for a later
    specification.
    """
    candidate_id = candidate.get(
        "candidate_id",
        "<unknown>",
    )

    score = candidate.get("score")

    if score is None:
        add_error(
            errors,
            "ZN-VORTEX-SCORE-001",
            (
                f"Vortex Candidate {candidate_id} using "
                f"persistent_circulation_score_v1 must "
                f"declare score."
            ),
        )
        return

    if float(score) < 0:
        add_error(
            errors,
            "ZN-VORTEX-SCORE-001",
            (
                f"Vortex Candidate {candidate_id} "
                f"has negative score={score}."
            ),
        )


def validate_multi_signal_score(
    candidate: Dict[str, Any],
    errors: List[str],
) -> None:
    candidate_id = candidate.get(
        "candidate_id",
        "<unknown>",
    )

    weights = candidate.get(
        "weights",
        {},
    )

    signals = candidate.get(
        "signals",
        {},
    )

    # ---------------------------------------------------------
    # Weights must sum to 1.0
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
            "ZN-VORTEX-WEIGHT-001",
            (
                f"Vortex Candidate {candidate_id} "
                f"weights sum to {total_weight}, "
                f"expected 1.0."
            ),
        )

    # ---------------------------------------------------------
    # Every weighted signal must exist
    # ---------------------------------------------------------

    calculated_score = 0.0

    for signal_name, weight in weights.items():
        if signal_name not in signals:
            add_error(
                errors,
                "ZN-VORTEX-WEIGHT-002",
                (
                    f"Vortex Candidate {candidate_id} "
                    f"assigns weight to {signal_name}, "
                    f"but signals does not provide it."
                ),
            )
            continue

        calculated_score += (
            float(signals[signal_name])
            * float(weight)
        )

    # Signals that are not weighted are allowed.
    #
    # Example:
    # persistence_count may be present as supporting metadata
    # while the classifier weights only four normalized signals.

    reported_score = candidate.get(
        "score"
    )

    if reported_score is None:
        add_error(
            errors,
            "ZN-VORTEX-SCORE-002",
            (
                f"Vortex Candidate {candidate_id} "
                f"does not declare score."
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
            "ZN-VORTEX-SCORE-002",
            (
                f"Vortex Candidate {candidate_id} "
                f"reports score={reported_score}, "
                f"but expected {calculated_score}."
            ),
        )


def validate_fixture(
    data: Dict[str, Any],
) -> List[str]:
    errors: List[str] = []

    circulations = data.get(
        "circulations",
        [],
    )

    candidates = data.get(
        "vortex_candidates",
        [],
    )

    circulation_index = (
        build_circulation_index(circulations)
    )

    # ---------------------------------------------------------
    # Duplicate circulation IDs
    # ---------------------------------------------------------

    if len(circulation_index) != len(circulations):
        add_error(
            errors,
            "ZN-CIRC-ID-001",
            "Duplicate or missing circulation_id detected.",
        )

    for circulation in circulations:
        validate_circulation(
            circulation,
            errors,
        )

    # ---------------------------------------------------------
    # Duplicate candidate IDs
    # ---------------------------------------------------------

    candidate_ids = set()

    for candidate in candidates:
        candidate_id = candidate.get(
            "candidate_id"
        )

        if candidate_id in candidate_ids:
            add_error(
                errors,
                "ZN-VORTEX-ID-001",
                (
                    f"Duplicate candidate_id detected: "
                    f"{candidate_id}."
                ),
            )

        candidate_ids.add(candidate_id)

        validate_vortex_candidate(
            candidate,
            circulation_index,
            errors,
        )

    return errors


def validate_directory(
    directory: Path,
    expected_valid: bool,
) -> int:
    failures = 0

    label = (
        "PASS"
        if expected_valid
        else "FAIL"
    )

    print(
        f"\n=== v0.6 Conformance "
        f"{label} examples ==="
    )

    files = sorted(
        directory.glob("*.json")
    )

    if not files:
        print(
            f"[ERROR] No fixtures found in "
            f"{directory}"
        )
        return 1

    for path in files:
        try:
            data = load_json(path)

            errors = validate_fixture(
                data
            )

            is_valid = not errors

            if expected_valid and is_valid:
                print(
                    f"[PASS] "
                    f"{path.relative_to(ROOT)}"
                )

            elif expected_valid and not is_valid:
                failures += 1

                print(
                    f"[FAIL] "
                    f"{path.relative_to(ROOT)} "
                    f"was expected to conform"
                )

                for error in errors:
                    print(
                        f"       - {error}"
                    )

            elif (
                not expected_valid
                and not is_valid
            ):
                print(
                    f"[PASS] "
                    f"{path.relative_to(ROOT)} "
                    f"correctly rejected"
                )

                for error in errors:
                    print(
                        f"       - {error}"
                    )

            else:
                failures += 1

                print(
                    f"[FAIL] "
                    f"{path.relative_to(ROOT)} "
                    f"was expected to violate "
                    f"conformance but passed"
                )

        except (
            json.JSONDecodeError,
            OSError,
            TypeError,
            ValueError,
        ) as exc:
            failures += 1

            print(
                f"[FAIL] "
                f"{path.relative_to(ROOT)}"
            )

            print(
                f"       - Fixture could not "
                f"be evaluated: {exc}"
            )

    return failures


def main() -> int:
    print(
        "AI Zero Network v0.6 "
        "conformance validator"
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
                f"[ERROR] Required path does "
                f"not exist: {path}"
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
            f"FAILED: {failures} v0.6 "
            f"conformance expectation(s) failed."
        )
        return 1

    print(
        "PASS: all AI Zero Network v0.6 "
        "Circulation and Vortex Candidate "
        "conformance fixtures behaved as expected."
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
