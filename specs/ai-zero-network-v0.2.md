# AI Zero Network v0.2

## Authority Provenance and Bounded Delegation

**Status:** Draft  
**Version:** v0.2  
**Scope:** Authority provenance, lifecycle, expiration, revocation, and bounded delegation  
**Repository:** `ai-zero-network`

---

## 1. Purpose

AI Zero Network v0.2 extends v0.1 by making authority itself observable, attributable, and verifiable.

v0.1 established the minimum lifecycle:

```text
Identity
   ↓
Trace
   ↓
Authority Validation
   ↓
External Effect
   ↓
Receipt
```

However, v0.1 intentionally left several authority questions unresolved:

- Who issued the authority?
- Who requested it?
- Where did the authority originate?
- When does it expire?
- Can it be revoked?
- Can it be delegated?
- Can an agent grant authority to itself?
- Can a delegated agent exceed the scope of its parent authority?

v0.2 addresses these questions.

The central objective is:

> **No authority without provenance. No delegation beyond its source.**

---

# 2. Relationship to v0.1

AI Zero Network v0.2 preserves the core invariants of v0.1.

The following remain mandatory:

1. participants are identifiable;
2. meaningful network-visible events are traceable;
3. external effects require prior authority;
4. successful external effects produce Receipts.

v0.2 adds a fifth requirement:

5. **used authority MUST have a verifiable origin and valid lifecycle state.**

The lifecycle therefore becomes:

```text
Identity
   ↓
Trace
   ↓
Authority Request
   ↓
Authority Provenance
   ↓
Authority Validation
   ↓
External Effect
   ↓
Receipt
```

---

# 3. Design Principle

v0.2 introduces four additional design principles.

## 3.1 Authority has an origin

Every usable authority MUST identify the authority source that issued it.

## 3.2 Authority is bounded

Authority MUST NOT silently expand beyond its granted scope.

## 3.3 Authority has a lifecycle

Authority MAY expire or be revoked.

An expired or revoked authority MUST NOT authorize new external effects.

## 3.4 Delegation cannot create authority from nothing

Delegated authority MUST derive from valid parent authority.

A child authority MUST NOT exceed its parent.

---

# 4. Normative Language

The keywords **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are normative.

---

# 5. Authority Record

v0.2 introduces the normative **Authority Record**.

Conceptually:

```json
{
  "authority_id": "uuid",
  "requester_id": "agent-a",
  "issuer_id": "human-admin-001",
  "subject_id": "agent-a",
  "scope": [
    "write:document"
  ],
  "decision": "allow",
  "source_type": "human",
  "issued_at": "2026-10-03T01:00:00+09:00",
  "expires_at": "2026-10-03T02:00:00+09:00",
  "revoked_at": null,
  "delegation_parent": null
}
```

The canonical machine-readable definition SHOULD be provided by:

```text
schemas/authority-v0.2.schema.json
```

---

# 6. Authority Roles

v0.2 distinguishes three roles.

## 6.1 Requester

The participant requesting authority.

```text
requester_id
```

The requester asks for permission.

The requester does not necessarily receive it.

---

## 6.2 Issuer

The authority source that makes the authorization decision.

```text
issuer_id
```

Examples MAY include:

- a human,
- an organization policy service,
- an authorization server,
- a governance agent,
- a hardware-backed authority service,
- another explicitly trusted authority source.

---

## 6.3 Subject

The participant that receives and may use the authority.

```text
subject_id
```

Often:

```text
requester_id == subject_id
```

but this is not required.

For example, a human administrator MAY authorize another agent on behalf of a requesting coordinator.

---

# 7. Authority Source Types

An Authority Record SHOULD declare its source type.

Minimum v0.2 source types are:

```text
human
policy
service
delegated
```

Implementations MAY extend this list in later versions.

### human

Authority directly issued by a human or human-controlled authority system.

### policy

Authority issued by a deterministic or externally governed policy.

### service

Authority issued by a recognized authorization service.

### delegated

Authority derived from another valid Authority Record.

---

# 8. Core Authority Invariants

## ZN-AUTH-001 — Authority MUST Have Provenance

Every allowed authority MUST identify:

```text
authority_id
issuer_id
subject_id
scope
decision
issued_at
source_type
```

Authority without an identifiable issuer MUST NOT authorize an external action.

