# AI Zero Network Conformance Index

**Status:** Draft  
**Scope:** AI Zero Network v0.1–v0.6  
**Purpose:** Common index for structural and semantic conformance requirements  
**Repository:** `ai-zero-network`

---

# 1. Purpose

This document provides a unified conformance index for AI Zero Network v0.1 through v0.6.

It does not replace the normative version specifications.

Instead, it provides a common map across:

```text
Specification
↓
JSON Schema
↓
Schema Examples
↓
Schema Validator
↓
Semantic Conformance Fixtures
↓
Conformance Validator
↓
GitHub Actions
```

The current conformance scope covers the:

> **AI Zero Network Observation & Structural Meteorology Core v0.1–v0.6**

---

# 2. Core Conformance Principle

AI Zero Network separates structural validity from semantic validity.

```text
Schema Validity
≠
Semantic Conformance
```

JSON Schema answers:

> Is this object structurally well-formed?

Conformance validation answers:

> Are the relationships represented by this object structurally and semantically consistent?

Both layers are required.

---

# 3. Conformance Is Not Trust

Passing AI Zero Network conformance does not prove that a system is:

- safe,
- benevolent,
- accurate,
- secure,
- reliable,
- legally compliant,
- or trustworthy.

Therefore:

> **Conformance ≠ Trust**

Instead:

> **Conformance = Minimum structural accountability**

A conformant implementation provides enough structure for important claims to be checked and reconstructed.

---

# 4. Conformance Layers

AI Zero Network currently uses four practical validation layers.

## Layer 1 — JSON Syntax

The artifact must be valid JSON.

---

## Layer 2 — JSON Schema

Checks structural properties such as:

```text
required fields
types
formats
UUIDs
date-time values
enums
minimum values
allowed properties
```

---

## Layer 3 — Semantic Conformance

Checks relationships that JSON Schema alone cannot reliably enforce.

Examples:

```text
authority existed before action

delta matches source snapshots

gradient matches source values

cycle returns to origin

candidate references real evidence
```

---

## Layer 4 — CI Enforcement

GitHub Actions runs validators so conformance regressions fail automatically.

---

# 5. Version Conformance Map

| Version | Conformance Domain | Main Semantic Question |
|---|---|---|
| v0.1 | Existence / Trace / Receipt | Did observable action leave structurally valid evidence? |
| v0.2 | Authority Provenance | Did authority exist, remain valid, and stay within its source? |
| v0.3 | Field Observation | Is the field measurement internally consistent? |
| v0.4 | Field Dynamics | Does reported change and flow match observable source state? |
| v0.5 | Boundary / Front Candidate | Is boundary evidence reconstructable and candidate classification supported? |
| v0.6 | Circulation / Vortex Candidate | Is circulation reconstructable and vortex classification supported by evidence? |

---

# 6. v0.1 — Existence Conformance

v0.1 establishes minimum structural accountability for actors, traces, authority-sensitive actions, and receipts.

Primary schemas:

```text
schemas/trace-v0.1.schema.json
schemas/receipt-v0.1.schema.json
```

Schema validator:

```text
scripts/validate.py
```

Semantic validator:

```text
scripts/validate_conformance.py
```

Conformance fixtures:

```text
examples/v0.1/conformance/pass/
examples/v0.1/conformance/fail/
```

---

# 7. v0.1 Conformance Rules

## ZN-CONF-001 — Known Participant

Every referenced actor MUST be a known participant in the evaluated fixture or system context.

---

## ZN-CONF-002 — Receipt References Existing Trace

A Receipt MUST reference an existing Trace.

---

## ZN-CONF-003 — Actor Consistency

The actor identified by a Receipt MUST be consistent with the actor associated with the referenced action or Trace.

---

## ZN-CONF-004 — Authority Before Action

An externally effective action requiring authority MUST NOT precede its valid authority decision.

Conceptually:

```text
Authority
↓
Action
```

not:

```text
Action
↓
Authority
```

---

## ZN-CONF-005 — Authority Scope Covers Action

The granted scope MUST cover the action being performed.

---

## ZN-CONF-006 — No Self-Escalation

