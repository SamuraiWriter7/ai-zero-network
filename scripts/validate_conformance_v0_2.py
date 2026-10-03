#!/usr/bin/env python3

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]

PASS_DIR = ROOT / "examples" / "v0.2" / "conformance" / "pass"
FAIL_DIR = ROOT / "examples" / "v0.2" / "conformance" / "fail"


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def parse_time(value: str) -> datetime:
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    return datetime.fromisoformat(value)


def add_error(errors: List[str], rule: str, message: str) -> None:
    errors.append(f"{rule}: {message}")


def validate_fixture(data: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    participants = data.get("participants", [])
    authorities = data.get("authorities", [])
    actions = data.get("actions", [])
    receipts = data.get("receipts", [])

    participant_ids = {
        item.get("agent_id")
        for item in participants
        if item.get("agent_id")
    }

    authority_by_id = {
        item.get("authority_id"): item
        for item in authorities
        if item.get("authority_id")
    }

    action_by_id = {
        item.get("action_id"): item
        for item in actions
        if item.get("action_id")
    }

    # ---------------------------------------------------------
    # Basic participant consistency
    # ---------------------------------------------------------

    for authority in authorities:
        for field in ("requester_id", "issuer_id", "subject_id"):
            value = authority.get(field)

            if value not in participant_ids:
                add_error(
                    errors,
                    "ZN-AUTH-001",
                    (
                        f"Authority {authority.get('authority_id')} "
                        f"references unknown participant "
                        f"{field}={value!r}."
                    ),
                )

    for action in actions:
        agent_id = action.get("agent_id")

        if agent_id not in participant_ids:
            add_error(
                errors,
                "ZN-AUTH-001",
                (
                    f"Action {action.get('action_id')} references "
                    f"unknown participant {agent_id!r}."
                ),
            )

    for receipt in receipts:
        agent_id = receipt.get("agent_id")

        if agent_id not in participant_ids:
            add_error(
                errors,
                "ZN-AUTH-001",
                (
                    f"Receipt {receipt.get('receipt_id')} references "
                    f"unknown participant {agent_id!r}."
                ),
            )

    # ---------------------------------------------------------
    # ZN-AUTH-002 — No self-escalation
    # ---------------------------------------------------------

    for authority in authorities:
        if authority.get("decision") != "allow":
            continue

        requester_id = authority.get("requester_id")
        issuer_id = authority.get("issuer_id")
        subject_id = authority.get("subject_id")
        source_type = authority.get("source_type")

        if (
            requester_id
            and requester_id == issuer_id
            and requester_id == subject_id
            and source_type != "policy"
        ):
            add_error(
                errors,
                "ZN-AUTH-002",
                (
                    f"Authority {authority.get('authority_id')} "
                    f"appears to be self-issued by {requester_id!r}."
                ),
            )

    # ---------------------------------------------------------
    # Authority internal lifecycle sanity
    # ---------------------------------------------------------

    for authority in authorities:
        authority_id = authority.get("authority_id")

        issued_at = authority.get("issued_at")
        expires_at = authority.get("expires_at")
        revoked_at = authority.get("revoked_at")

        try:
            issued_time = parse_time(issued_at)
        except Exception as exc:
            add_error(
                errors,
                "ZN-AUTH-003",
                f"Authority {authority_id} has invalid issued_at: {exc}",
            )
            continue

        if expires_at is not None:
            try:
                expires_time = parse_time(expires_at)

                if expires_time <= issued_time:
                    add_error(
                        errors,
                        "ZN-AUTH-003",
                        (
                            f"Authority {authority_id} expires at or before "
                            f"its issuance time."
                        ),
                    )
            except Exception as exc:
                add_error(
                    errors,
                    "ZN-AUTH-003",
                    f"Authority {authority_id} has invalid expires_at: {exc}",
                )

        if revoked_at is not None:
            try:
                revoked_time = parse_time(revoked_at)

                if revoked_time < issued_time:
                    add_error(
                        errors,
                        "ZN-AUTH-004",
                        (
                            f"Authority {authority_id} is revoked before "
                            f"it was issued."
                        ),
                    )
            except Exception as exc:
                add_error(
                    errors,
                    "ZN-AUTH-004",
                    f"Authority {authority_id} has invalid revoked_at: {exc}",
                )

    # ---------------------------------------------------------
    # ZN-DELEG-001 / 002 / 003 / 004
    # ---------------------------------------------------------

    for authority in authorities:
        if authority.get("source_type") != "delegated":
            continue

        authority_id = authority.get("authority_id")
        parent_id = authority.get("delegation_parent")

        parent = authority_by_id.get(parent_id)

        if parent is None:
            add_error(
                errors,
                "ZN-DELEG-001",
                (
                    f"Delegated authority {authority_id} references "
                    f"missing parent {parent_id!r}."
                ),
            )
            continue

        # Parent must itself be usable.
        if parent.get("decision") != "allow":
            add_error(
                errors,
                "ZN-DELEG-002",
                (
                    f"Delegated authority {authority_id} derives from "
                    f"non-allowed parent {parent_id}."
                ),
            )

        try:
            child_issued = parse_time(authority.get("issued_at"))
        except Exception:
            child_issued = None

        try:
            parent_issued = parse_time(parent.get("issued_at"))
        except Exception:
            parent_issued = None

        if (
            child_issued is not None
            and parent_issued is not None
            and child_issued < parent_issued
        ):
            add_error(
                errors,
                "ZN-DELEG-002",
                (
                    f"Delegated authority {authority_id} was issued "
                    f"before parent {parent_id} existed."
                ),
            )

        parent_revoked_at = parent.get("revoked_at")

        if parent_revoked_at is not None and child_issued is not None:
            try:
                parent_revoked = parse_time(parent_revoked_at)

                if child_issued >= parent_revoked:
                    add_error(
                        errors,
                        "ZN-DELEG-002",
                        (
                            f"Delegated authority {authority_id} was issued "
                            f"after parent {parent_id} was revoked."
                        ),
                    )
            except Exception:
                pass

        parent_expires_at = parent.get("expires_at")

        if parent_expires_at is not None and child_issued is not None:
            try:
                parent_expires = parse_time(parent_expires_at)

                if child_issued >= parent_expires:
                    add_error(
                        errors,
                        "ZN-DELEG-002",
                        (
                            f"Delegated authority {authority_id} was issued "
                            f"after parent {parent_id} expired."
                        ),
                    )
            except Exception:
                pass

        # Child scope must be subset of parent scope.
        parent_scope = set(parent.get("scope", []))
        child_scope = set(authority.get("scope", []))

        excess_scope = child_scope - parent_scope

        if excess_scope:
            add_error(
                errors,
                "ZN-DELEG-003",
                (
                    f"Delegated authority {authority_id} exceeds parent "
                    f"scope with {sorted(excess_scope)}."
                ),
            )

        # Child lifetime must not exceed parent lifetime.
        child_expires_at = authority.get("expires_at")

        if (
            parent_expires_at is not None
            and child_expires_at is None
        ):
            add_error(
                errors,
                "ZN-DELEG-004",
                (
                    f"Delegated authority {authority_id} has no expiration "
                    f"while parent {parent_id} is time-bounded."
                ),
            )

        elif (
            parent_expires_at is not None
            and child_expires_at is not None
        ):
            try:
                parent_expires = parse_time(parent_expires_at)
                child_expires = parse_time(child_expires_at)

                if child_expires > parent_expires:
                    add_error(
                        errors,
                        "ZN-DELEG-004",
                        (
                            f"Delegated authority {authority_id} expires "
                            f"after parent {parent_id}."
                        ),
                    )
            except Exception:
                pass

    # ---------------------------------------------------------
    # ZN-DELEG-005 — Parent revocation propagates downward
    # ---------------------------------------------------------

    for authority in authorities:
        if authority.get("source_type") != "delegated":
            continue

        parent = authority_by_id.get(authority.get("delegation_parent"))

        if parent is None:
            continue

        parent_revoked_at = parent.get("revoked_at")

        if parent_revoked_at is None:
            continue

        for action in actions:
            refs = action.get("authority_refs", [])

            if authority.get("authority_id") not in refs:
                continue

            try:
                action_time = parse_time(action.get("timestamp"))
                revoked_time = parse_time(parent_revoked_at)

                if action_time >= revoked_time:
                    add_error(
                        errors,
                        "ZN-DELEG-005",
                        (
                            f"Action {action.get('action_id')} uses child "
                            f"authority {authority.get('authority_id')} "
                            f"after parent authority was revoked."
                        ),
                    )
            except Exception:
                pass

    # ---------------------------------------------------------
    # Action authority validation
    # ZN-AUTH-003 / 004 / 005 / 006 / 007
    # ---------------------------------------------------------

    for action in actions:
        if action.get("status") != "success":
            continue

        action_id = action.get("action_id")
        action_agent = action.get("agent_id")
        required_scope = action.get("required_scope")
        authority_refs = action.get("authority_refs", [])

        try:
            action_time = parse_time(action.get("timestamp"))
        except Exception as exc:
            add_error(
                errors,
                "ZN-AUTH-003",
                f"Action {action_id} has invalid timestamp: {exc}",
            )
            continue

        if not authority_refs:
            add_error(
                errors,
                "ZN-AUTH-001",
                f"Action {action_id} has no authority_refs.",
            )
            continue

        scope_satisfied = False

        for authority_ref in authority_refs:
            authority = authority_by_id.get(authority_ref)

            if authority is None:
                add_error(
                    errors,
                    "ZN-AUTH-001",
                    (
                        f"Action {action_id} references missing authority "
                        f"{authority_ref!r}."
                    ),
                )
                continue

            if authority.get("decision") != "allow":
                add_error(
                    errors,
                    "ZN-AUTH-005",
                    (
                        f"Action {action_id} uses denied authority "
                        f"{authority_ref}."
                    ),
                )

            if authority.get("subject_id") != action_agent:
                add_error(
                    errors,
                    "ZN-AUTH-007",
                    (
                        f"Action {action_id} by {action_agent!r} uses "
                        f"authority {authority_ref} issued to "
                        f"{authority.get('subject_id')!r}."
                    ),
                )

            if required_scope in authority.get("scope", []):
                scope_satisfied = True

            try:
                issued_time = parse_time(authority.get("issued_at"))

                if action_time < issued_time:
                    add_error(
                        errors,
                        "ZN-AUTH-003",
                        (
                            f"Action {action_id} occurred before authority "
                            f"{authority_ref} was issued."
                        ),
                    )
            except Exception:
                pass

            expires_at = authority.get("expires_at")

            if expires_at is not None:
                try:
                    expires_time = parse_time(expires_at)

                    if action_time >= expires_time:
                        add_error(
                            errors,
                            "ZN-AUTH-003",
                            (
                                f"Action {action_id} uses expired authority "
                                f"{authority_ref}."
                            ),
                        )
                except Exception:
                    pass

            revoked_at = authority.get("revoked_at")

            if revoked_at is not None:
                try:
                    revoked_time = parse_time(revoked_at)

                    if action_time >= revoked_time:
                        add_error(
                            errors,
                            "ZN-AUTH-004",
                            (
                                f"Action {action_id} uses revoked authority "
                                f"{authority_ref}."
                            ),
                        )
                except Exception:
                    pass

        if not scope_satisfied:
            add_error(
                errors,
                "ZN-AUTH-006",
                (
                    f"Action {action_id} requires scope "
                    f"{required_scope!r}, but referenced authorities "
                    f"do not provide it."
                ),
            )

    # ---------------------------------------------------------
    # Receipt linkage to action and authority provenance
    # ---------------------------------------------------------

    for receipt in receipts:
        receipt_id = receipt.get("receipt_id")
        action_id = receipt.get("action_id")
        action = action_by_id.get(action_id)

        if action is None:
            add_error(
                errors,
                "ZN-AUTH-001",
                (
                    f"Receipt {receipt_id} references missing action "
                    f"{action_id!r}."
                ),
            )
            continue

        if receipt.get("agent_id") != action.get("agent_id"):
            add_error(
                errors,
                "ZN-AUTH-007",
                (
                    f"Receipt {receipt_id} actor does not match "
                    f"action {action_id} actor."
                ),
            )

        action_refs = set(action.get("authority_refs", []))
        receipt_refs = set(receipt.get("authority_refs", []))

        if action_refs != receipt_refs:
            add_error(
                errors,
                "ZN-AUTH-001",
                (
                    f"Receipt {receipt_id} authority_refs do not match "
                    f"action {action_id} authority_refs."
                ),
            )

        for authority_ref in receipt_refs:
            if authority_ref not in authority_by_id:
                add_error(
                    errors,
                    "ZN-AUTH-001",
                    (
                        f"Receipt {receipt_id} references missing authority "
                        f"{authority_ref!r}."
                    ),
                )

        try:
            receipt_time = parse_time(receipt.get("timestamp"))
            action_time = parse_time(action.get("timestamp"))

            if receipt_time < action_time:
                add_error(
                    errors,
                    "ZN-AUTH-001",
                    (
                        f"Receipt {receipt_id} predates "
                        f"action {action_id}."
                    ),
                )
        except Exception:
            pass

    return errors


def validate_directory(
    directory: Path,
    expected_valid: bool,
) -> int:
    failures = 0

    label = "PASS" if expected_valid else "FAIL"

    print(f"\n=== v0.2 Conformance {label} examples ===")

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
    print("AI Zero Network v0.2 conformance validator")
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
            f"FAILED: {failures} v0.2 conformance "
            f"expectation(s) failed."
        )
        return 1

    print(
        "PASS: all AI Zero Network v0.2 "
        "conformance fixtures behaved as expected."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