---

## ZN-AUTH-002 — Requester MUST NOT Unilaterally Become Issuer

A participant MUST NOT request authority and unilaterally issue that same new authority to itself unless a separately governed policy explicitly authorizes such issuance.

Default v0.2 behavior:

```text
requester_id == issuer_id
```

for newly expanded authority is non-conforming.

Example:

```text
agent-a currently has:
read:document

agent-a requests:
write:document

agent-a issues:
write:document

agent-a uses:
write:document
```

Result:

```text
NON-CONFORMING
```

---

## ZN-AUTH-003 — Authority MUST Be Valid at Action Time

An authority used for an external action MUST be valid when that action occurs.

Conceptually:

```text
issued_at
    ≤
action.timestamp
    <
expires_at
```

when `expires_at` exists.

If no expiration exists, implementation policy determines lifetime.

---

## ZN-AUTH-004 — Revoked Authority MUST NOT Be Used

If:

```text
revoked_at <= action.timestamp
```

the authority is invalid for that action.

An authority MAY remain valid for historical verification of actions performed before revocation.

Revocation does not rewrite history.

---

## ZN-AUTH-005 — Denied Authority MUST NOT Authorize Action

An Authority Record with:

```text
decision = deny
```

MUST NOT be used as authority for an external effect.

A denied authority request SHOULD remain observable through Trace and/or Authority records.

---

## ZN-AUTH-006 — Scope MUST Cover Action

Authority scope MUST cover the effective action.

Example:

```text
granted:
read:document

required:
write:document
```

Result:

```text
NON-CONFORMING
```

---

## ZN-AUTH-007 — Authority MUST Belong to Subject

An authority issued to:

```text
subject_id = agent-a
```

MUST NOT be used directly by:

```text
agent-b
```

unless a valid delegation exists.

---

# 9. Authority Lifecycle

An authority MAY move through the following lifecycle:

```text
requested
   ↓
allowed / denied
   ↓
active
   ↓
expired / revoked
```

A denied authority never becomes active unless a new Authority Record is issued.

Expiration and revocation are distinct.

### Expiration

Authority becomes invalid because its predefined validity period ends.

### Revocation

Authority is actively invalidated before its natural expiration.

---

# 10. Expiration

An Authority Record MAY include:

```text
expires_at
```

When present:

```text
issued_at < expires_at
```

MUST hold.

An action occurring at or after `expires_at` MUST NOT use that authority.

Example:

```text
issued_at:
10:00

expires_at:
10:30

action:
10:31
```

Result:

```text
NON-CONFORMING
```

---

# 11. Revocation

An Authority Record MAY include:

```text
revoked_at
```

If an authority is revoked:

```text
action.timestamp < revoked_at
```

MAY remain conforming.

But:

```text
action.timestamp >= revoked_at
```

MUST NOT use that authority.

A revocation SHOULD itself be observable.

Example:

```text
Trace:
authority_revoked
```

---

# 12. Delegation

v0.2 introduces minimal bounded delegation.

Delegated authority MUST reference its parent through:

```text
delegation_parent
```

Example:

```text
Authority A
human → coordinator

Authority B
coordinator → worker-agent

Authority B.delegation_parent = Authority A
```

---

# 13. Delegation Invariants

## ZN-DELEG-001 — Parent Authority MUST Exist

Every delegated Authority Record MUST reference an existing parent authority.

---

## ZN-DELEG-002 — Parent Authority MUST Be Valid

A delegated authority MUST NOT be created from:

- denied authority,
- expired authority,
- revoked authority,
- unknown authority.

---

## ZN-DELEG-003 — Child Scope MUST NOT Exceed Parent Scope

Example:

```text
Parent:
read:document

Child:
write:document
```

Result:

```text
NON-CONFORMING
```

A child MAY narrow authority.

Example:

```text
Parent:
read:document
write:document

Child:
read:document
```

Result:

```text
CONFORMING
```

---

## ZN-DELEG-004 — Child Lifetime MUST NOT Exceed Parent Lifetime

If parent authority expires at:

```text
12:00
```

a child authority MUST NOT remain valid after `12:00`.

Example:

```text
Parent expires:
12:00

Child expires:
13:00
```

Result:

```text
NON-CONFORMING
```

---

