# AI Zero Network v0.4

## Field Dynamics and the Entry Point to AI Meteorology

**Status:** Draft  
**Version:** v0.4  
**Scope:** Field change, temporal comparison, directional flow, boundary gradients, and circulation candidates  
**Repository:** `ai-zero-network`

---

## 1. Purpose

AI Zero Network v0.4 extends static Field Observation into Field Dynamics.

v0.3 answered:

> **What is the observable state of a Region during a bounded time window?**

v0.4 asks:

> **How is that state changing over time, and how is activity moving between Regions?**

The progression is:

```text
v0.1
Existence

v0.2
Authority

v0.3
Observation

v0.4
Dynamics
```

v0.4 is the first version that treats the Zero Network as a changing field rather than a collection of static observations.

Its core principle is:

> **A field becomes meteorological only when change, direction, and interaction become observable.**

---

# 2. Relationship to v0.3

v0.3 introduced:

```text
Region
+
Observation Window
+
Field Snapshot
```

v0.4 introduces:

```text
Field Snapshot t0
        ↓
Field Snapshot t1
        ↓
Field Delta
        ↓
Flow / Gradient / Circulation
```

v0.4 does not replace Field Snapshots.

It compares them.

A valid Field Delta MUST be reconstructable from valid Field Snapshots or equivalent observable records.

---

# 3. Design Goals

v0.4 has six goals.

1. Represent change between field observations.
2. Distinguish raw change from interpreted trend.
3. Represent directional flow between Regions.
4. Measure boundary differences without prematurely declaring a Front.
5. Observe circulation without prematurely declaring a Vortex or Storm.
6. Prepare stable inputs for later AI Meteorology layers.

---

# 4. Non-Goals

v0.4 does NOT define:

- definitive Front detection,
- cold-front or warm-front classification,
- vortex classification,
- storm severity,
- typhoon-like states,
- weather forecasting,
- predictive intervention,
- autonomous authority restriction,
- route optimization,
- risk forecasting,
- or automatic governance.

These belong to later versions.

---

# 5. Normative Language

The keywords **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are normative.

---

# 6. Core v0.4 Concepts

v0.4 introduces five concepts.

```text
Field Delta
Pressure Trend
Region Flow
Boundary Gradient
Circulation Candidate
```

These concepts form the minimum dynamic layer.

---

# 7. Field Delta

A **Field Delta** represents measurable change between two Field Snapshots.

Conceptually:

```text
ΔF = F(t1) - F(t0)
```

A Field Delta MUST identify:

```text
delta_id
region
from_snapshot
to_snapshot
changes
```

Example:

```json
{
  "schema_version": "0.4",
  "delta_id": "4f58566e-b38a-4ef8-9ed6-8dd947ea8212",
  "region": "finance-01",
  "from_snapshot": "11111111-1111-4111-8111-111111111111",
  "to_snapshot": "22222222-2222-4222-8222-222222222222",
  "changes": {
    "trace_count": 60,
    "receipt_count": 14,
    "authority_request_count": 17,
    "authority_grant_count": 9,
    "authority_deny_count": 8,
    "active_agent_count": 9
  }
}
```

Unlike v0.3 raw counts, Delta values MAY be negative.

Example:

```text
trace_count = -40
```

means observable Trace activity decreased by 40 between the compared snapshots.

---

# 8. Delta Semantics

For any compatible metric:

```text
delta(metric)
=
to_snapshot.metric
-
from_snapshot.metric
```

Examples:

```text
trace_count:
120 → 180

delta:
+60
```

```text
receipt_count:
22 → 9

delta:
-13
```

A Delta MUST NOT silently use a different calculation rule without documenting it.

---

# 9. Compatible Snapshot Requirement

Two snapshots used for a direct Field Delta MUST have compatible semantics.

At minimum, implementations MUST ensure compatibility of:

```text
region
metric definitions
aggregation semantics
```

Implementations SHOULD also compare equal-duration Observation Windows when interpreting rate-like change.

Example:

