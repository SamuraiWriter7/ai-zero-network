# AI Zero Network v0.1 Conformance

**Status:** Draft  
**Version:** v0.1  
**Scope:** Semantic conformance rules for AI Zero Network v0.1

---

## 1. Purpose

This document defines semantic conformance requirements for AI Zero Network v0.1.

The JSON Schemas validate whether individual Trace and Receipt documents are structurally valid.

This document defines whether multiple records, authority decisions, and external actions form a valid Zero Network lifecycle.

The distinction is:

```text
JSON Schema Validation
=
Is this individual document structurally valid?

Conformance Validation
=
Did the system behave according to Zero Network rules?
```

A document MAY be schema-valid while the overall system behavior is non-conforming.

---

## 2. Conformance Model

AI Zero Network v0.1 uses the following minimum lifecycle:

```text
Participant
    ↓
Trace
    ↓
Action Request
    ↓
Authority Validation
    ↓
 ┌──┴───┐
DENY   ALLOW
 │       │
Trace    ↓
      External Action
          ↓
       Receipt
```

The core rule is:

> **External effect MUST be preceded by valid authority and followed by a Receipt.**

---

## 3. Conformance Levels

v0.1 defines two levels of validation.

### Level 1 — Schema Conformance

Validates individual JSON documents against:

```text
schemas/trace-v0.1.schema.json
schemas/receipt-v0.1.schema.json
```

Level 1 checks syntax and document structure.

Examples:

- required fields,
- UUID format,
- timestamps,
- allowed event types,
- hash format,
- risk score range,
- non-empty authority scopes.

---

### Level 2 — Lifecycle Conformance

Validates relationships between:

- participants,
- Trace records,
- authority decisions,
- external actions,
- and Receipts.

Level 2 determines whether system behavior respects Zero Network invariants.

---

# 4. Core Conformance Rules

## ZN-CONF-001 — Known Participant

Every Trace and Receipt MUST reference a participant known to the Zero Network.

The participant identifier MUST NOT silently refer to multiple distinct actors.

Example:

```text
agent_id = agent-finance-001
```

MUST resolve consistently to the same logical participant within the applicable identity domain.

### PASS

```text
registered participant:
agent-finance-001

Trace:
agent-finance-001

Receipt:
agent-finance-001
```

### FAIL

```text
Receipt:
agent-unknown-999

No corresponding registered participant exists.
```

---

## ZN-CONF-002 — Receipt References Existing Trace

Every Receipt MUST reference an existing Trace through `trace_id`.

### PASS

```text
Trace:
trace_id = T-001

Receipt:
trace_id = T-001
```

### FAIL

```text
Receipt:
trace_id = T-999

No Trace T-999 exists.
```

A Receipt without a corresponding Trace cannot be considered valid Zero Network history.

---

## ZN-CONF-003 — Actor Consistency

The `agent_id` in a Receipt MUST match the actor associated with the Trace referenced by that Receipt unless an explicitly defined delegation mechanism exists.

Delegation is outside the scope of v0.1.

Therefore, in v0.1:

```text
Trace.agent_id
MUST equal
Receipt.agent_id
```

### PASS

```text
Trace.agent_id   = agent-a
Receipt.agent_id = agent-a
```

### FAIL

```text
Trace.agent_id   = agent-a
Receipt.agent_id = agent-b
```

---

## ZN-CONF-004 — Authority Before Action

Every externally effective action MUST be preceded by successful authority validation.

The authority decision MUST occur before the external action.

Conceptually:

```text
authority_granted.timestamp
<
external_action.timestamp
```

An implementation MAY represent authority validation using:

- a dedicated authority record,
- an authorization token,
- a signed capability,
- a policy engine decision,
- or another verifiable mechanism.

The mechanism is implementation-defined.

The ordering requirement is not.

### PASS

```text
10:00:00 authority granted
10:00:02 external action
10:00:03 Receipt emitted
```

### FAIL

```text
10:00:00 external action
10:00:02 authority granted
```

Later authorization MUST NOT retroactively legitimize an earlier unauthorized action.

---

## ZN-CONF-005 — Authority Scope Covers Action

The authority used for an action MUST permit that action.

Example:

```text
action:
write_external_record

required scope:
write:document
```

The following is conforming:

```text
authority_used:
- write:document
```

The following is not:

```text
authority_used:
- read:document
```

Authority validation MUST consider the actual effective action, not merely whether the participant possessed some unrelated permission.

---

## ZN-CONF-006 — No Self-Escalation

A participant MUST NOT create or expand its own authority and treat that authority as valid without an external authorization source.

### FAIL

```text
Agent has:
read:market

Agent modifies local state to:
read:market
write:order

Agent executes write:order
```

This violates Zero Network conformance even if the resulting Receipt is structurally valid.

Authority changes MUST originate from an authority source outside the requesting participant's unilateral control.

---

## ZN-CONF-007 — Denied Action Produces No Execution Receipt

