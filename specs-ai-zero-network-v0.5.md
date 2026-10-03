# AI Zero Network v0.5

## Boundary Gradients and Front Candidates

**Status:** Draft
**Version:** v0.5
**Scope:** Cross-region gradients, boundary comparison, multi-metric contrast, and Front Candidate representation
**Repository:** `ai-zero-network`

---

## 1. Purpose

AI Zero Network v0.5 introduces a formal model for detecting significant differences between Regions.

v0.4 established:

```text
Field Snapshot
↓
Field Delta
↓
Region Flow
↓
Field Dynamics
```

v0.5 adds:

```text
Region A
+
Region B
↓
Boundary Gradient
↓
Front Candidate
```

The core question changes from:

> How is a Region changing?

to:

> How different are neighboring or interacting Regions?

This is the first formal boundary-analysis layer of AI Meteorology.

---

# 2. Position in the AI Zero Network Stack

```text
v0.1 — Existence
v0.2 — Authority
v0.3 — Field Observation
v0.4 — Field Dynamics
v0.5 — Boundary Gradients / Front Candidates
```

The progression is:

```text
Actors
↓
Authority
↓
Field
↓
Dynamics
↓
Boundary Structure
```

---

# 3. Core Principle

v0.5 follows one central rule:

> **A strong difference across a boundary is observable evidence, not proof of a Front.**

Therefore:

```text
Boundary Gradient
≠
Front
```

and:

```text
Front Candidate
≠
Confirmed Front
```

---

# 4. Design Goals

v0.5 has six primary goals.

1. Represent differences between two Regions.
2. Preserve metric-level provenance.
3. Distinguish raw gradient from interpretation.
4. Support multiple metrics across one boundary.
5. Produce explicit Front Candidates without claiming certainty.
6. Prepare inputs for later Front evolution and storm analysis.

---

# 5. Non-Goals

v0.5 does NOT define:

- confirmed Fronts,
- warm Fronts,
- cold Fronts,
- stationary Fronts,
- occluded Fronts,
- storm formation,
- vortex detection,
- typhoon classification,
- future-state forecasting,
- automatic intervention,
- authority revocation,
- or autonomous safety decisions.

These belong to later layers.

---

# 6. Core Concepts

v0.5 introduces four primary concepts.

```text
Boundary
Boundary Gradient
Gradient Set
Front Candidate
```

---

# 7. Boundary

A **Boundary** represents a logical comparison relationship between two Regions.

A boundary does not necessarily imply physical adjacency.

Regions MAY be compared when they are:

- topologically adjacent,
- operationally connected,
- causally linked,
- connected by Region Flow,
- or explicitly selected for comparison.

A Boundary MUST identify:

```text
region_a
region_b
```

---

# 8. Boundary Identity

A boundary SHOULD have a stable identifier.

Example:

```json
{
  "boundary_id": "finance-01__safety-01",
  "region_a": "finance-01",
  "region_b": "safety-01"
}
```

Boundary identity SHOULD remain stable when repeatedly measured across time.

---

# 9. Boundary Gradient

A **Boundary Gradient** represents the difference in one observable or derived metric between two Regions.

Conceptually:

```text
gradient
=
value_a - value_b
```

or, if direction is not relevant:

```text
absolute_gradient
=
|value_a - value_b|
```

The method MUST be explicit.

---

# 10. Minimum Boundary Gradient

A minimum Boundary Gradient MUST identify:

```text
gradient_id
boundary_id
region_a
region_b
metric
value_a
value_b
gradient
method
window_start
window_end
```

Example:

```json
{
  "schema_version": "0.5",
  "gradient_id": "11111111-1111-4111-8111-111111111111",
  "boundary_id": "finance-01__safety-01",
  "region_a": "finance-01",
  "region_b": "safety-01",
  "metric": "activity_pressure",
  "value_a": 0.85,
  "value_b": 0.35,
  "gradient": 0.50,
  "method": "absolute_difference",
  "window_start": "2026-10-04T03:00:00+09:00",
  "window_end": "2026-10-04T03:05:00+09:00"
}
```

---

# 11. Directional Gradient

A directional method MAY preserve sign.

Example:

```text
value_a = 0.85
value_b = 0.35

gradient = +0.50
```

This means the metric is higher in Region A.

If:

```text
value_a = 0.35
value_b = 0.85
```

then:

```text
gradient = -0.50
```

Implementations MUST document whether the metric is:

```text
directional
```

or:

```text
absolute
```

---

# 12. ZN-GRAD-001 — Two Distinct Regions Required

A Boundary Gradient MUST compare two distinct Regions.

The following is invalid:

```text
finance-01
vs
finance-01
```

---

# 13. ZN-GRAD-002 — Metric Compatibility