An actor MUST NOT silently create additional privilege for itself.

Full provenance enforcement is strengthened in v0.2.

---

## ZN-CONF-007 — Denied Action Produces No Execution Receipt

A denied action MUST NOT produce a Receipt claiming successful external effect.

---

## ZN-CONF-008 — Failed Action Produces No Success Receipt

A failed action MUST NOT be represented as a successful externally effective action.

---

## ZN-CONF-009 — Successful External Action Requires Receipt

A successful externally effective action MUST have a corresponding Receipt.

---

## ZN-CONF-010 — No Duplicate Authoritative Receipt

The same successful action MUST NOT be represented by multiple conflicting authoritative Receipts.

---

## ZN-CONF-011 — Trace Causality Must Not Self-Reference

A Trace MUST NOT declare itself as its own causal parent.

Implementations SHOULD reject obvious causal cycles where appropriate.

---

## ZN-CONF-012 — Receipt Time Must Not Precede Action

A Receipt timestamp MUST NOT precede the action it proves.

---

# 8. v0.1 Compact Law

```text
No invisible actor.
No invisible action.
No authorityless action.
No receiptless effect.
```

---

# 9. v0.2 — Authority Provenance Conformance

v0.2 makes authority origin, validity, and delegation reconstructable.

Primary schema:

```text
schemas/authority-v0.2.schema.json
```

Schema validator:

```text
scripts/validate_v0_2.py
```

Semantic validator:

```text
scripts/validate_conformance_v0_2.py
```

Fixtures:

```text
examples/v0.2/conformance/pass/
examples/v0.2/conformance/fail/
```

---

# 10. v0.2 Authority Rules

## ZN-AUTH-001 — Authority Requires Provenance

An Authority Record MUST identify a source and issuer.

Authority MUST NOT appear without provenance.

---

## ZN-AUTH-002 — No Unilateral Self-Escalation

An actor MUST NOT unilaterally become the issuer of new privilege for itself.

Policy-based authority MAY be handled separately when explicitly governed.

---

## ZN-AUTH-003 — Authority Must Be Valid at Action Time

An action MUST occur after authority issuance and before expiration, if an expiration exists.

---

## ZN-AUTH-004 — Revoked Authority Cannot Be Used

An action MUST NOT rely on authority after its revocation time.

---

## ZN-AUTH-005 — Denied Authority Cannot Authorize

A denied Authority Record MUST NOT authorize an action.

---

## ZN-AUTH-006 — Scope Must Cover Action

The action MUST fall within the authority scope.

---

## ZN-AUTH-007 — Authority Must Belong to Subject

The actor performing the action MUST match the authorized subject.

---

# 11. v0.2 Delegation Rules

## ZN-DELEG-001 — Parent Authority Must Exist

A delegated authority MUST reference an existing parent authority.

---

## ZN-DELEG-002 — Parent Authority Must Be Valid

The parent authority MUST be valid when delegation occurs.

---

## ZN-DELEG-003 — Child Scope Must Not Exceed Parent

Conceptually:

```text
child_scope
⊆
parent_scope
```

---

## ZN-DELEG-004 — Child Lifetime Must Not Exceed Parent

A child authority MUST NOT remain valid beyond its parent authority.

---

## ZN-DELEG-005 — Revocation Propagates Downward

Revocation of a parent authority invalidates dependent delegated authority according to the defined chain.

---

# 12. Effective Delegated Scope

For a delegation chain:

```text
A0
↓
A1
↓
A2
```

effective authority is bounded by the intersection of valid scopes.

Conceptually:

```text
effective_scope
=
scope(A0)
∩
scope(A1)
∩
scope(A2)
```

---

# 13. v0.2 Compact Law

```text
No authority without an issuer.
No self-created privilege escalation.
No action under expired or revoked authority.
No delegation beyond the parent authority.
No effective action without reconstructable authority provenance.
```

---

# 14. v0.3 — Field Observation Conformance

v0.3 validates aggregate network-state measurement.

Primary schema:

```text
schemas/field-snapshot-v0.3.schema.json
```

Schema validator:

```text
scripts/validate_v0_3.py
```

