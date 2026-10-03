# AI Zero Network v0.6

## Circulation and Vortex Candidates

**Status:** Draft  
**Version:** v0.6  
**Scope:** Cyclic flow, circulation structure, return paths, persistence, and provisional Vortex Candidate representation  
**Repository:** `ai-zero-network`

---

## 1. Purpose

AI Zero Network v0.6 extends boundary-aware Field Dynamics into circulation analysis.

v0.5 established:

```text
Region A
+
Region B
↓
Boundary Gradient
↓
Front Candidate
```

v0.6 asks:

> **When does directional flow begin to form a persistent return structure?**

The progression becomes:

```text
Flow
↓
Cycle
↓
Circulation
↓
Vortex Candidate
```

v0.6 formalizes the minimum structure required to observe cyclic network behavior without prematurely labeling it as a Storm.

Its central rule is:

> **Circulation is observable structure. A Vortex Candidate is interpretation. A Storm is a higher-order conclusion.**

---

# 2. Position in the AI Zero Network Stack

```text
v0.1 — Existence
v0.2 — Authority
v0.3 — Field Observation
v0.4 — Field Dynamics
v0.5 — Boundary Gradients / Front Candidates
v0.6 — Circulation / Vortex Candidates
```

The structural progression is:

```text
Actors
↓
Authority
↓
Field
↓
Dynamics
↓
Boundary
↓
Circulation
```

v0.6 completes the first Observation and Structural Meteorology Core.

---

# 3. Core Principle

v0.6 follows three distinctions:

```text
Cycle
≠
Circulation
```

```text
Circulation
≠
Vortex
```

```text
Vortex Candidate
≠
Storm
```

A single repeated path is not enough to prove a stable vortex-like structure.

---

# 4. Design Goals

v0.6 has seven primary goals.

1. Represent observable cyclic flow.
2. Distinguish isolated cycles from persistent circulation.
3. Measure return-flow strength.
4. Preserve directionality and Region membership.
5. Represent circulation as evidence rather than danger.
6. Produce provisional Vortex Candidates from reconstructable circulation evidence.
7. Stop before predictive Storm classification.

---

# 5. Non-Goals

v0.6 does NOT define:

- confirmed vortices,
- storms,
- typhoons,
- hurricanes,
- storm intensity,
- storm tracks,
- future trajectory prediction,
- forecast confidence,
- autonomous containment,
- authority revocation,
- automatic isolation,
- or intervention policies.

These belong to future layers.

---

# 6. Core Concepts

v0.6 introduces five primary concepts.

```text
Cycle
Return Flow
Circulation Observation
Circulation Candidate
Vortex Candidate
```

---

# 7. Cycle

A **Cycle** is a directed path that returns to its origin.

Example:

```text
Region A
↓
Region B
↓
Region C
↓
Region A
```

Formally:

```text
A → B → C → A
```

A cycle MUST contain at least two distinct nodes or Regions before returning to its origin.

---

# 8. Cycle Is Not Automatically Circulation

A single cycle may represent:

- retry logic,
- human review,
- iterative refinement,
- error recovery,
- approval loops,
- synchronization,
- or normal multi-agent cooperation.

Therefore:

```text
cycle_count > 0
```

does NOT automatically imply:

```text
circulation_candidate
```

Persistence or repeated return behavior SHOULD be considered.

---

# 9. Return Flow

A **Return Flow** represents directional flow that returns toward a previously visited Region or node.

Example:

```text
A → B → A
```

or:

```text
A → B → C → A
```

A Return Flow MAY be measured using:

```text
return_count
return_rate
returned_trace_count
returned_receipt_count
```

---

# 10. Circulation Observation

A **Circulation Observation** represents measurable cyclic behavior during a bounded window.

A minimum Circulation Observation SHOULD identify:

```text
circulation_id
window_start
window_end
region_refs
cycle_count
return_count
```

Example:

```json
{
  "schema_version": "0.6",
  "circulation_id": "11111111-1111-4111-8111-111111111111",
  "window_start": "2026-10-04T06:00:00+09:00",
  "window_end": "2026-10-04T06:05:00+09:00",
  "region_refs": [
    "planner-01",
    "executor-01",
    "reviewer-01"
  ],
  "cycle_count": 7,
  "return_count": 11
}
```

---

# 11. ZN-CIRC-001 — Bounded Observation Window

Every Circulation Observation MUST identify:

```text
window_start
window_end
```

and:

```text
window_end > window_start
```

---

# 12. ZN-CIRC-002 — Multiple Regions or Nodes

A Circulation Observation MUST involve at least two distinct Regions or nodes.

The following is not sufficient:

```text
A → A
```

unless a future specification explicitly defines internal self-loop semantics.

---

# 13. ZN-CIRC-003 — Cycle Evidence Required

A Circulation Observation MUST derive from observable directional relationships.

Possible evidence includes:

- Region Flow,
- Trace causal edges,
- explicit message transitions,
- Receipt-linked actions,
- authority handoffs,
- tool-call transitions,
- or equivalent auditable edges.

Private chain-of-thought MUST NOT be required.

---

# 14. ZN-CIRC-004 — Direction MUST Be Preserved

Circulation is directional.

Therefore:

```text
A → B → C → A
```

is not identical to:

```text
A → C → B → A
```

Implementations MUST preserve edge direction when reconstructing cycles.

---

# 15. Cycle Count

`cycle_count` represents the number of qualifying cycles observed during the analysis window.

The cycle-detection method MUST be declared when needed for reproducibility.

Possible methods include:

```text
directed_cycle_count_v1
simple_cycle_count_v1
bounded_return_cycle_v1
```

---

# 16. Cycle Identity

A cycle MAY be represented by an ordered Region path.

Example:

```json
{
  "path": [
    "planner-01",
    "executor-01",
    "reviewer-01",
    "planner-01"
  ]
}
```

Implementations MAY normalize cycle identity to prevent repeated rotations from being counted as different structures.

For example:

```text
A → B → C → A
```

and:

```text
B → C → A → B
```

may represent the same logical cycle.

v0.6 does not require a single canonicalization algorithm, but implementations SHOULD document their method.

---

# 17. Return Count

`return_count` measures qualifying return movements toward previously visited Regions.

It is not necessarily identical to `cycle_count`.

Example:

```text
one cycle
may contain
multiple return-related events
```

Therefore:

```text
cycle_count
≠
return_count
```

---

# 18. Circulation Strength

v0.6 MAY derive a neutral **circulation strength**.

Possible inputs include:

```text
cycle_count
return_count
cycle_density
return_rate
persistence
flow magnitude
```

Example:

```json
{
  "circulation_strength": {
    "value": 0.62,
    "method": "normalized_cycle_return_score_v1"
  }
}
```

The method MUST be explicit.

---

# 19. Cycle Density

An implementation MAY define:

```text
cycle_density
```

as a normalized measure of how much of the observed graph participates in cyclic structure.

The exact formula is implementation-defined in v0.6.

If present, its method MUST be declared.

---

# 20. Persistence

A circulation structure becomes more meaningful when it persists.

Example:

```text
t0 cycle_count = 6
t1 cycle_count = 8
t2 cycle_count = 7
t3 cycle_count = 9
```

may indicate persistent circulation.

By contrast:

```text
t0 = 0
t1 = 12
t2 = 0
t3 = 0
```

may be a short-lived spike.

---

# 21. Persistence Observation

v0.6 MAY represent:

```text
persistence_count
persistence_duration
```

Example:

```json
{
  "persistence": {
    "count": 4,
    "duration_seconds": 1200
  }
}
```

---

# 22. Circulation Candidate