```text
t0 window:
5 minutes

t1 window:
5 minutes
```

is directly comparable.

A 1-minute snapshot and a 1-hour snapshot MAY be compared only if the implementation explicitly normalizes their metrics.

---

# 10. Core Dynamic Invariants

## ZN-DYN-001 — Delta Requires Two Existing Snapshots

Every Field Delta MUST reference:

```text
from_snapshot
to_snapshot
```

Both snapshots MUST exist or be otherwise verifiably resolvable.

---

## ZN-DYN-002 — Snapshot Order MUST Be Forward in Time

The snapshot represented by `to_snapshot` MUST follow the snapshot represented by `from_snapshot`.

Conceptually:

```text
from.window_end
<=
to.window_end
```

Implementations SHOULD prevent accidental reverse deltas unless explicitly marked as reverse analysis.

---

## ZN-DYN-003 — Region Compatibility

A normal intra-region Field Delta MUST compare snapshots from the same Region.

Example:

```text
finance-01
→
finance-01
```

The following MUST NOT be represented as an ordinary Field Delta:

```text
finance-01
→
safety-01
```

Differences between Regions belong to Boundary Gradient or Region Flow structures.

---

## ZN-DYN-004 — Raw Change and Interpretation MUST Remain Separate

A measured change:

```text
trace_count_delta = +60
```

is not identical to:

```text
activity_pressure = rising
```

The first is measured change.

The second is interpretation.

Implementations MUST keep these conceptually and structurally distinguishable.

---

# 11. Field Delta Metrics

A v0.4 Field Delta MAY include changes for any compatible v0.3 observation metric.

Recommended minimum fields:

```text
trace_count
receipt_count
authority_request_count
authority_grant_count
authority_deny_count
active_agent_count
```

Optional:

```text
incoming_trace_count
outgoing_trace_count
cross_region_trace_count
causal_edge_count
tokens
cost
compute_units
```

---

# 12. Pressure Trend

A **Pressure Trend** is a derived interpretation of change over time.

Minimum trend values are:

```text
rising
falling
stable
```

Example:

```json
{
  "activity_pressure": {
    "from": 0.42,
    "to": 0.71,
    "trend": "rising",
    "method": "compare_normalized_activity_pressure_v1"
  }
}
```

Trend classification MUST identify its method or threshold semantics.

---

# 13. Stable Trend

`stable` MUST NOT mean exact equality unless the method explicitly defines it that way.

Implementations MAY define a tolerance.

Example:

```text
abs(to - from) < 0.02
→ stable
```

If such a tolerance is used, it MUST be documented.

---

# 14. Pressure Trend Is Not Risk Classification

The following is valid:

```text
activity_pressure = rising
```

The following belongs to a higher layer:

```text
danger_level = severe
```

v0.4 MUST NOT treat rising activity alone as evidence of danger.

---

# 15. Region Flow

A **Region Flow** represents observable directional movement between logical Regions.

Example:

```text
finance-01
      ↓
payment-01
```

A Region Flow MUST identify:

```text
source_region
target_region
```

and one or more measurable flow quantities.

Example:

```json
{
  "schema_version": "0.4",
  "flow_id": "72c60ef3-2fd1-4078-a0ab-64ec2e688e84",
  "source_region": "finance-01",
  "target_region": "payment-01",
  "window_start": "2026-10-03T13:00:00+09:00",
  "window_end": "2026-10-03T13:05:00+09:00",
  "observations": {
    "trace_count": 48,
    "receipt_count": 9
  }
}
```

---

# 16. Region Flow Invariants

## ZN-FLOW-001 — Source and Target Required

Every Region Flow MUST identify a source and target Region.

---

## ZN-FLOW-002 — Ordinary Flow MUST Be Directional

The implementation MUST distinguish:

```text
A → B
```

from:

```text
B → A
```

These are separate directional flows.

---

## ZN-FLOW-003 — Flow Metrics MUST Be Observable

Region Flow quantities MUST derive from observable records, such as:

- Trace causal transitions,
- cross-region Tool calls,
- Receipt-linked actions,
- explicit message transfers,
- or equivalent auditable events.

