# Changelog

All notable changes to **AI Zero Network** are documented in this file.

AI Zero Network uses explicit version boundaries so that earlier structural semantics are not silently changed by later versions.

The current milestone is:

> **Observation & Structural Meteorology Core v0.1–v0.6**

---

## [Unreleased]

### Planned

Future work may explore concepts outside the current observation core, including:

- Storm Candidate
- Front / Vortex interaction
- trajectory analysis
- forecasting
- forecast confidence
- storm lifecycle
- higher-order AI Meteorology
- intervention policies

These concepts are intentionally not included in v0.1–v0.6.

The current core stops at reconstructable observation and provisional structural interpretation.

---

# [0.6] — Circulation and Vortex Candidates

## Added

### Circulation Observation

Introduced a formal representation for observable cyclic directional flow.

New schema:

```text
schemas/circulation-observation-v0.6.schema.json
```

Core fields include:

```text
circulation_id
window_start
window_end
region_refs
cycle_count
return_count
```

Optional structures include:

```text
cycles
cycle_method
cycle_density
return_rate
circulation_strength
persistence
source
provenance
```

---

### Cycle Evidence

Added explicit cycle records capable of representing directed return paths.

Example:

```text
planner
→ executor
→ reviewer
→ planner
```

Cycle evidence can include:

```text
cycle_id
path
occurrence_count
```

Semantic conformance verifies that qualifying cycle paths return to their origin.

---

### Vortex Candidate

Introduced provisional vortex-like classification.

New schema:

```text
schemas/vortex-candidate-v0.6.schema.json
```

Supported classifier methods include:

```text
persistent_circulation_score_v1
cycle_density_threshold_v1
multi_signal_vortex_candidate_v1
```

Added support for:

```text
circulation_refs
core_regions
thresholds
weights
signals
score
confidence
strength
persistence
provenance
```

---

### Candidate-Only Classification

The v0.6 schema explicitly permits:

```text
vortex_candidate
```

and rejects unsupported certainty such as:

```text
vortex_confirmed
storm
```

This preserves the distinction:

```text
Circulation
≠
Vortex

Vortex Candidate
≠
Storm
```

---

### Schema Examples

Added:

```text
examples/v0.6/pass/
examples/v0.6/fail/
```

covering:

- minimal circulation
- explicit cycle evidence
- threshold-based Vortex Candidates
- multi-signal Vortex Candidates
- invalid Region counts
- negative cycle counts
- invalid cycle path shape
- unsupported vortex confirmation
- missing thresholds
- missing scores
- empty circulation references

---

### Semantic Conformance

Added:

```text
examples/v0.6/conformance/pass/
examples/v0.6/conformance/fail/
```

Semantic checks include:

```text
window_start < window_end

cycle path returns to origin

cycle Regions belong to region_refs

Σ occurrence_count == cycle_count

circulation_refs exist

core_regions belong to circulation evidence

cycle-density threshold is satisfied

weights sum to 1.0

score == Σ(signal × weight)

provenance references match evidence

generated_at >= window_end
```

---

### Validators

Added:

```text
scripts/validate_v0_6.py
scripts/validate_conformance_v0_6.py
```

The schema validator automatically distinguishes:

```text
circulation_id
→ Circulation Observation

candidate_id
→ Vortex Candidate
```

---

### CI

Added v0.6 Schema and Conformance validation to GitHub Actions.

---

## Structural Meaning

v0.6 makes **circulation** observable.

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

With v0.6, the first AI Zero Network Observation & Structural Meteorology Core reaches a natural milestone.

---

# [0.5] — Boundary Gradients and Front Candidates

## Added

### Boundary Gradient

Introduced formal cross-region comparison.

New schema:

```text
schemas/boundary-gradient-v0.5.schema.json
```

A Boundary Gradient compares compatible values across two distinct Regions.

Supported methods:

```text
absolute_difference
directional_difference
```

For:

```text
absolute_difference
```

the gradient is:

```text
abs(value_a - value_b)
```

For:

```text
directional_difference
```

the gradient is:

```text
value_a - value_b
```

---

### Boundary Metadata

Added support for:

```text
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
comparison_state
temporal_alignment
source
provenance
```