Semantic validator:

```text
scripts/validate_conformance_v0_3.py
```

Fixtures:

```text
examples/v0.3/conformance/pass/
examples/v0.3/conformance/fail/
```

---

# 15. v0.3 Field Rules

## ZN-FIELD-001 — Valid Observation Window

A Field Snapshot MUST represent a bounded forward window.

```text
window_start
<
window_end
```

---

## ZN-FIELD-002 — Observable Evidence

Field observations MUST derive from observable records.

Private hidden reasoning MUST NOT be required.

---

## ZN-FIELD-003 — Derived Metrics Must Be Explicit

Derived values MUST remain separate from raw observations and identify their method.

---

## ZN-FIELD-004 — Counts Must Be Non-Negative

Observed counts MUST NOT be negative.

This is primarily enforced at Schema level.

---

## ZN-FIELD-005 — Authority Counts Must Be Consistent

At minimum:

```text
authority_grant_count
+
authority_deny_count
<=
authority_request_count
```

---

# 16. v0.3 Derived Metric Rules

For:

```text
authority_friction
```

when method is:

```text
deny_count/request_count
```

the reported value MUST match:

```text
authority_deny_count
/
authority_request_count
```

when request count is greater than zero.

If:

```text
authority_request_count = 0
```

the metric SHOULD be absent rather than represented as a normal zero ratio.

This preserves:

```text
no requests
≠
0% denial
```

---

# 17. v0.3 Provenance Rules

If `generated_at` exists:

```text
generated_at
>=
window_end
```

A Field Snapshot MUST NOT claim to have been generated from a completed window before that window ended.

`source_record_count` SHOULD remain consistent with the observable record volume without assuming double-counting semantics that have not been standardized.

---

# 18. v0.3 Compact Law

```text
No field value without a Region.
No snapshot without a time window.
No observation without observable evidence.
No interpretation disguised as observation.
```

---

# 19. v0.4 — Field Dynamics Conformance

v0.4 validates temporal change and directional Region Flow.

Primary schemas:

```text
schemas/field-delta-v0.4.schema.json
schemas/region-flow-v0.4.schema.json
```

Schema validator:

```text
scripts/validate_v0_4.py
```

Semantic validator:

```text
scripts/validate_conformance_v0_4.py
```

Fixtures:

```text
examples/v0.4/conformance/pass/
examples/v0.4/conformance/fail/
```

---

# 20. v0.4 Field Delta Rules

## ZN-DYN-001 — Two Existing Source Snapshots

Every Field Delta MUST reference:

```text
from_snapshot
to_snapshot
```

Both MUST exist.

---

## ZN-DYN-002 — Forward Temporal Order

The `to_snapshot` MUST represent a later state than `from_snapshot`.

---

## ZN-DYN-003 — Region Compatibility

An ordinary Field Delta MUST compare the same Region.

Cross-region differences belong to Boundary Gradient analysis.

---

## ZN-DYN-004 — Delta Must Be Reconstructable

For each compatible metric:

```text
delta
=
to_value
-
from_value
```

The reported Delta MUST match that calculation.

---

# 21. v0.4 Normalization Rules

If compared snapshot windows have unequal duration, direct raw-count interpretation may be misleading.

Therefore unequal time windows SHOULD require:

```text
window_compatibility = normalized
```

with an explicit:

```text
normalization_method
```

---

# 22. v0.4 Trend Rules

For directly compared derived values:

```text
to > from
→ rising

to < from
→ falling

to ≈ from
→ stable
```

If tolerance is used for `stable`, it SHOULD be documented.

Trend is interpretation.

Delta is measurement.

They MUST remain distinguishable.

---

# 23. v0.4 Region Flow Rules

## ZN-FLOW-001 — Source and Target Required

Every Region Flow MUST identify:

```text
source_region
target_region
```

---

## ZN-FLOW-002 — Direction Must Be Preserved

```text
A → B
```

and:

```text
B → A
```

are separate flows.

Ordinary cross-region flow MUST NOT use identical source and target Regions.

---

## ZN-FLOW-003 — Valid Observation Window

```text
window_start
<
window_end
```