A **Circulation Candidate** is an interpreted state indicating that observed cyclic behavior appears persistent enough to warrant higher-order analysis.

It is still not a Vortex.

Conceptually:

```text
cycles
+
return flow
+
persistence
↓
circulation_candidate
```

---

# 23. ZN-CIRC-CAND-001 — Candidate Requires Cycle Evidence

A Circulation Candidate MUST reference underlying circulation or cycle evidence.

It MUST NOT appear from an unsupported classifier output.

---

# 24. ZN-CIRC-CAND-002 — Candidate Method Required

A Circulation Candidate MUST identify its classification method.

Examples:

```text
cycle_threshold_v1
cycle_return_threshold_v1
persistent_circulation_score_v1
```

---

# 25. Vortex Candidate

A **Vortex Candidate** is a higher-order interpretation indicating that cyclic directional flow appears sufficiently concentrated, persistent, and self-reinforcing to resemble a vortex-like structure.

A minimum conceptual Vortex Candidate SHOULD identify:

```text
candidate_id
circulation_refs
classification
method
window_start
window_end
```

Example:

```json
{
  "schema_version": "0.6",
  "candidate_id": "22222222-2222-4222-8222-222222222222",
  "circulation_refs": [
    "11111111-1111-4111-8111-111111111111"
  ],
  "classification": "vortex_candidate",
  "method": "persistent_circulation_score_v1",
  "window_start": "2026-10-04T06:00:00+09:00",
  "window_end": "2026-10-04T06:05:00+09:00"
}
```

---

# 26. ZN-VORTEX-001 — Evidence Required

A Vortex Candidate MUST reference one or more valid Circulation Observations or Circulation Candidates.

No evidence means no candidate.

---

# 27. ZN-VORTEX-002 — Candidate Only

v0.6 recognizes:

```text
vortex_candidate
```

It does NOT normatively recognize:

```text
vortex_confirmed
```

A future specification is required for confirmation semantics.

---

# 28. ZN-VORTEX-003 — Method Required

Every Vortex Candidate MUST expose the method used to derive the classification.

Examples:

```text
persistent_circulation_score_v1
cycle_density_threshold_v1
multi_signal_vortex_candidate_v1
```

---

# 29. ZN-VORTEX-004 — Thresholds Must Be Reconstructable

If a Vortex Candidate is threshold-based, the threshold configuration MUST be explicit.

Example:

```json
{
  "thresholds": {
    "cycle_count": 5,
    "return_count": 8,
    "circulation_strength": 0.6
  }
}
```

---

# 30. Confidence

A Vortex Candidate MAY contain:

```text
confidence
```

with a bounded value such as:

```text
0.0 ≤ confidence ≤ 1.0
```

Unless calibrated probability semantics are separately defined:

> confidence is a classifier score, not an objective probability.

---

# 31. Vortex Strength

Implementations MAY describe structural strength as:

```text
weak
moderate
strong
```

only when explicit thresholds define those categories.

A strength label MUST NOT be inferred from undocumented intuition.

---

# 32. Vortex Candidate Is Not Danger

The following does not follow automatically:

```text
vortex_candidate
→ dangerous
```

A vortex-like structure may be:

- a stable review loop,
- repeated market negotiation,
- distributed consensus,
- task refinement,
- recovery coordination,
- iterative planning,
- or self-reinforcing failure.

Its meaning depends on context.

---

# 33. Vortex Candidate Is Not Storm

This is one of the strongest v0.6 constraints.

```text
vortex_candidate
≠
storm
```

A Storm would require additional dimensions such as:

```text
growth
energy
boundary interaction
acceleration
persistence
spread
impact
```

v0.6 intentionally stops before that layer.

---

# 34. Flow Concentration

A vortex-like structure often requires more than repeated cycles.

Implementations MAY measure whether flow is concentrated around a relatively stable set of Regions.

Possible indicators:

```text
core_region_count
cycle_overlap
return concentration
edge reuse
```

