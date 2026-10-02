#!/usr/bin/env python3

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple


ROOT = Path(__file__).resolve().parents[1]

PASS_DIR = ROOT / "examples" / "v0.1" / "conformance" / "pass"
FAIL_DIR = ROOT / "examples" / "v0.1" / "conformance" / "fail"


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def parse_time(value: str) -> datetime:
    """
    Parse ISO-8601 timestamps.

    Python's datetime.fromisoformat() accepts offsets such as +09:00.
    It also accepts trailing Z after normalization.
    """
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
    """
    Validate one AI Zero Network v0.1 conformance fixture.

    Returns a list of semantic conformance errors.
    An empty list means the fixture is conforming.
    """
    errors: List[str] = []

    participant = data.get("participant", {})
    traces = data.get("traces", [])
    authority_events = data.get("authority_events", [])
    actions = data.get("actions", [])
    receipts = data.get("receipts", [])

    participant_id = participant.get("agent_id")

    trace_by_id = {
        trace.get("trace_id"): trace
        for trace in traces
        if trace.get("trace_id")
    }

    action_by_id = {
        action.get("action_id"): action
        for action in actions
        if action.get("action_id")
    }

    # ---------------------------------------------------------
    # ZN-CONF-001 — Known Participant
    # ---------------------------------------------------------

    if not participant_id:
        add_error(
            errors,
            "ZN-CONF-001",
            "Fixture participant has no agent_id.",
        )

    for trace in traces:
        agent_id = trace.get("agent_id")

        if agent_id != participant_id:
            add_error(
                errors,
                "ZN-CONF-001",
                (
                    f"Trace {trace.get('trace_id')} references "
                    f"unknown or inconsistent participant {agent_id!r}."
                ),
            )

    for authority in authority_events:
        agent_id = authority.get("agent_id")

        if agent_id != participant_id:
            add_error(
                errors,
                "ZN-CONF-001",
                (
                    f"Authority event {authority.get('authority_id')} "
                    f"references unknown or inconsistent participant "
                    f"{agent_id!r}."
                ),
            )

    for action in actions:
        agent_id = action.get("agent_id")

        if agent_id != participant_id:
            add_error(
                errors,
                "ZN-CONF-001",
                (
                    f"Action {action.get('action_id')} references "
                    f"unknown or inconsistent participant {agent_id!r}."
                ),
            )

    for receipt in receipts:
        agent_id = receipt.get("agent_id")

        if agent_id != participant_id:
            add_error(
                errors,
                "ZN-CONF-001",
                (
                    f"Receipt {receipt.get('receipt_id')} references "
                    f"unknown or inconsistent participant {agent_id!r}."
                ),
            )

    # ---------------------------------------------------------
    # ZN-CONF-002 — Receipt References Existing Trace
    # ---------------------------------------------------------

    for receipt in receipts:
        trace_id = receipt.get("trace_id")

        if trace_id not in trace_by_id:
            add_error(
                errors,
                "ZN-CONF-002",
                (
                    f"Receipt {receipt.get('receipt_id')} references "
                    f"missing Trace {trace_id!r}."
                ),
            )

    # Actions should also reference existing Traces.
    for action in actions:
        trace_id = action.get("trace_id")

        if trace_id not in trace_by_id:
            add_error(
                errors,
                "ZN-CONF-002",
                (
                    f"Action {action.get('action_id')} references "
                    f"missing Trace {trace_id!r}."
                ),
            )

    # ---------------------------------------------------------
    # ZN-CONF-003 — Actor Consistency
    # ---------------------------------------------------------

    for receipt in receipts:
        trace = trace_by_id.get(receipt.get("trace_id"))

        if trace is None:
            continue

        if receipt.get("agent_id") != trace.get("agent_id"):
            add_error(
                errors,
                "ZN-CONF-003",
                (
                    f"Receipt {receipt.get('receipt_id')} agent_id "
                    f"{receipt.get('agent_id')!r} does not match "
                    f"Trace agent_id {trace.get('agent_id')!r}."
                ),
            )

    # ---------------------------------------------------------
    # ZN-CONF-004 / 005 — Authority Before Action + Scope
    # ---------------------------------------------------------

    for action in actions:
        if action.get("status") != "success":
            continue

        action_agent = action.get("agent_id")
        required_scope = action.get("required_scope")
        action_timestamp = action.get("timestamp")

        matching_authorities = []

        for authority in authority_events:
            if authority.get("agent_id") != action_agent:
                continue

            if authority.get("scope") != required_scope:
                continue

            matching_authorities.append(authority)

        allowed_authorities = [
            authority
            for authority in matching_authorities
            if authority.get("decision") == "allow"
        ]

        if not allowed_authorities:
            add_error(
                errors,
                "ZN-CONF-005",
                (
                    f"Action {action.get('action_id')} requires scope "
                    f"{required_scope!r}, but no matching ALLOW authority "
                    f"exists."
                ),
            )
            continue

        try:
            action_time = parse_time(action_timestamp)
        except Exception as exc:
            add_error(
                errors,
                "ZN-CONF-004",
                (
                    f"Action {action.get('action_id')} has invalid "
                    f"timestamp {action_timestamp!r}: {exc}"
                ),
            )
            continue

        valid_prior_authority = False

        for authority in allowed_authorities:
            try:
                authority_time = parse_time(authority.get("timestamp"))
            except Exception:
                continue

            if authority_time < action_time:
                valid_prior_authority = True
                break

        if not valid_prior_authority:
            add_error(
                errors,
                "ZN-CONF-004",
                (
                    f"Action {action.get('action_id')} occurred before "
                    f"valid authority was granted."
                ),
            )

    # ---------------------------------------------------------
    # ZN-CONF-006 — No Self-Escalation
    # ---------------------------------------------------------
    #
    # v0.1 fixtures currently do not model authority issuers.
    # Therefore this rule cannot yet be fully proven.
    #
    # Future fixture versions should add:
    #   issuer_id
    #   requester_id
    #   authority_source_type
    #
    # Until then, ZN-CONF-006 remains documented but not executable.

    # ---------------------------------------------------------
    # ZN-CONF-007 — Denied Action Produces No Execution Receipt
    # ---------------------------------------------------------

    denied_scopes = {
        (
            authority.get("agent_id"),
            authority.get("scope"),
        )
        for authority in authority_events
        if authority.get("decision") == "deny"
    }

    for receipt in receipts:
        receipt_agent = receipt.get("agent_id")
        scopes = receipt.get("authority_used", [])

        for scope in scopes:
            if (receipt_agent, scope) in denied_scopes:
                add_error(
                    errors,
                    "ZN-CONF-007",
                    (
                        f"Receipt {receipt.get('receipt_id')} uses denied "
                        f"authority scope {scope!r}."
                    ),
                )

    # ---------------------------------------------------------
    # ZN-CONF-008 — Failed Action Produces No Success Receipt
    # ---------------------------------------------------------

    failed_actions = {
        (
            action.get("agent_id"),
            action.get("trace_id"),
            action.get("action"),
        )
        for action in actions
        if action.get("status") == "failed"
    }

    for receipt in receipts:
        key = (
            receipt.get("agent_id"),
            receipt.get("trace_id"),
            receipt.get("action"),
        )

        if key in failed_actions:
            add_error(
                errors,
                "ZN-CONF-008",
                (
                    f"Receipt {receipt.get('receipt_id')} claims success "
                    f"for a failed action."
                ),
            )

    # ---------------------------------------------------------
    # ZN-CONF-009 — Successful External Action Requires Receipt
    # ---------------------------------------------------------

    for action in actions:
        if action.get("status") != "success":
            continue

        matching_receipts = [
            receipt
            for receipt in receipts
            if receipt.get("agent_id") == action.get("agent_id")
            and receipt.get("trace_id") == action.get("trace_id")
            and receipt.get("action") == action.get("action")
        ]

        if not matching_receipts:
            add_error(
                errors,
                "ZN-CONF-009",
                (
                    f"Successful action {action.get('action_id')} has "
                    f"no authoritative Receipt."
                ),
            )

    # ---------------------------------------------------------
    # ZN-CONF-010 — No Duplicate Authoritative Receipt
    # ---------------------------------------------------------

    for action in actions:
        if action.get("status") != "success":
            continue

        matching_receipts = [
            receipt
            for receipt in receipts
            if receipt.get("agent_id") == action.get("agent_id")
            and receipt.get("trace_id") == action.get("trace_id")
            and receipt.get("action") == action.get("action")
        ]

        unique_receipt_ids = {
            receipt.get("receipt_id")
            for receipt in matching_receipts
        }

        if len(unique_receipt_ids) > 1:
            add_error(
                errors,
                "ZN-CONF-010",
                (
                    f"Action {action.get('action_id')} has multiple "
                    f"authoritative Receipts: "
                    f"{sorted(unique_receipt_ids)}"
                ),
            )

    # ---------------------------------------------------------
    # ZN-CONF-011 — Trace Causality Must Not Self-Reference
    # ---------------------------------------------------------

    for trace in traces:
        trace_id = trace.get("trace_id")
        parent_trace_id = trace.get("parent_trace_id")

        if parent_trace_id is not None and parent_trace_id == trace_id:
            add_error(
                errors,
                "ZN-CONF-011",
                f"Trace {trace_id} references itself as parent.",
            )

    # Optional cycle detection.
    parent_map = {
        trace.get("trace_id"): trace.get("parent_trace_id")
        for trace in traces
        if trace.get("trace_id")
    }

    for start_trace_id in parent_map:
        seen = set()
        current = start_trace_id

        while current is not None and current in parent_map:
            if current in seen:
                add_error(
                    errors,
                    "ZN-CONF-011",
                    (
                        f"Causal cycle detected starting from Trace "
                        f"{start_trace_id}."
                    ),
                )
                break

            seen.add(current)
            current = parent_map.get(current)

    # ---------------------------------------------------------
    # ZN-CONF-012 — Receipt Must Not Predate Action
    # ---------------------------------------------------------

    for receipt in receipts:
        matching_actions = [
            action
            for action in actions
            if action.get("agent_id") == receipt.get("agent_id")
            and action.get("trace_id") == receipt.get("trace_id")
            and action.get("action") == receipt.get("action")
        ]

        if not matching_actions:
            continue

        try:
            receipt_time = parse_time(receipt.get("timestamp"))
        except Exception as exc:
            add_error(
                errors,
                "ZN-CONF-012",
                (
                    f"Receipt {receipt.get('receipt_id')} has invalid "
                    f"timestamp: {exc}"
                ),
            )
            continue

        for action in matching_actions:
            try:
                action_time = parse_time(action.get("timestamp"))
            except Exception:
                continue

            if receipt_time < action_time:
                add_error(
                    errors,
                    "ZN-CONF-012",
                    (
                        f"Receipt {receipt.get('receipt_id')} predates "
                        f"action {action.get('action_id')}."
                    ),
                )

    return errors


def validate_directory(
    directory: Path,
    expected_valid: bool,
) -> int:
    failures = 0

    label = "PASS" if expected_valid else "FAIL"

    print(f"\n=== Conformance {label} examples ===")

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

        except (json.JSONDecodeError, OSError, TypeError, ValueError) as exc:
            failures += 1

            print(f"[FAIL] {path.relative_to(ROOT)}")
            print(f"       - Fixture could not be evaluated: {exc}")

    return failures


def main() -> int:
    print("AI Zero Network v0.1 conformance validator")
    print("==========================================")

    required_paths = [
        PASS_DIR,
        FAIL_DIR,
    ]

    for path in required_paths:
        if not path.exists():
            print(f"[ERROR] Required path does not exist: {path}")
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
            f"FAILED: {failures} conformance expectation(s) failed."
        )
        return 1

    print(
        "PASS: all AI Zero Network v0.1 "
        "conformance fixtures behaved as expected."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