---

# 24. v0.4 Flow Rate Rules

When method is:

```text
trace_count/per_minute
```

then:

```text
flow_rate
=
trace_count / duration_minutes
```

When method is:

```text
receipt_count/per_minute
```

then:

```text
effective_flow
=
receipt_count / duration_minutes
```

---

# 25. v0.4 Compact Law

```text
No Delta without two observations.
No trend without measurable change.
No flow without direction.
```

---

# 26. v0.5 — Boundary Gradient Conformance

v0.5 validates differences between Regions and evidence-backed Front Candidates.

Primary schemas:

```text
schemas/boundary-gradient-v0.5.schema.json
schemas/front-candidate-v0.5.schema.json
```

Schema validator:

```text
scripts/validate_v0_5.py
```

Semantic validator:

```text
scripts/validate_conformance_v0_5.py
```

Fixtures:

```text
examples/v0.5/conformance/pass/
examples/v0.5/conformance/fail/
```

---

# 27. v0.5 Gradient Rules

## ZN-GRAD-001 — Two Distinct Regions

```text
region_a
!=
region_b
```

---

## ZN-GRAD-002 — Metric Compatibility

Compared values MUST represent the same compatible metric semantics.

---

## ZN-GRAD-003 — Compatible Time Scope

Boundary comparisons MUST use compatible windows or explicitly declared temporal alignment or normalization.

---

## ZN-GRAD-004 — Gradient Must Be Reconstructable

For:

```text
method = absolute_difference
```

the required calculation is:

```text
gradient
=
abs(value_a - value_b)
```

For:

```text
method = directional_difference
```

the required calculation is:

```text
gradient
=
value_a - value_b
```

---

# 28. v0.5 Front Candidate Rules

## ZN-FRONT-001 — Gradient Evidence Required

Every Front Candidate MUST reference existing gradient evidence.

---

## ZN-FRONT-002 — Candidate Only

v0.5 permits:

```text
front_candidate
```

It does not permit:

```text
front_confirmed
```

as a normative classification.

---

## ZN-FRONT-003 — Classification Method Required

Every Front Candidate MUST expose its classifier method.

---

## ZN-FRONT-004 — Thresholds Must Be Explicit

Threshold-based methods MUST expose their threshold configuration.

---

# 29. v0.5 Boundary Consistency

Each referenced gradient SHOULD match the candidate's:

```text
boundary_id
region_a
region_b
window_start
window_end
```

unless the method explicitly defines an aggregation across windows.

The current v0.5 validator expects matching analysis windows for the conformance fixtures.

---

# 30. v0.5 Threshold Conformance

For:

```text
single_metric_threshold_v1
```

the referenced metric gradient MUST meet or exceed its declared threshold.

For:

```text
multi_metric_threshold_v1
```

each declared threshold MUST have corresponding referenced gradient evidence and satisfy the configured threshold.

For boundary-strength classification, conformance evaluates the magnitude of directional gradients where appropriate.

---

# 31. v0.5 Weighted Score Conformance

For:

```text
gradient_weighted_score_v1
```

weights MUST sum to:

```text
1.0
```

The score is reconstructed as:

```text
score
=
Σ(
  abs(metric_gradient)
  ×
  metric_weight
)
```

Every weighted metric MUST have referenced gradient evidence.

---

# 32. v0.5 Provenance

If present:

```text
source_gradient_refs
```

MUST correspond to the evidence referenced by the candidate.

And:

```text
generated_at
>=
window_end
```

---

# 33. v0.5 Compact Law

```text
No Gradient without two Regions.
No comparison without compatible metrics.
No Gradient without reconstructable evidence.
No Front Candidate without Gradient evidence.
No Candidate presented as certainty.
```

---

# 34. v0.6 — Circulation Conformance

v0.6 validates cyclic directional flow and evidence-backed Vortex Candidates.

Primary schemas:

```text
schemas/circulation-observation-v0.6.schema.json
schemas/vortex-candidate-v0.6.schema.json
```

Schema validator:

```text
scripts/validate_v0_6.py
```

Semantic validator:

```text
scripts/validate_conformance_v0_6.py
```