The values being compared MUST represent compatible metric semantics.

Example:

```text
activity_pressure
vs
activity_pressure
```

is valid.

The following is not a direct gradient:

```text
activity_pressure
vs
authority_friction
```

---

# 14. ZN-GRAD-003 — Compatible Time Scope

The compared values MUST refer to compatible temporal windows.

Preferred:

```text
Region A
10:00–10:05

Region B
10:00–10:05
```

If time windows differ, normalization or explicit temporal alignment MUST be documented.

---

# 15. ZN-GRAD-004 — Gradient MUST Be Reconstructable

Given:

```text
value_a
value_b
method
```

the reported gradient MUST be reproducible.

For:

```text
method = absolute_difference
```

the rule is:

```text
gradient = abs(value_a - value_b)
```

For:

```text
method = directional_difference
```

the rule is:

```text
gradient = value_a - value_b
```

---

# 16. Gradient Set

A single metric may not be sufficient to characterize a meaningful boundary.

Therefore v0.5 introduces a **Gradient Set**.

Example:

```text
finance-01
vs
safety-01

activity_pressure      = 0.50
authority_friction     = 0.67
effective_pressure     = 0.41
cross_region_flow      = 0.33
```

A Gradient Set combines several individually reconstructable gradients.

---

# 17. Gradient Set Structure

A Gradient Set SHOULD identify:

```text
gradient_set_id
boundary_id
region_a
region_b
window_start
window_end
gradients[]
```

Example:

```json
{
  "gradient_set_id": "gs-001",
  "boundary_id": "finance-01__safety-01",
  "region_a": "finance-01",
  "region_b": "safety-01",
  "window_start": "2026-10-04T03:00:00+09:00",
  "window_end": "2026-10-04T03:05:00+09:00",
  "gradients": [
    {
      "metric": "activity_pressure",
      "value_a": 0.85,
      "value_b": 0.35,
      "gradient": 0.50,
      "method": "absolute_difference"
    },
    {
      "metric": "authority_friction",
      "value_a": 0.12,
      "value_b": 0.79,
      "gradient": 0.67,
      "method": "absolute_difference"
    }
  ]
}
```

---

# 18. Raw Gradient vs Interpretation

The following is an observation or direct calculation:

```text
activity_pressure_gradient = 0.50
```

The following is an interpretation:

```text
strong_boundary
```

and the following is a higher-order interpretation:

```text
front_candidate
```

These layers MUST remain distinguishable.

---

# 19. Front Candidate

A **Front Candidate** is an interpreted boundary state indicating that the difference between Regions deserves meteorological attention.

It is NOT a confirmed Front.

Minimum conceptual structure:

```text
candidate_id
boundary_id
gradient_refs
classification
method
```

Example:

```json
{
  "candidate_id": "fc-001",
  "boundary_id": "finance-01__safety-01",
  "gradient_refs": [
    "gradient-activity-001",
    "gradient-authority-001"
  ],
  "classification": "front_candidate",
  "method": "multi_metric_threshold_v1"
}
```

---

# 20. ZN-FRONT-001 — Candidate Requires Boundary Evidence

A Front Candidate MUST reference one or more Boundary Gradients or Gradient Sets.

It MUST NOT appear without underlying evidence.

---

# 21. ZN-FRONT-002 — Candidate MUST NOT Become Confirmation

v0.5 recognizes:

```text
front_candidate
```

It does NOT recognize:

```text
front_confirmed
```

as a normative state.

A higher specification is required before confirmation semantics are introduced.

---

# 22. ZN-FRONT-003 — Classification Method Required

Every Front Candidate MUST identify the method used to produce the classification.

Examples:

```text
single_metric_threshold_v1
multi_metric_threshold_v1
gradient_weighted_score_v1
```

---

# 23. ZN-FRONT-004 — Thresholds MUST Be Explicit

If a Front Candidate is produced using thresholds, those thresholds MUST be reconstructable.

Example:

```json
{
  "thresholds": {
    "activity_pressure": 0.40,
    "authority_friction": 0.50
  }
}
```

Hidden threshold logic SHOULD NOT be used for normative conformance.

---

# 24. Confidence

A Front Candidate MAY contain a `confidence` value.

Example:

```json
{
  "confidence": 0.72
}
```

However:

> Confidence does not automatically mean probability.

Unless calibrated probabilistic semantics exist, confidence SHOULD be treated as an implementation-defined classification score.

---

# 25. Candidate Strength

Implementations MAY describe candidate strength using neutral structural terms such as:

```text
weak
moderate
strong
```

only when explicit thresholds define those categories.

Example:

```text
0.00–0.29 → weak
0.30–0.59 → moderate
0.60–1.00 → strong
```

The thresholds MUST be documented.

---

# 26. Front Candidate Is Not Danger