If an action request is denied, the denied attempt MAY produce one or more Trace records.

It MUST NOT produce a Receipt claiming successful external execution.

### PASS

```text
Trace:
authority_request

Trace:
authority_denied

No execution Receipt
```

### FAIL

```text
Trace:
authority_denied

Receipt:
action = submit_external_order
```

A denial is observable history.

It is not an executed external effect.

---

## ZN-CONF-008 — Failed Action Produces No Success Receipt

If an authorized external action fails before producing its intended external effect, it MUST NOT produce a Receipt claiming successful completion.

The failure SHOULD produce a Trace.

### PASS

```text
authority granted
↓
external action attempted
↓
execution failed
↓
error Trace
```

### FAIL

```text
execution failed
↓
Receipt claims action completed
```

Receipt semantics in v0.1 are intentionally strict:

> **Receipt means effective action occurred.**

---

## ZN-CONF-009 — Successful External Action Requires Receipt

Every successfully completed externally effective action MUST produce exactly one authoritative execution Receipt for that action instance.

An implementation MAY create supplementary records, but MUST NOT omit the authoritative Receipt.

### FAIL

```text
authority granted
↓
external state changed
↓
no Receipt
```

This is a receiptless effect and violates the Zero Network model.

---

## ZN-CONF-010 — No Duplicate Authoritative Receipt

One external action instance MUST NOT produce multiple independent authoritative Receipts that represent the same execution as separate events.

This prevents duplicated history and future double-counting of:

- resource usage,
- contribution,
- attribution,
- payment,
- or value distribution.

Duplicate transport or replicated storage copies are allowed if they retain the same `receipt_id`.

### PASS

```text
receipt_id = R-001
replicated across three storage nodes
```

### FAIL

```text
Same action instance

receipt_id = R-001
receipt_id = R-002

Both independently claim to be the authoritative execution Receipt.
```

---

## ZN-CONF-011 — Trace Causality Must Not Self-Reference

A Trace MUST NOT reference itself as its own `parent_trace_id`.

### FAIL

```text
trace_id        = T-001
parent_trace_id = T-001
```

An implementation SHOULD also detect causal loops when practical.

Example:

```text
T-001 → T-002 → T-003 → T-001
```

Full cycle detection is RECOMMENDED but not required for minimal v0.1 conformance.

---

## ZN-CONF-012 — Receipt Time Must Not Precede Its Effective Action

A Receipt timestamp MUST represent the completion of, or a time after, the externally effective action it proves.

A Receipt MUST NOT predate the action.

Conceptually:

```text
authority validation
    ≤
action execution
    ≤
Receipt timestamp
```

---

# 5. Recommended Temporal Ordering

A conforming successful lifecycle SHOULD follow:

```text
T0  identity available
T1  action request Trace
T2  authority validation
T3  external action begins
T4  external effect confirmed
T5  action completion Trace
T6  Receipt emitted
```

Not every implementation must expose all six events.

However, the following relationship MUST hold:

```text
Authority
    before
External Effect
    before or at
Receipt
```

---

# 6. Minimal Successful Conformance Case

Example:

```text
Participant:
agent-finance-001

Trace T1:
type = authority_request
action = submit_external_order

Authority:
write:order = ALLOW

External Action:
submit_external_order succeeds

Trace T2:
type = action_completed
parent = T1

Receipt R1:
trace_id = T2
agent_id = agent-finance-001
authority_used = write:order
```

Result:

```text
CONFORMING
```

---

# 7. Minimal Denied Conformance Case

```text
Participant:
agent-finance-001

Trace T1:
type = authority_request

Authority:
write:order = DENY

Trace T2:
type = authority_denied
parent = T1

No external action
No execution Receipt
```

Result:

```text
CONFORMING
```

A denied action is not a failure of Zero Network.

It is a valid observable outcome.

---

# 8. Minimal Failed Execution Case

```text
Trace T1:
action_requested

Authority:
ALLOW

External action attempted

Execution:
FAILED

Trace T2:
error

No execution Receipt
```

Result:

```text
CONFORMING
```

The system remains conforming because it did not falsely convert an unsuccessful attempt into authoritative history.

---

# 9. Non-Conforming Lifecycle Examples

## FAIL-CONF-001 — Unknown Actor

```text
Receipt references an unregistered agent_id.
```

Violates:

`ZN-CONF-001`

---

## FAIL-CONF-002 — Missing Referenced Trace

```text
Receipt.trace_id does not resolve to an existing Trace.
```

Violates:

`ZN-CONF-002`

---

## FAIL-CONF-003 — Actor Mismatch

```text
Trace.agent_id != Receipt.agent_id
```

Violates:

`ZN-CONF-003`

---

## FAIL-CONF-004 — Action Before Authorization

```text
External action occurred before authority validation.
```

Violates:

`ZN-CONF-004`

---

## FAIL-CONF-005 — Wrong Authority Scope