---

### Front Candidate

Introduced provisional Front classification.

New schema:

```text
schemas/front-candidate-v0.5.schema.json
```

Supported methods:

```text
single_metric_threshold_v1
multi_metric_threshold_v1
gradient_weighted_score_v1
```

Added:

```text
gradient_refs
thresholds
weights
score
confidence
strength
persistence
provenance
```

---

### Candidate Principle

v0.5 explicitly establishes:

```text
Boundary Gradient
≠
Front

Front Candidate
≠
Confirmed Front
```

The schema permits only:

```text
front_candidate
```

as the normative classification.

---

### Schema Examples

Added:

```text
examples/v0.5/pass/
examples/v0.5/fail/
```

covering Boundary Gradient and Front Candidate structural validation.

---

### Semantic Conformance

Added:

```text
examples/v0.5/conformance/pass/
examples/v0.5/conformance/fail/
```

Checks include:

```text
region_a != region_b

gradient reconstruction

gradient_refs exist

candidate boundary matches gradient boundary

candidate Region pair matches evidence

threshold conditions are satisfied

weights sum to 1.0

weighted score is reconstructable

generated_at >= window_end
```

---

### Weighted Front Score

For:

```text
gradient_weighted_score_v1
```

v0.5 conformance reconstructs:

```text
score
=
Σ(
  abs(metric_gradient)
  ×
  metric_weight
)
```

---

### Validators

Added:

```text
scripts/validate_v0_5.py
scripts/validate_conformance_v0_5.py
```

---

### CI

Added v0.5 Schema and Conformance validation to GitHub Actions.

---

## Structural Meaning

v0.5 makes **network boundaries** measurable.

The progression becomes:

```text
Region A
+
Region B
↓
Boundary Gradient
↓
Front Candidate
```

v0.5 is the first formal boundary-analysis layer of AI Meteorology.

---

# [0.4] — Field Dynamics

## Added

### Field Delta

Introduced measurable change between Field Snapshots.

New schema:

```text
schemas/field-delta-v0.4.schema.json
```

A Field Delta compares:

```text
from_snapshot
→
to_snapshot
```

and records observable changes.

Unlike v0.3 observations, Delta values may be:

```text
positive
zero
negative
```

---

### Dynamic Metrics

Field Delta supports changes in:

```text
trace_count
receipt_count
authority_request_count
authority_grant_count
authority_deny_count
active_agent_count
incoming_trace_count
outgoing_trace_count
cross_region_trace_count
causal_edge_count
resources
```

---

### Trend Interpretation

Added derived trend support:

```text
rising
falling
stable
```

Observation and interpretation remain separated.

---

### Window Compatibility

Added:

```text
window_compatibility
normalization_method
delta_state
```

Unequal observation windows can be explicitly marked as normalized.

---

### Region Flow

Introduced directional flow between Regions.

New schema:

```text
schemas/region-flow-v0.4.schema.json
```

Region Flow preserves direction:

```text
A → B
≠
B → A
```

Supported observations include:

```text
trace_count
receipt_count
message_count
tool_call_count
authority_transfer_count
resource_flow
```

---

### Flow Metrics

Added derived:

```text
flow_rate
effective_flow
```

with explicit derivation methods.

---

### Schema Examples

Added:

```text
examples/v0.4/pass/
examples/v0.4/fail/
```

for Field Delta and Region Flow.

---

### Semantic Conformance

Added:

```text
examples/v0.4/conformance/pass/
examples/v0.4/conformance/fail/
```

Checks include:

```text
source snapshots exist

forward snapshot ordering

same-region Field Delta comparison

reported Delta matches actual source difference

unequal windows declare normalization

derived trends match from/to values

source_region != target_region

flow window is valid

flow_rate is reconstructable

generated_at >= window_end
```

---

### Validators

Added:

```text
scripts/validate_v0_4.py
scripts/validate_conformance_v0_4.py
```

---

### CI

Added v0.4 Schema and Conformance validation to GitHub Actions.

---

## Structural Meaning

v0.4 turns a static field into a dynamic one.

The progression becomes:

```text
Field Snapshot t0
↓
Field Snapshot t1
↓
Field Delta
```