This distinction is critical.

```text
front_candidate
```

does NOT imply:

```text
unsafe
malicious
unstable
dangerous
```

A Front Candidate only means:

> A significant structural difference exists or may exist across a boundary.

---

# 27. Why This Matters

A boundary may arise because:

- two teams perform different roles,
- one Region is highly active while another is quiet,
- one Region requires strict authority while another is open,
- one Region is compute-heavy,
- one Region is human-controlled,
- one Region is undergoing a temporary workload spike.

None of these conditions is automatically harmful.

---

# 28. Cross-Region Flow and Boundary Gradient

Region Flow from v0.4 MAY contribute to boundary analysis.

Example:

```text
finance-01
   ↓↓↓↓↓
payment-01
```

If flow rises sharply while a strong gradient exists, that combination MAY strengthen a Front Candidate.

However:

```text
high flow
≠
front
```

and:

```text
high gradient
≠
front
```

The classifier method determines how evidence is combined.

---

# 29. Temporal Persistence

A meaningful Front Candidate may require persistence.

For example:

```text
t0 gradient = 0.62
t1 gradient = 0.66
t2 gradient = 0.69
```

may be structurally different from:

```text
t0 gradient = 0.10
t1 gradient = 0.71
t2 gradient = 0.12
```

The second may be a temporary spike.

v0.5 MAY record persistence information but does not standardize Front lifecycle semantics.

---

# 30. Candidate Observation Window

A Front Candidate SHOULD identify the time window or analysis interval from which it was derived.

Example:

```text
window_start
window_end
```

This prevents a stale boundary classification from being treated as current.

---

# 31. Provenance

Boundary and Front Candidate records SHOULD preserve provenance.

Recommended fields:

```text
generated_at
analyzer_id
source_snapshot_refs
source_gradient_refs
source_digest
```

---

# 32. ZN-FRONT-PROV-001 — Evidence Traceability

A Front Candidate SHOULD be traceable back to:

```text
Front Candidate
↓
Gradient Set
↓
Boundary Gradients
↓
Field Snapshots
↓
Trace / Receipt / Authority observations
```

This produces a reconstructable meteorological evidence chain.

---

# 33. The Meteorological Evidence Chain

Conceptually:

```text
Trace / Receipt
      ↓
Field Snapshot
      ↓
Field Delta
      ↓
Boundary Gradient
      ↓
Gradient Set
      ↓
Front Candidate
```

No layer should erase the evidence beneath it.

---

# 34. Missing Data

Missing metrics MUST NOT silently become zero.

Example:

```text
authority_friction = unavailable
```

is not equivalent to:

```text
authority_friction = 0
```

If one Region lacks data for a metric, that metric SHOULD be excluded or marked unavailable.

---

# 35. Partial Gradient Sets

A Gradient Set MAY be marked:

```text
complete
partial
provisional
```

A Front Candidate derived from partial evidence SHOULD preserve that state.

---

# 36. Example — Single Strong Gradient

```text
Region A activity_pressure = 0.91
Region B activity_pressure = 0.30

gradient = 0.61
```

This is a strong observable difference.

It MAY trigger:

```text
front_candidate
```

under a declared classifier.

It does not confirm a Front.

---

# 37. Example — Multi-Metric Boundary

```text
activity_pressure gradient  = 0.52
authority_friction gradient = 0.64
effective_pressure gradient = 0.49
```

A classifier MAY combine them.

Example:

```text
score
=
0.4 × activity
+
0.4 × authority
+
0.2 × effective
```

If such weighting is used, the method and weights MUST be documented.

---

# 38. Example — False Boundary Signal

Suppose:

```text
activity gradient = 0.80
```

but all other metrics are nearly equal.

This may represent a temporary workload difference rather than a broader structural Front.

Therefore v0.5 SHOULD encourage multi-metric analysis where practical.

---

# 39. Example — Temporal Persistence

```text
t0 = 0.55
t1 = 0.58
t2 = 0.63
t3 = 0.67
```

This may indicate a persistent boundary strengthening.

v0.5 MAY expose:

```text
persistence_count
```

or:

```text
persistence_duration
```

but does not yet define Front lifecycle states.

---

# 40. Candidate Lifecycle

v0.5 MAY observe:

```text
appeared
persisted
weakened
disappeared
```

only as descriptive candidate-state transitions.

It MUST NOT yet define meteorological Front lifecycle classes.

---

# 41. Boundary Analysis Architecture

```text
Field Snapshot A ───────┐
                        │
                        ▼
                 Boundary Analyzer
                        ▲
                        │
Field Snapshot B ───────┘
                        │
                        ▼
                 Boundary Gradient
                        │
                        ▼
                    Gradient Set
                        │
                        ▼
                 Candidate Classifier
                        │
                        ▼
                  Front Candidate
```