v0.6 does not standardize these formulas.

---

# 35. Core Region Set

A Vortex Candidate MAY identify:

```text
core_regions
```

Example:

```json
{
  "core_regions": [
    "planner-01",
    "executor-01",
    "reviewer-01"
  ]
}
```

These Regions indicate the principal circulation core.

---

# 36. Region Membership Stability

If the Region set changes completely from one window to the next, the structure may not represent persistent circulation.

Example:

```text
t0:
A → B → C → A

t1:
X → Y → Z → X
```

These should not automatically be treated as the same vortex-like structure.

---

# 37. Circulation Evolution

v0.6 MAY describe circulation-state transitions such as:

```text
appeared
persisted
strengthened
weakened
dissipated
```

These are descriptive states only.

They do not imply forecasting.

---

# 38. Candidate Persistence

A Vortex Candidate MAY include:

```text
persistence_count
persistence_duration
```

to distinguish persistent circulation from transient cycles.

---

# 39. Relation to Front Candidates

A Front Candidate and Vortex Candidate are independent structures.

Possible network state:

```text
Front Candidate
+
Vortex Candidate
```

may be noteworthy for future meteorological layers.

However v0.6 MUST NOT infer:

```text
Front + Vortex
= Storm
```

That relationship belongs to later work.

---

# 40. Relation to Region Flow

Region Flow from v0.4 provides directed edges.

Conceptually:

```text
Region Flow
↓
Directed Graph
↓
Cycle Detection
↓
Circulation Observation
```

Thus v0.6 builds directly on v0.4.

---

# 41. Relation to Boundary Gradient

Boundary Gradient from v0.5 may provide context around the circulation core.

Example:

```text
strong circulation
inside Region cluster

+
strong boundary gradient
around cluster
```

may later become an important storm-like signal.

v0.6 records the components but does not combine them into Storm semantics.

---

# 42. Circulation Architecture

```text
Region Flows
     │
     ▼
Directed Flow Graph
     │
     ▼
Cycle Detector
     │
     ├── cycle_count
     ├── return_count
     ├── cycle_density
     └── persistence
     │
     ▼
Circulation Observation
     │
     ▼
Circulation Classifier
     │
     ▼
Circulation Candidate
```

---

# 43. Vortex Architecture

```text
Circulation Observation(s)
        │
        ▼
Persistence / Concentration Analysis
        │
        ▼
Vortex Candidate Classifier
        │
        ▼
Vortex Candidate
```

---

# 44. Evidence Chain

A Vortex Candidate SHOULD remain traceable through the lower layers.

Conceptually:

```text
Trace / Receipt
      ↓
Field Snapshot
      ↓
Region Flow
      ↓
Cycle
      ↓
Circulation Observation
      ↓
Vortex Candidate
```

No higher layer should erase the evidence chain beneath it.

---

# 45. Observation vs Interpretation

Observable or directly calculated:

```text
cycle_count = 7
return_count = 11
cycle_density = 0.31
```

Derived interpretation:

```text
circulation_candidate
```

Higher interpretation:

```text
vortex_candidate
```

Unsupported future conclusion:

```text
storm
```

These layers MUST remain distinguishable.

---

# 46. Missing Data

Missing evidence MUST NOT silently become zero.

Example:

```text
cycle_density = unavailable
```

is different from:

```text
cycle_density = 0
```

Partial evidence SHOULD preserve:

```text
partial
```

or:

```text
provisional
```

state.

---

# 47. Observation State

Circulation records MAY use:

```text
complete
partial
provisional
```

A Vortex Candidate derived from incomplete evidence SHOULD preserve that limitation.

---

# 48. Provenance

Circulation and Vortex Candidate records SHOULD preserve provenance.

Recommended fields:

```text
generated_at
analyzer_id
source_flow_refs
source_circulation_refs
source_trace_refs
source_digest
```

---