A guessed flow MUST NOT be represented as raw flow observation.

---

# 17. Network Wind

Region Flow provides the minimum basis for future **Network Wind**.

Conceptually:

```text
source_region
+
target_region
+
flow magnitude
+
time window
=
directional movement
```

v0.4 does NOT define a continuous vector field.

It defines discrete directional edges.

A future version MAY interpolate those edges into a network-scale field.

---

# 18. Boundary Gradient

A **Boundary Gradient** measures the difference between two Regions across a shared or relevant boundary.

Example:

```text
Region A
activity_pressure = 0.85

Region B
activity_pressure = 0.35
```

The difference is:

```text
0.50
```

This difference MAY be represented as a Boundary Gradient.

---

# 19. Boundary Gradient Structure

A minimal Boundary Gradient SHOULD identify:

```text
region_a
region_b
metric
value_a
value_b
gradient
method
```

Example:

```json
{
  "region_a": "finance-01",
  "region_b": "safety-01",
  "metric": "activity_pressure",
  "value_a": 0.85,
  "value_b": 0.35,
  "gradient": 0.50,
  "method": "absolute_difference"
}
```

---

# 20. Boundary Gradient Is Not Automatically a Front

This distinction is fundamental.

A large gradient MAY indicate a possible Front.

It does not prove one.

Therefore v0.4 MAY represent:

```text
front_candidate
```

but MUST NOT claim:

```text
front_confirmed
```

unless a higher-level specification defines the required evidence.

---

# 21. Front Candidate

A **Front Candidate** is an interpreted state indicating that a Region boundary may warrant higher-order meteorological analysis.

Example:

```json
{
  "classification": "front_candidate",
  "confidence": 0.68,
  "method": "multi_metric_boundary_gradient_v1"
}
```

The `confidence` field, if used, MUST describe classifier confidence or score semantics.

It MUST NOT be presented as objective probability unless the implementation has a calibrated probabilistic model.

---

# 22. Candidate Principle

v0.4 introduces a general rule:

> **Early meteorological structures are candidates, not conclusions.**

This applies to:

```text
front_candidate
circulation_candidate
```

The purpose is to prevent an interpretation layer from being mistaken for direct observation.

---

# 23. Circulation

Circulation describes repeated directional return flow.

Example:

```text
A → B
↑   ↓
D ← C
```

or:

```text
A → B → C → A
```

Such patterns MAY be identified from causal or communication graphs.

---

# 24. Circulation Candidate

A **Circulation Candidate** MAY be created when observable records show repeated cyclic flow.

Recommended underlying observations include:

```text
cycle_count
cycle_edge_count
repeated_return_count
cycle_density
```

Example:

```json
{
  "cycle_count": 7,
  "cycle_density": 0.31,
  "classification": "circulation_candidate",
  "method": "directed_cycle_detection_v1"
}
```

---

# 25. Circulation Is Not Automatically a Vortex

A cycle may represent:

- normal iterative workflow,
- retry logic,
- feedback optimization,
- coordination,
- error recovery,
- or unstable self-reinforcement.

Therefore:

```text
circulation_candidate
≠
vortex
```

and:

```text
vortex
≠
storm
```

v0.4 MUST preserve these distinctions.

---

# 26. Dynamic Observations vs Dynamic Interpretations

Examples of observable dynamic data:

```text
trace_count_delta = +60
cross_region_trace_count = 48
cycle_count = 7
gradient = 0.50
```

Examples of interpreted dynamic states:

```text
activity_pressure = rising
front_candidate = true
circulation_candidate = true
```

The first category belongs to observations or direct calculations.

The second category belongs to interpretation.

---

# 27. Field Dynamics Provenance

Dynamic records SHOULD preserve provenance.

Recommended fields include:

```text
generated_at
analyzer_id
source_snapshot_refs
source_digest
method
```

Example:

```json
{
  "generated_at": "2026-10-03T13:05:03+09:00",
  "analyzer_id": "field-dynamics-01",
  "source_snapshot_refs": [
    "snapshot-a",
    "snapshot-b"
  ]
}
```

---

# 28. Temporal Consistency

Dynamic interpretation depends on ordering.

Therefore:

```text
t0
<
t1
<
t2
```

SHOULD remain reconstructable.

An implementation SHOULD NOT silently reorder snapshots to produce a preferred trend.

---

# 29. Missing Snapshot Data

If one snapshot is:

```text
partial
```

and another is:

```text
complete
```

the resulting Delta MAY be unreliable.

Implementations SHOULD expose this uncertainty.

Example:

```text
delta_state = partial
```

or equivalent metadata.

Missing data MUST NOT silently become zero.

---

# 30. Normalization

Raw count differences may become misleading when Observation Window durations differ.

For example:

```text
Snapshot A:
100 traces / 5 minutes

Snapshot B:
150 traces / 60 minutes
```

Raw count:

```text
+50
```

does not mean activity increased.

Therefore, implementations SHOULD normalize rate-sensitive comparisons when window durations differ.

Possible form:

```text
trace_rate
=
trace_count / window_duration
```

Normalization methods MUST be documented.

---

# 31. Resource Dynamics

v0.4 MAY represent changes in resource usage.

Example:

```text
tokens:
+12000

cost:
+0.83

compute_units:
-8.2
```

Such changes MAY later contribute to an Effective Energy or Effective Pressure model.

v0.4 does not standardize those higher-order formulas.

---

# 32. Authority Dynamics

v0.4 MAY observe authority changes over time.

Examples:

```text
authority_request_delta
authority_grant_delta
authority_deny_delta
revocation_delta
delegation_delta
```

These measurements may later indicate:

- permission pressure,
- authority friction,
- governance instability,
- or delegation concentration.

v0.4 does not assign those meanings automatically.

---

# 33. Example — Rising Activity

Snapshot A:

```text
trace_count = 100
receipt_count = 10
```

Snapshot B:

```text
trace_count = 160
receipt_count = 24
```

Delta:

```text
trace_count = +60
receipt_count = +14
```

A derived indicator MAY state:

```text
activity trend = rising
effective activity trend = rising
```

It MUST NOT automatically conclude:

```text
storm forming
```

---

# 34. Example — Falling Activity

```text
trace_count:
180 → 120

receipt_count:
30 → 12
```

Delta:

```text
trace_count = -60
receipt_count = -18
```

Possible interpretation:

```text
activity trend = falling
```

No safety or quality conclusion is implied.

---

# 35. Example — Strong Region Boundary

```text
finance-01
activity_pressure = 0.88
authority_friction = 0.12

safety-01
activity_pressure = 0.39
authority_friction = 0.79
```

This produces strong differences across multiple metrics.

A higher-order analyzer MAY produce:

```text
front_candidate
```

v0.4 does not confirm a Front.

---

# 36. Example — Cyclic Workflow

```text
planner
   ↓
executor
   ↓
reviewer
   ↓
planner
```

Repeated cycles are observed.

This MAY produce:

```text
circulation_candidate
```

However, if the loop is an intentional review process, no harmful interpretation follows.

---

# 37. Field Dynamics Architecture

```text
Field Snapshot t0 ─────┐
                       │
Field Snapshot t1 ─────┼──→ Delta Analyzer
                       │         │
Field Snapshot t2 ─────┘         ▼
                            Field Deltas
                                 │
             ┌───────────────────┼────────────────────┐
             ▼                   ▼                    ▼
       Pressure Trend       Region Flow       Boundary Gradient
                                                      │
                                                      ▼
                                               Front Candidate

Trace Graph
    │
    ▼
Cycle Analysis
    │
    ▼
Circulation Candidate
```

---

# 38. AI Meteorology Boundary

v0.4 is the boundary between:

```text
field observation
```

and:

```text
meteorological interpretation
```

The lower layers tell us what changed.

The future meteorological layers will attempt to explain what those changes mean.

This distinction MUST remain explicit.

---