---

# 42. Cross-Layer Architecture

```text
v0.3
Field Snapshot
      ↓
v0.4
Field Dynamics
      ↓
v0.5
Boundary Gradient
      ↓
Front Candidate
```

---

# 43. Minimum v0.5 Conformance Requirements

An implementation claiming v0.5 conformance MUST ensure:

### Requirement 1

Every gradient compares two distinct Regions.

### Requirement 2

Compared metrics have compatible semantics.

### Requirement 3

Compared temporal scopes are compatible or explicitly normalized.

### Requirement 4

Reported gradients are reconstructable from source values.

### Requirement 5

Front Candidates reference underlying gradient evidence.

### Requirement 6

Front Candidates identify their classifier method.

### Requirement 7

Threshold-based classification exposes thresholds.

### Requirement 8

A Front Candidate is not represented as a confirmed Front.

---

# 44. Recommended v0.5 Schemas

The minimum machine-readable layer SHOULD introduce:

```text
schemas/boundary-gradient-v0.5.schema.json
schemas/front-candidate-v0.5.schema.json
```

A future extension MAY introduce:

```text
schemas/gradient-set-v0.5.schema.json
```

if Gradient Set complexity grows.

For the first implementation, Gradient Sets MAY be embedded in the Front Candidate object.

---

# 45. Recommended Validation Layers

v0.5 SHOULD retain the existing validation pattern.

```text
JSON Schema
↓
Schema examples
↓
Semantic conformance fixtures
↓
Conformance Validator
↓
GitHub Actions
```

---

# 46. Schema-Level Validation

JSON Schema SHOULD validate:

```text
required fields
UUID formats
metric names
numeric values
classification enums
threshold structure
provenance structure
```

---

# 47. Conformance-Level Validation

Semantic validation SHOULD check:

```text
region_a != region_b

source snapshots exist

time windows are compatible

gradient value matches calculation

gradient references exist

Front Candidate references valid gradient evidence

threshold conditions actually produce candidate

confidence stays within declared range

candidate does not claim confirmed status
```

---

# 48. Failure Examples

## FAIL-GRAD-001 — Same Region

```text
region_a = finance-01
region_b = finance-01
```

---

## FAIL-GRAD-002 — Incorrect Gradient

```text
value_a = 0.80
value_b = 0.30

reported gradient = 0.20
```

For `absolute_difference`, expected:

```text
0.50
```

---

## FAIL-GRAD-003 — Incompatible Metric

Different semantic metrics are treated as one direct gradient.

---

## FAIL-GRAD-004 — Incompatible Time Windows

Two snapshots from unrelated windows are directly compared without alignment or normalization.

---

## FAIL-FRONT-001 — No Gradient Evidence

A Front Candidate exists but references no boundary evidence.

---

## FAIL-FRONT-002 — Missing Classification Method

```text
classification = front_candidate
```

without a method.

---

## FAIL-FRONT-003 — Hidden Threshold

A threshold classifier produces a candidate without exposing its threshold configuration.

---

## FAIL-FRONT-004 — Premature Confirmation

```text
classification = front_confirmed
```

is invalid under v0.5.

---

# 49. Human Review Boundary

A Front Candidate is observational guidance.

It MUST NOT itself grant authority to:

- terminate agents,
- revoke permissions,
- block transactions,
- isolate Regions,
- alter policies,
- or perform external actions.

Any intervention requires an independent authority layer.

---

# 50. Data Minimization

Boundary analysis SHOULD use aggregate field measurements where possible.

It SHOULD NOT require:

- private chain-of-thought,
- full conversation bodies,
- hidden reasoning,
- unrelated personal information,
- or unnecessary raw content.

---

# 51. Minimum Boundary Law

v0.5 can be summarized as:

> **No Gradient without two Regions.**
> **No comparison without compatible metrics.**
> **No Gradient without reconstructable evidence.**
> **No Front Candidate without Gradient evidence.**
> **No Candidate presented as certainty.**

---

# 52. AI Meteorology Progression

The emerging structure is:

```text
v0.3
Measure the atmosphere.

v0.4
Measure its movement.

v0.5
Measure its boundaries.
```

Future layers may then ask:

```text
Does the boundary persist?

Does circulation form around it?

Does activity accelerate?

Does a storm-like structure emerge?
```

---

# 53. AI Zero Network v0.5 Definition

AI Zero Network v0.5 defines the minimum structure required to measure cross-region differences and represent those differences as provisional Front Candidates.

In compact form:

> **Fields create differences.**
> **Differences create gradients.**
> **Persistent gradients begin to reveal fronts.**

But:

> **A candidate is still only a candidate.**

That restraint is a core part of AI Zero Network v0.5.