and:

```text
Region A
→
Region B
```

This establishes the first formal notion of network movement.

---

# [0.3] — Field Observation

## Added

### Field Snapshot

Introduced aggregate observation of network state.

New schema:

```text
schemas/field-snapshot-v0.3.schema.json
```

A Field Snapshot represents a Region during a bounded observation window.

Required observations include:

```text
trace_count
receipt_count
authority_request_count
authority_grant_count
authority_deny_count
active_agent_count
```

Optional observations include:

```text
incoming_trace_count
outgoing_trace_count
cross_region_trace_count
causal_edge_count
resources
```

---

### Observation State

Added:

```text
complete
partial
provisional
```

to distinguish data completeness.

---

### Derived Field Metrics

Added optional:

```text
activity_pressure
effective_pressure
authority_friction
```

Each derived metric includes:

```text
value
method
```

---

### Observation / Interpretation Separation

Established the principle:

```text
Observation
≠
Interpretation
```

Raw field measurements and derived metrics are structurally separated.

---

### Provenance

Added optional:

```text
generated_at
collector_id
source_record_count
source_digest
```

---

### Schema Examples

Added:

```text
examples/v0.3/pass/
examples/v0.3/fail/
```

---

### Semantic Conformance

Added:

```text
examples/v0.3/conformance/pass/
examples/v0.3/conformance/fail/
```

Checks include:

```text
window_start < window_end

grant_count + deny_count <= request_count

authority_friction matches deny/request

zero requests do not silently become zero friction

generated_at >= window_end

source_record_count passes conservative consistency checks
```

---

### Validators

Added:

```text
scripts/validate_v0_3.py
scripts/validate_conformance_v0_3.py
```

---

### CI

Added v0.3 Schema and Conformance validation to GitHub Actions.

---

## Structural Meaning

v0.3 moves AI Zero Network from individual events to field-level observation.

The central transition is:

```text
Records
↓
Measurements
↓
Field
```

v0.3 establishes the network “atmosphere.”

---

# [0.2] — Authority Provenance and Bounded Delegation

## Added

### Authority Record

Introduced explicit authority provenance.

New schema:

```text
schemas/authority-v0.2.schema.json
```

Authority records include:

```text
authority_id
requester_id
issuer_id
subject_id
scope
decision
source_type
issued_at
expires_at
revoked_at
delegation_parent
```

---

### Authority Provenance

Established:

> **No authority without provenance.**

Every authority decision identifies its source and issuer.

---

### Self-Escalation Protection

Added semantic checks preventing an actor from silently issuing new privilege to itself.

---

### Authority Validity

Added checks for:

```text
issuance
expiration
revocation
decision
subject
scope
```

---

### Bounded Delegation

Introduced delegation chains.

Core rules:

```text
parent authority must exist

parent authority must remain valid

child scope ⊆ parent scope

child lifetime <= parent lifetime

parent revocation propagates downward
```

---

### Effective Scope

Delegated authority is bounded by the chain of parent authorities.

Conceptually:

```text
effective_scope
=
scope(A0)
∩
scope(A1)
∩
...
∩
scope(An)
```

---

### Schema Examples

Added:

```text
examples/v0.2/pass/
examples/v0.2/fail/
```

---

### Semantic Conformance

Added:

```text
examples/v0.2/conformance/pass/
examples/v0.2/conformance/fail/
```

Cases cover:

- valid direct authority
- valid revocation after action
- valid delegation
- narrowed delegation
- self-escalation
- expired authority
- revoked authority
- missing delegation parent
- child scope exceeding parent
- child lifetime exceeding parent

---

### Validators

Added:

```text
scripts/validate_v0_2.py
scripts/validate_conformance_v0_2.py
```

---

### CI

Added v0.2 Authority and Conformance validation to GitHub Actions.

---

## Structural Meaning

v0.2 answers:

> **Where did authority come from?**

The lifecycle expands from basic action tracking to:

```text
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

# [0.1] — Initial Observable Network Core

## Added

### Initial Specification

Introduced the minimum AI Zero Network model.

Specification:

```text
specs/ai-zero-network-v0.1.md
```

v0.1 defines the minimum structural conditions for observable AI agent activity.

---

### Trace

Added:

```text
schemas/trace-v0.1.schema.json
```

Trace records externally relevant state transitions without requiring hidden chain-of-thought.

Supported event types include:

```text
decision
message
tool_call
authority_request
authority_denied
action_requested
action_completed
error
state_transition
```

---

### Receipt

Added:

```text
schemas/receipt-v0.1.schema.json
```

A Receipt represents successful externally effective action.

Core fields include:

```text
receipt_id
trace_id
agent_id
action
authority_used
timestamp
```

Optional fields include:

```text
resources
result_hash
prev_receipt_hash
signature
```

---

### Core Invariants

Established:

```text
ZN-INV-001 — Unique Identity

ZN-INV-002 — Meaningful Events Produce Trace

ZN-INV-003 — Authority Before External Action

ZN-INV-004 — Receipt After Effective Action
```

---

### Minimum Lifecycle

Introduced:

```text
Identity
↓
Trace
↓
Authority Validation
↓
External Action
↓
Receipt
```

---

### Compact Law

Established:

```text
No invisible actor.

No invisible action.

No authorityless action.

No receiptless effect.
```

---

### Schema Examples

Added:

```text
examples/v0.1/pass/
examples/v0.1/fail/
```

for Trace and Receipt Schema validation.

---

### Schema Validator

Added:

```text
scripts/validate.py
```

using:

```text
Draft 2020-12 JSON Schema
jsonschema
FormatChecker
```

---

### Semantic Conformance

Added:

```text
specs/conformance.md
```

and initial semantic fixtures:

```text
examples/v0.1/conformance/pass/
examples/v0.1/conformance/fail/
```

Initial semantic rules include:

```text
known participant

Receipt references Trace

actor consistency

authority before action

scope covers action

no self-escalation

denied action produces no Receipt

failed action produces no success Receipt

successful external action requires Receipt

no duplicate authoritative Receipt

no self-referencing Trace causality

Receipt time does not precede action
```

---

### Conformance Validator

Added:

```text
scripts/validate_conformance.py
```

---

### Continuous Validation

Added:

```text
.github/workflows/validate.yml
```

for automated Schema and semantic checks.

---

## Structural Meaning

v0.1 establishes the first observable substrate:

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
```

It defines the minimum rule:

> **Externally meaningful activity should leave reconstructable evidence.**

---

# Core Evolution

The complete v0.1–v0.6 progression is:

```text
v0.1
Existence

↓


v0.2
Authority

↓


v0.3
Field Observation

↓


v0.4
Field Dynamics

↓


v0.5
Boundary / Front Candidate

↓


v0.6
Circulation / Vortex Candidate
```

Structurally:

```text
Actor
↓
Authority
↓
Field
↓
Movement
↓
Boundary
↓
Circulation
```

---

# Observation & Structural Meteorology Core

With v0.6, AI Zero Network establishes a first coherent structural meteorology layer.

```text
Measure the actors.
↓
Trace their authority.
↓
Measure the field.
↓
Measure its movement.
↓
Measure its boundaries.
↓
Measure its circulation.
```

The resulting vocabulary includes:

```text
Trace
Receipt
Authority
Field Snapshot
Field Delta
Region Flow
Boundary Gradient
Front Candidate
Circulation Observation
Vortex Candidate
```

---

# Current Architectural Boundary

v0.1–v0.6 primarily cover:

```text
Observation
Reconstruction
Structural Interpretation
```

They intentionally stop before:

```text
Prediction
Forecasting
Storm Classification
Trajectory Prediction
Automated Intervention
```

This boundary is deliberate.

---

# Compatibility Principle

Later versions SHOULD NOT silently redefine earlier semantics.

Versioned specifications, schemas, examples, and validators are treated as explicit contracts.

If semantics materially change, a new version SHOULD be introduced.

---

# Conformance Principle

Across all current releases:

> **No claim without structure.**  
> **No effect without evidence.**  
> **No authority without provenance.**  
> **No measurement without observable basis.**  
> **No derived value without a method.**  
> **No candidate without supporting evidence.**  
> **No candidate presented as certainty.**  
> **No observation silently becomes authority.**