## ZN-DELEG-005 — Revocation Propagates Downward

If a parent authority is revoked, delegated child authorities derived from that parent MUST become unusable unless an explicitly independent authority source exists.

Default v0.2 behavior:

```text
Parent revoked
    ↓
Children invalid
```

---

# 14. Authority Chains

Authority may form a chain:

```text
Human
   ↓
Coordinator Agent
   ↓
Worker Agent
   ↓
Tool Agent
```

Each delegation edge MUST remain independently verifiable.

Conceptually:

```text
A0 → A1 → A2 → A3
```

where every child authority references its parent.

The effective authority of the leaf participant is bounded by the intersection of valid authority along the chain.

Conceptually:

```text
Effective Scope
=
Scope(A0)
∩
Scope(A1)
∩
Scope(A2)
∩
Scope(A3)
```

A delegation chain MUST NOT increase privilege as it descends.

---

# 15. Authority and Trace

Authority changes SHOULD produce observable Trace events.

v0.2 extends recommended Trace types with:

```text
authority_granted
authority_revoked
authority_expired
authority_delegated
```

A Trace represents the observable transition.

The Authority Record represents the authoritative permission state.

This distinction remains:

```text
Trace
=
something happened

Authority Record
=
the permission state that resulted
```

---

# 16. Authority and Receipt

Every Receipt for an externally effective action MUST identify the authority actually used.

v0.2 SHOULD migrate:

```json
"authority_used": [
  "write:document"
]
```

toward explicit authority references.

Recommended v0.2 representation:

```json
"authority_refs": [
  "authority-uuid"
]
```

This allows a Receipt to prove not only:

> which scope was claimed,

but:

> which exact authority record authorized the action.

For backward compatibility, implementations MAY retain `authority_used` during v0.2.

---

# 17. Receipt Authority Validation

For every successful external action:

```text
Receipt
   ↓
authority_refs
   ↓
Authority Record
   ↓
issuer
subject
scope
validity
delegation chain
```

MUST be reconstructable.

An authoritative Receipt SHOULD therefore permit the validator to answer:

1. Who performed the action?
2. Which authority was used?
3. Who issued that authority?
4. Was the authority active?
5. Did the authority cover the action?
6. Was it delegated?
7. If delegated, was the chain valid?

---

# 18. Updated Successful Lifecycle

```text
Participant
    ↓
Trace: authority_request
    ↓
Authority Source
    ↓
Authority Record: ALLOW
    ↓
Trace: authority_granted
    ↓
Action Request
    ↓
Authority Validation
    ↓
External Action
    ↓
Trace: action_completed
    ↓
Receipt
```

---

# 19. Example — Direct Human Authority

```text
Human H1
   ↓ grants
Agent A
   ↓ performs
write_document
```

Authority:

```json
{
  "authority_id": "auth-001",
  "requester_id": "agent-a",
  "issuer_id": "human-h1",
  "subject_id": "agent-a",
  "scope": [
    "write:document"
  ],
  "decision": "allow",
  "source_type": "human",
  "issued_at": "2026-10-03T10:00:00+09:00",
  "expires_at": "2026-10-03T11:00:00+09:00",
  "revoked_at": null,
  "delegation_parent": null
}
```

Result:

```text
CONFORMING
```

if the action occurs within the validity period.

---

# 20. Example — Self-Escalation

Current authority:

```text
read:document
```

Agent attempts:

```text
requester_id = agent-a
issuer_id    = agent-a
new scope    = write:document
```

No independent policy authorizes this escalation.

Result:

```text
NON-CONFORMING
```

Violation:

```text
ZN-AUTH-002
```

---

# 21. Example — Expired Authority

```text
Authority expires:
10:30

Action occurs:
10:31
```

Result:

```text
NON-CONFORMING
```

Violation:

```text
ZN-AUTH-003
```

---

# 22. Example — Revoked Authority

```text
Authority issued:
10:00

Authority revoked:
10:15

Action occurs:
10:20
```

Result:

```text
NON-CONFORMING
```

Violation:

```text
ZN-AUTH-004
```

---

# 23. Example — Valid Delegation

```text
Human
  ↓
Coordinator
scope:
read:document
write:document

Coordinator
  ↓
Worker
scope:
read:document
```

The child scope is narrower than its parent.

Result:

```text
CONFORMING
```

---

# 24. Example — Privilege Expansion Through Delegation

```text
Parent:
read:document

Child:
read:document
write:document
```

Result:

```text
NON-CONFORMING
```

Violation:

```text
ZN-DELEG-003
```

---

# 25. Example — Delegation Beyond Parent Expiration

```text
Parent expires:
12:00

Child expires:
14:00
```

Result:

```text
NON-CONFORMING
```

Violation:

```text
ZN-DELEG-004
```

---

# 26. v0.2 Conformance Requirements

An implementation claiming AI Zero Network v0.2 conformance MUST satisfy v0.1 requirements and the following additional conditions.

### Requirement 1

Every allowed authority has an identifiable issuer.

### Requirement 2

Authority used by an action belongs to the acting subject or is validly delegated.

### Requirement 3

Authority is active at action time.

### Requirement 4

Expired or revoked authority cannot authorize new effects.

### Requirement 5

Authority scope covers the external action.

### Requirement 6

Participants cannot unilaterally expand their own authority.

### Requirement 7

Delegated authority cannot exceed its parent's scope or lifetime.

### Requirement 8

Receipts can be linked to the authority records that authorized their effects.

---

# 27. v0.2 Non-Goals

v0.2 does NOT define:

- advanced trust scoring,
- reputation systems,
- economic value,
- royalty allocation,
- contribution weighting,
- AI Meteorology,
- front detection,
- vortex detection,
- consensus governance,
- global identity federation,
- complete cryptographic key infrastructure,
- autonomous authority optimization,
- or unrestricted recursive delegation.

These remain higher-layer concerns.

---

# 28. Security Considerations

Implementations SHOULD assume that agents may:

- request excessive authority,
- replay old authority,
- use expired authority,
- attempt authority substitution,
- attempt self-escalation,
- reuse another participant's authority,
- create misleading delegation chains,
- or continue operating after revocation.

Therefore v0.2 implementations SHOULD validate authority at the moment of external action rather than relying only on previous authorization state.

Short-lived authority is RECOMMENDED for high-impact actions.

---

# 29. Compatibility With AI Meteorology

Authority provenance creates several future field-level signals.

Examples:

```text
authority request density
→ permission pressure

grant / deny ratio
→ authority friction

revocation rate
→ instability signal

delegation depth
→ authority topology

high-scope authority concentration
→ effective pressure concentration

expired-authority attempts
→ abnormal behavior signal
```

AI Meteorology remains outside v0.2.

v0.2 only makes these future observations possible.

---

# 30. Compatibility With Royalty and Contribution Layers

Authority provenance also improves later attribution.

A future contribution system MAY determine:

```text
who acted
under whose authority
using which resources
within which delegation chain
```

However:

> **Authority does not imply contribution.**

and:

> **Contribution does not imply ownership.**

Economic meaning remains outside v0.2.

---

# 31. Minimal v0.2 Architecture

```text
                    Authority Source
                          │
                          ▼
Participant ──request──→ Authority Record
     │                    │
     │                    ▼
     │              Authority Gate
     │                    │
     │              allow / deny
     │                    │
     └──── Trace ─────────┤
                          ▼
                    External Action
                          │
                          ▼
                       Receipt
                          │
                          ▼
                  authority_refs
```

For delegation:

```text
Root Authority
      │
      ▼
Delegated Authority
      │
      ▼
Delegated Authority
      │
      ▼
External Action
```

The privilege boundary MUST become equal or narrower as authority moves downward.

---

# 32. Minimum Authority Law

AI Zero Network v0.2 can be reduced to five authority rules:

> **No authority without an issuer.**  
> **No self-created privilege escalation.**  
> **No action under expired or revoked authority.**  
> **No delegation beyond the parent authority.**  
> **No effective action without reconstructable authority provenance.**

---

# 33. AI Zero Network v0.2 Definition

AI Zero Network v0.1 established:

> **Identity → Trace → Authority → Effect → Receipt**

AI Zero Network v0.2 refines that structure into:

> **Identity → Trace → Authority Provenance → Valid Authority → Effect → Receipt**

The essential change is simple:

> **v0.1 proves that authority existed.  
> v0.2 proves where that authority came from and whether it was still valid.**

This is the minimum authority-provenance layer of AI Zero Network.