# 49. ZN-VORTEX-PROV-001 — Evidence Traceability

A Vortex Candidate SHOULD be reconstructable from referenced circulation evidence.

Conceptually:

```text
Vortex Candidate
↓
Circulation Observation
↓
Region Flow
↓
Trace / Receipt
```

---

# 50. Example — Normal Review Loop

```text
planner
↓
executor
↓
reviewer
↓
planner
```

This cycle occurs repeatedly.

Possible observation:

```text
cycle_count = 10
return_count = 14
```

This may produce:

```text
circulation_candidate
```

but not necessarily:

```text
vortex_candidate
```

if the structure is weak or intentionally bounded.

---

# 51. Example — Persistent Circulation

Suppose:

```text
window 1:
cycle_count = 7

window 2:
cycle_count = 8

window 3:
cycle_count = 9
```

with nearly identical Region membership.

This provides stronger evidence of persistent circulation.

---

# 52. Example — Candidate Vortex

Suppose:

```text
cycle_count = 18
return_count = 30
cycle_density = 0.72
persistence_count = 6
```

under a declared classifier.

A system MAY classify:

```text
vortex_candidate
```

It MUST NOT automatically classify:

```text
storm
```

---

# 53. Example — Temporary Spike

```text
t0 cycle_count = 1
t1 cycle_count = 21
t2 cycle_count = 0
t3 cycle_count = 1
```

This may be an isolated burst rather than persistent vortex-like behavior.

Persistence analysis SHOULD distinguish the two.

---

# 54. Example — Direction Matters

These structures are different:

```text
A → B → C → A
```

and:

```text
A → C → B → A
```

Even if Region membership is identical, edge direction is different.

v0.6 MUST preserve that distinction.

---

# 55. Example — Self-Reinforcing Loop

Consider:

```text
planner
↓
executor
↓
failure
↓
retry
↓
planner
```

If this loop grows in frequency, v0.6 may observe increasing circulation.

It does not determine whether the loop is beneficial or harmful.

---

# 56. Human Interpretation Boundary

A Vortex Candidate is observational guidance.

It MUST NOT itself grant authority to:

- stop agents,
- revoke permissions,
- isolate Regions,
- cancel transactions,
- alter policies,
- shut down services,
- or perform external actions.

Intervention remains a separate authority decision.

---

# 57. Data Minimization

v0.6 SHOULD operate on structural events and aggregate relationships.

It SHOULD NOT require:

- hidden chain-of-thought,
- full private messages,
- unrelated personal data,
- complete prompt bodies,
- or unnecessary content inspection.

The goal is to observe circulation without unnecessarily observing meaning.

---

# 58. Minimum v0.6 Conformance Requirements

An implementation claiming v0.6 conformance MUST ensure:

### Requirement 1

Circulation observations use bounded time windows.

### Requirement 2

At least two distinct Regions or nodes participate in qualifying circulation.

### Requirement 3

Cycle evidence is derived from observable directional relationships.

### Requirement 4

Direction is preserved.

### Requirement 5

Vortex Candidates reference underlying circulation evidence.

### Requirement 6

Vortex Candidate methods are explicit.

### Requirement 7

Threshold-based classification exposes thresholds.

### Requirement 8

A Vortex Candidate is not represented as a Storm.

---

# 59. Recommended v0.6 Schemas

The minimum machine-readable implementation SHOULD introduce:

```text
schemas/circulation-observation-v0.6.schema.json
schemas/vortex-candidate-v0.6.schema.json
```

A future extension MAY introduce:

```text
schemas/cycle-record-v0.6.schema.json
```

if cycle-level normalization requires its own normative object.

For the initial v0.6 implementation, cycle details MAY remain embedded inside Circulation Observation.

---

# 60. Recommended Schema Validation

JSON Schema SHOULD validate:

```text
required identifiers
Region arrays
minimum Region count
non-negative counts
classification enums
threshold structures
confidence bounds
persistence structures
provenance structures
```