Fixtures:

```text
examples/v0.6/conformance/pass/
examples/v0.6/conformance/fail/
```

---

# 35. v0.6 Circulation Rules

## ZN-CIRC-001 — Bounded Observation Window

```text
window_start
<
window_end
```

---

## ZN-CIRC-002 — Multiple Distinct Regions

A qualifying circulation MUST involve at least two distinct Regions or nodes.

---

## ZN-CIRC-003 — Cycle Must Return to Origin

A cycle path MUST return to its starting point.

Example:

```text
A → B → C → A
```

Valid.

Example:

```text
A → B → C
```

Not a complete cycle.

---

## ZN-CIRC-004 — Direction Must Be Preserved

Ordered cycle paths are directional.

```text
A → B → C → A
```

and:

```text
A → C → B → A
```

are structurally different.

---

# 36. v0.6 Region Membership

Every node appearing in supplied cycle evidence MUST belong to the declared:

```text
region_refs
```

for that Circulation Observation.

---

# 37. v0.6 Cycle Count Reconstruction

When explicit `cycles[]` evidence is provided:

```text
cycle_count
=
Σ occurrence_count
```

for the normalized cycle records supplied in the fixture.

If no explicit cycle records are provided, the count MAY originate from the declared detection method.

---

# 38. v0.6 Return Rate

When:

```text
method = return_count/per_minute
```

then:

```text
return_rate
=
return_count / duration_minutes
```

---

# 39. v0.6 Vortex Candidate Rules

## ZN-VORTEX-001 — Circulation Evidence Required

Every Vortex Candidate MUST reference existing circulation evidence.

---

## ZN-VORTEX-002 — Candidate Only

v0.6 permits:

```text
vortex_candidate
```

It does NOT permit:

```text
vortex_confirmed
```

or:

```text
storm
```

as normative classifications.

---

## ZN-VORTEX-003 — Classification Method Required

Every Vortex Candidate MUST expose the classifier method.

---

## ZN-VORTEX-004 — Threshold Configuration Must Be Explicit

Threshold-based classification MUST expose its thresholds.

---

# 40. v0.6 Candidate Time Consistency

The candidate analysis interval MUST be compatible with referenced circulation evidence.

The current v0.6 conformance fixtures require matching windows.

---

# 41. v0.6 Core Region Consistency

If a candidate declares:

```text
core_regions
```

then:

```text
core_regions
⊆
union(referenced circulation.region_refs)
```

---

# 42. v0.6 Cycle Density Threshold

For:

```text
cycle_density_threshold_v1
```

the referenced circulation evidence MUST expose `cycle_density`.

The observed value MUST meet the configured threshold.

---

# 43. v0.6 Persistent Circulation Score

For:

```text
persistent_circulation_score_v1
```

v0.6 does not yet define one canonical score formula.

Therefore current conformance requires:

```text
score exists
score >= 0
```

but does not reconstruct a formula that the normative specification has not defined.

This prevents the validator from becoming more normative than the specification.

---

# 44. v0.6 Multi-Signal Score

For:

```text
multi_signal_vortex_candidate_v1
```

weights MUST sum to:

```text
1.0
```

Each weighted signal MUST exist.

The score is reconstructed as:

```text
score
=
Σ(
  signal_value
  ×
  signal_weight
)
```

Signals not used by the declared weight map MAY remain as supporting metadata.

---

# 45. v0.6 Provenance

If present:

```text
source_circulation_refs
```

MUST correspond to candidate evidence.

And:

```text
generated_at
>=
window_end
```

---

# 46. v0.6 Compact Law

```text
No circulation without directed return flow.
No candidate without cycle evidence.
No Vortex Candidate without circulation evidence.
No candidate presented as certainty.
No Vortex silently promoted to Storm.
```

---

# 47. Cross-Version Evidence Chain

AI Zero Network conformance is cumulative in structure.

One possible evidence chain is:

```text
Trace
↓
Authority
↓
Receipt
↓
Field Snapshot
↓
Field Delta
↓
Boundary Gradient
↓
Front Candidate
```

Another is:

```text
Trace / Receipt
↓
Region Flow
↓
Cycle
↓
Circulation Observation
↓
Vortex Candidate
```

Higher-order objects SHOULD remain reconstructable from lower-order evidence where the implementation exposes that evidence.

---

# 48. Observation vs Interpretation

Across v0.1–v0.6, implementations SHOULD preserve the distinction between:

```text
observable or directly calculated data
```

and:

```text
interpretive classification
```

Examples:

```text
trace_count
receipt_count
gradient
cycle_count
return_count
```

are measurements or direct calculations.

Examples:

```text
rising
front_candidate
vortex_candidate
```

are interpretations.

---

# 49. Candidate Principle

The following hierarchy is intentional:

```text
Boundary Gradient
↓
Front Candidate
```

not:

```text
Boundary Gradient
↓
Confirmed Front
```

and:

```text
Circulation
↓
Vortex Candidate
```

not:

```text
Circulation
↓
Storm
```

The conformance system SHOULD reject unsupported escalation of certainty.

---

# 50. Human Authority Boundary

Conformance results are observational and structural.

A successful classifier MUST NOT itself create authority to:

- stop an agent,
- revoke permissions,
- block transactions,
- isolate a Region,
- rewrite policy,
- terminate a service,
- or perform external intervention.

Any such action belongs to an independent authority layer.

---

# 51. Missing Data Principle

Across all field and meteorological layers:

```text
missing
≠
zero
```

and:

```text
unknown
≠
safe
```

and:

```text
partial
≠
complete
```

Implementations SHOULD preserve uncertainty rather than silently substituting values.

---

# 52. Provenance Principle

Where provenance fields are available, they SHOULD make higher-level results traceable to lower-level evidence.

Examples:

```text
Receipt
→ Trace
```

```text
Field Delta
→ Field Snapshots
```

```text
Front Candidate
→ Boundary Gradients
```

```text
Vortex Candidate
→ Circulation Observations
```

---

# 53. Duplicate Identifier Principle

Within one evaluated fixture or conformance scope, identifiers used as authoritative references SHOULD be unique.

Examples include:

```text
trace_id
receipt_id
authority_id
snapshot_id
delta_id
flow_id
gradient_id
candidate_id
circulation_id
cycle_id
```

Duplicate identifiers make evidence reconstruction ambiguous and SHOULD be rejected where validators support the check.

---

# 54. Time Principle

Across versions, causal and observational objects SHOULD preserve forward time.

Examples:

```text
authority issued
≤
action
≤
receipt
```

```text
window_start
<
window_end
≤
generated_at
```

and:

```text
from_snapshot
<
to_snapshot
```

where applicable.

---

# 55. Direction Principle

Where movement is modeled, direction MUST remain explicit.

Examples:

```text
A → B
≠
B → A
```

and:

```text
A → B → C → A
≠
A → C → B → A
```

Direction is part of the evidence.

---

# 56. Reconstruction Principle

Whenever a specification defines a deterministic calculation, conformance SHOULD reproduce it rather than trust the reported result.

Examples:

```text
Field Delta
Boundary Gradient
authority_friction
flow_rate
return_rate
weighted Front score
weighted Vortex score
```

---

# 57. Validator Index

| Version | Schema Validator | Semantic Validator |
|---|---|---|
| v0.1 | `scripts/validate.py` | `scripts/validate_conformance.py` |
| v0.2 | `scripts/validate_v0_2.py` | `scripts/validate_conformance_v0_2.py` |
| v0.3 | `scripts/validate_v0_3.py` | `scripts/validate_conformance_v0_3.py` |
| v0.4 | `scripts/validate_v0_4.py` | `scripts/validate_conformance_v0_4.py` |
| v0.5 | `scripts/validate_v0_5.py` | `scripts/validate_conformance_v0_5.py` |
| v0.6 | `scripts/validate_v0_6.py` | `scripts/validate_conformance_v0_6.py` |

---

# 58. Schema Index