# 39. AI Meteorology Compatibility

v0.4 produces the minimum dynamic signals needed for later AI Meteorology.

Possible mappings include:

```text
activity delta
→ pressure change

Region Flow
→ wind direction

Boundary Gradient
→ front candidate

cyclic flow
→ circulation candidate

resource acceleration
→ energy change
```

These mappings remain conceptual in v0.4.

---

# 40. Minimum v0.4 Conformance Requirements

An implementation claiming AI Zero Network v0.4 conformance MUST:

### Requirement 1

Reference valid source snapshots for every Field Delta.

### Requirement 2

Preserve forward temporal ordering.

### Requirement 3

Compare compatible Region and metric semantics.

### Requirement 4

Keep measured change separate from interpreted trend.

### Requirement 5

Represent Region Flow direction explicitly.

### Requirement 6

Derive flow metrics from observable records.

### Requirement 7

Represent boundary differences separately from Front classification.

### Requirement 8

Represent circulation observations separately from Vortex or Storm classification.

---

# 41. Recommended v0.4 Objects

Two machine-readable schemas are recommended:

```text
schemas/field-delta-v0.4.schema.json
schemas/region-flow-v0.4.schema.json
```

Future versions MAY add:

```text
boundary-gradient
circulation-observation
meteorology-event
```

as separate normative objects.

---

# 42. v0.4 Failure Examples

## FAIL-DYN-001 — Missing Source Snapshot

```text
Field Delta references snapshot-x
but snapshot-x does not exist.
```

---

## FAIL-DYN-002 — Reverse Temporal Delta

```text
from_snapshot = later state
to_snapshot   = earlier state
```

without explicit reverse-analysis semantics.

---

## FAIL-DYN-003 — Cross-Region Delta Misuse

```text
from region = finance-01
to region   = safety-01
```

represented as an ordinary intra-region Field Delta.

---

## FAIL-DYN-004 — Incorrect Delta

```text
from trace_count = 100
to trace_count   = 160

reported delta   = +40
```

Expected:

```text
+60
```

---

## FAIL-FLOW-001 — Missing Flow Direction

Flow magnitude is reported without source and target Regions.

---

## FAIL-FLOW-002 — Unsupported Flow Claim

A Region Flow is reported without observable source records or documented derivation.

---

## FAIL-MET-001 — Gradient Presented as Confirmed Front

A boundary gradient directly declares:

```text
front_confirmed
```

without a higher-order Front specification.

---

## FAIL-MET-002 — Cycle Presented as Storm

A cyclic graph directly declares:

```text
storm = true
```

without an intermediate classification model.

---

# 43. Data Minimization

Field Dynamics SHOULD operate primarily on aggregated observations.

It SHOULD NOT require:

- full message bodies,
- private reasoning,
- hidden chain-of-thought,
- or unrelated personal content.

The network should observe motion without unnecessarily exposing content.

---

# 44. Human Interpretation Boundary

Dynamic indicators MAY support human decisions.

They SHOULD NOT silently become authority decisions.

For example:

```text
front_candidate detected
```

does not itself imply:

```text
revoke authority
```

Any later intervention layer SHOULD maintain a separate decision boundary.

---

# 45. Minimum Dynamics Law

AI Zero Network v0.4 can be reduced to five rules:

> **No Delta without two observations.**  
> **No trend without measurable change.**  
> **No flow without direction.**  
> **No Front without boundary evidence.**  
> **No Vortex without circulation evidence.**

And one additional restraint:

> **A candidate is not a conclusion.**

---

# 46. AI Zero Network v0.4 Definition

AI Zero Network v0.1 made actors observable.

v0.2 made authority provenance observable.

v0.3 made collective state observable.

v0.4 makes collective change observable.

The progression is:

```text
Actors
  ↓
Authority
  ↓
Field
  ↓
Dynamics
```

In compact form:

> **Snapshots become change.  
> Change becomes flow.  
> Flow begins to reveal weather.**

This is the minimum Field Dynamics layer and the entry point to AI Meteorology.