```text
Agent performs write action using read-only authority.
```

Violates:

`ZN-CONF-005`

---

## FAIL-CONF-006 — Self-Escalated Permission

```text
Agent grants itself a new permission and uses it.
```

Violates:

`ZN-CONF-006`

---

## FAIL-CONF-007 — Receipt After Denial

```text
Authority = DENY
but successful execution Receipt exists.
```

Violates:

`ZN-CONF-007`

---

## FAIL-CONF-008 — False Success Receipt

```text
Execution failed
but Receipt claims successful effect.
```

Violates:

`ZN-CONF-008`

---

## FAIL-CONF-009 — Receiptless Effect

```text
External state changed successfully
but no Receipt exists.
```

Violates:

`ZN-CONF-009`

---

## FAIL-CONF-010 — Duplicate Receipt

```text
One action instance generates multiple authoritative receipt_ids.
```

Violates:

`ZN-CONF-010`

---

## FAIL-CONF-011 — Self-Referencing Trace

```text
trace_id == parent_trace_id
```

Violates:

`ZN-CONF-011`

---

## FAIL-CONF-012 — Receipt Predates Action

```text
Receipt timestamp occurs before the action it claims to prove.
```

Violates:

`ZN-CONF-012`

---

# 10. Schema Validation vs Semantic Validation

Some rules can be enforced by JSON Schema.

Others require cross-record validation.

| Rule | JSON Schema | Conformance Validator |
|---|---:|---:|
| Required Trace fields | Yes | No |
| Allowed Trace type | Yes | No |
| UUID format | Yes | No |
| Risk range | Yes | No |
| Non-empty authority_used | Yes | No |
| Referenced Trace exists | No | Yes |
| Trace/Receipt actor match | No | Yes |
| Authority before action | No | Yes |
| Scope permits action | No | Yes |
| No self-escalation | No | Yes |
| No Receipt after denial | No | Yes |
| Successful action has Receipt | No | Yes |
| Duplicate action Receipt detection | No | Yes |

This separation MUST remain explicit.

JSON Schema MUST NOT be treated as proof of full Zero Network conformance.

---

# 11. Conformance Validator Responsibilities

A future semantic validator SHOULD evaluate at least:

```text
1. participant existence
2. Trace existence
3. Trace → Receipt linkage
4. actor consistency
5. authority decision ordering
6. authority scope compatibility
7. denial / execution consistency
8. execution / Receipt consistency
9. duplicate Receipt detection
10. causal reference sanity
```

A validator MAY operate on:

- individual event bundles,
- append-only logs,
- database records,
- streamed events,
- signed audit packages,
- or exported conformance fixtures.

---

# 12. Event Bundle Model

For testing purposes, a future conformance fixture MAY group related events into one bundle.

Example conceptual structure:

```json
{
  "participant": {},
  "traces": [],
  "authority_events": [],
  "actions": [],
  "receipts": []
}
```

This bundle format is NOT normative in v0.1.

It is reserved as a possible test representation for future validators.

---

# 13. Trust Boundary

Zero Network conformance does not mean that every participant is trustworthy.

It means that behavior is constrained enough to be:

```text
identifiable
+
observable
+
authority-bounded
+
evidenced
```

Therefore:

```text
Conformance ≠ Trust

Conformance = Minimum structural accountability
```

This distinction is fundamental.

---

# 14. Meteorology Compatibility

The conformance rules intentionally preserve data needed for future field-level observation.

For example:

```text
Trace density
→ activity pressure

authority_request density
→ permission pressure

Receipt density
→ effective activity

authority_used
→ effective authority distribution

parent_trace_id
→ causal flow

region
→ observation zone
```

AI Meteorology is not part of v0.1 conformance.

v0.1 only ensures that future Meteorology layers can observe meaningful network behavior.

---

# 15. Royalty and Contribution Compatibility

Receipt records MAY later support:

- attribution,
- resource accounting,
- contribution accounting,
- royalty distribution,
- value redistribution,
- and provenance.

However, v0.1 MUST NOT infer economic value merely from the existence of a Receipt.

A Receipt proves an effective action.

It does not automatically determine the value of that action.

---

# 16. Minimum Conformance Statement

An AI Zero Network v0.1 implementation is semantically conforming when:

```text
Every effective actor is identifiable.

Every meaningful network-visible event is traceable.

Every external effect is preceded by valid authority.

Every successful external effect leaves an authoritative Receipt.

No denied or failed action is represented as successful history.
```

In compact form:

> **Identity → Trace → Authority → Effect → Receipt**

This sequence is the minimum semantic backbone of AI Zero Network v0.1.

---

# 17. Zero Network Rule

The entire v0.1 conformance model can be reduced to five prohibitions:

> **No invisible actor.**  
> **No invisible transition.**  
> **No authorityless effect.**  
> **No false Receipt.**  
> **No receiptless effect.**

Everything beyond this belongs to higher layers.