```text
v0.1
schemas/trace-v0.1.schema.json
schemas/receipt-v0.1.schema.json

v0.2
schemas/authority-v0.2.schema.json

v0.3
schemas/field-snapshot-v0.3.schema.json

v0.4
schemas/field-delta-v0.4.schema.json
schemas/region-flow-v0.4.schema.json

v0.5
schemas/boundary-gradient-v0.5.schema.json
schemas/front-candidate-v0.5.schema.json

v0.6
schemas/circulation-observation-v0.6.schema.json
schemas/vortex-candidate-v0.6.schema.json
```

---

# 59. Fixture Index

Each version SHOULD maintain:

```text
examples/vX.Y/pass/
examples/vX.Y/fail/
examples/vX.Y/conformance/pass/
examples/vX.Y/conformance/fail/
```

The meaning is:

```text
pass/
→ expected to satisfy JSON Schema

fail/
→ expected to fail JSON Schema

conformance/pass/
→ expected to satisfy semantic rules

conformance/fail/
→ expected to violate at least one semantic rule
```

---

# 60. CI Expectations

The GitHub Actions workflow SHOULD run every current validator.

Conceptually:

```text
v0.1 Schema
↓
v0.1 Conformance
↓
v0.2 Schema
↓
v0.2 Conformance
↓
v0.3 Schema
↓
v0.3 Conformance
↓
v0.4 Schema
↓
v0.4 Conformance
↓
v0.5 Schema
↓
v0.5 Conformance
↓
v0.6 Schema
↓
v0.6 Conformance
```

Any unexpected PASS or FAIL SHOULD cause the workflow to fail.

---

# 61. Backward Compatibility

Later versions SHOULD NOT silently redefine earlier version semantics.

For example:

```text
v0.6
```

MUST NOT silently alter:

```text
v0.2 authority semantics
```

without explicit versioning.

Versioned schemas and specifications are treated as explicit contracts.

---

# 62. Extension Principle

Implementations MAY add higher-order metadata or implementation-specific analysis.

However, they SHOULD NOT claim AI Zero Network conformance for behavior that contradicts the normative rules of the declared version.

Extensions SHOULD preserve:

```text
evidence
version boundaries
provenance
candidate semantics
authority separation
```

---

# 63. Current Conformance Boundary

The current core validates:

```text
Existence
Authority
Observation
Dynamics
Boundary
Circulation
```

It does not yet define conformance for:

```text
Storm Candidate
Forecast
Trajectory Prediction
Forecast Confidence
Storm Lifecycle
Automated Intervention
```

These concepts remain outside v0.1–v0.6.

---

# 64. Observation Core vs Prediction Layer

The architectural boundary is:

```text
v0.1–v0.6
Observation
+
Reconstruction
+
Structural Meteorology
```

versus future work:

```text
Prediction
+
Forecasting
+
Higher-order Meteorology
```

This separation is intentional.

---

# 65. Unified Conformance Law

Across v0.1–v0.6:

> **No claim without structure.**  
> **No effect without evidence.**  
> **No authority without provenance.**  
> **No measurement without observable basis.**  
> **No derived value without a method.**  
> **No candidate without supporting evidence.**  
> **No candidate presented as certainty.**  
> **No observation silently becomes authority.**

---

# 66. Minimal Accountability Chain

The complete core can be viewed as:

```text
Actor
↓
Trace
↓
Authority
↓
Action
↓
Receipt
↓
Field
↓
Dynamics
↓
Boundary
↓
Circulation
↓
Candidate Interpretation
```

Each layer adds structure.

Each higher layer SHOULD remain accountable to the evidence beneath it.

---

# 67. Current Milestone

AI Zero Network v0.1–v0.6 currently forms the:

# Observation & Structural Meteorology Core

Its conformance system covers:

- JSON Schema validation,
- PASS/FAIL examples,
- semantic fixtures,
- reconstructable calculations,
- provenance checks,
- reference integrity,
- temporal checks,
- directional checks,
- candidate-evidence checks,
- and GitHub Actions enforcement.

This document serves as the common conformance index for that core.

---

# 68. Final Principle

AI Zero Network conformance does not ask:

> **Did the AI appear intelligent?**

It asks:

> **Can the structure around its actions and network behavior be reconstructed and checked?**

That is the purpose of conformance in AI Zero Network.