---

# 61. Recommended Conformance Validation

Semantic validation SHOULD check:

```text
window_end > window_start

Region refs are distinct

cycle paths are directional

cycle paths return to origin

cycle_count agrees with supplied cycle evidence

circulation references exist

Vortex Candidate references valid circulation evidence

threshold conditions are satisfied

weighted scores are reconstructable

provenance refs match source refs

generated_at >= window_end

classification does not escalate to Storm
```

---

# 62. Failure Examples

## FAIL-CIRC-001 — One Region Only

```text
region_refs = ["planner-01"]
```

---

## FAIL-CIRC-002 — Non-Returning Path

```text
A → B → C
```

is reported as a complete cycle.

---

## FAIL-CIRC-003 — Invalid Direction Reconstruction

Cycle evidence does not match the underlying directed flow.

---

## FAIL-CIRC-004 — Incorrect Cycle Count

Reported:

```text
cycle_count = 5
```

but reconstructable evidence contains only:

```text
3
```

qualifying cycles.

---

## FAIL-VORTEX-001 — Missing Circulation Evidence

A Vortex Candidate references no valid circulation record.

---

## FAIL-VORTEX-002 — Hidden Thresholds

A threshold-based Vortex Candidate does not expose its threshold configuration.

---

## FAIL-VORTEX-003 — Unsupported Confirmation

```text
classification = vortex_confirmed
```

is invalid in v0.6.

---

## FAIL-VORTEX-004 — Storm Escalation

```text
classification = storm
```

is invalid in v0.6.

---

# 63. Minimum Circulation Law

v0.6 can be summarized as:

> **No circulation without directed return flow.**  
> **No candidate without cycle evidence.**  
> **No Vortex Candidate without circulation evidence.**  
> **No candidate presented as certainty.**  
> **No Vortex silently promoted to Storm.**

---

# 64. AI Meteorology Core

With v0.6, the first AI Meteorology Core becomes:

```text
v0.3
Measure the atmosphere.

v0.4
Measure its movement.

v0.5
Measure its boundaries.

v0.6
Measure its circulation.
```

Together:

```text
Field
+
Flow
+
Gradient
+
Front Candidate
+
Circulation
+
Vortex Candidate
```

form the minimum structural vocabulary for observing weather-like behavior in an AI network.

---

# 65. Why v0.6 Is a Natural Milestone

v0.1 through v0.6 remain primarily observational and reconstructive.

They answer:

```text
Who exists?

What authority exists?

What is happening?

How is it changing?

Where are structural boundaries?

Where is activity circulating?
```

They do not yet attempt to answer:

```text
What will happen next?
```

That is the natural boundary between:

```text
Structural Meteorology
```

and:

```text
Forecasting
```

---

# 66. Observation and Structural Meteorology Core

The completed first-stage architecture is:

```text
AI Zero Network Core v0.1–v0.6

Existence
   ↓
Authority
   ↓
Observation
   ↓
Dynamics
   ↓
Boundary
   ↓
Circulation
```

This forms the **Observation & Structural Meteorology Core**.

---

# 67. Future Boundary

A future version MAY explore:

```text
Storm Candidate
Forecast
Forecast Confidence
Trajectory
Interaction between Front and Vortex
Storm Lifecycle
Intervention
```

However, those concepts SHOULD remain outside the v0.1–v0.6 core.

---

# 68. AI Zero Network v0.6 Definition

AI Zero Network v0.6 defines the minimum structure required to observe cyclic directional flow and represent persistent circulation as provisional Vortex Candidates.

In compact form:

> **Flow creates paths.**  
> **Returning paths create cycles.**  
> **Persistent cycles create circulation.**  
> **Circulation may reveal a vortex.**

But:

> **A vortex candidate is not a storm.**

That restraint closes the first AI Zero Network Observation & Structural Meteorology Core.
