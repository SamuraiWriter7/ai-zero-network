# AI Zero Network v0.3

## Field Observation and Minimal Network-State Measurement

**Status:** Draft  
**Version:** v0.3  
**Scope:** Region-based field observation, observation windows, raw metrics, and derived field indicators  
**Repository:** `ai-zero-network`

---

## 1. Purpose

AI Zero Network v0.3 extends the network from observable individual actions toward observable collective state.

v0.1 established:

```text
Identity
→ Trace
→ Authority
→ Effect
→ Receipt
```

v0.2 added:

```text
Authority Provenance
→ Expiration
→ Revocation
→ Bounded Delegation
```

v0.3 introduces the next layer:

```text
Observable Records
        ↓
Region
        ↓
Observation Window
        ↓
Aggregation
        ↓
Field Snapshot
```

The goal is not to predict agent behavior.

The goal is to make the collective condition of a Zero Network region measurable.

The core principle is:

> **Before predicting the weather, the network must be able to measure the atmosphere.**

---

# 2. Relationship to Previous Versions

AI Zero Network v0.3 preserves all requirements from v0.1 and v0.2.

v0.3 adds a field-observation layer above:

- Trace,
- Receipt,
- Authority,
- Participant identity,
- and resource records.

Conceptually:

```text
Agents / Humans / Tools
          ↓
       Trace
          ↓
      Authority
          ↓
        Effect
          ↓
       Receipt
          ↓
─────────────────────
   Field Observation
─────────────────────
          ↓
    Field Snapshot
```

Field Observation does not replace lower-layer records.

It summarizes them.

---

# 3. Design Goals

v0.3 has five goals.

1. Observe collective network state without inspecting private reasoning.
2. Aggregate records by logical region and time window.
3. Preserve separation between raw observations and derived interpretations.
4. Provide stable inputs for future AI Meteorology.
5. Avoid introducing forecasting or automatic intervention too early.

---

# 4. Non-Goals

v0.3 does NOT define:

- front detection,
- vortex detection,
- storm classification,
- weather forecasting,
- anomaly prediction,
- automated authority intervention,
- adaptive routing,
- economic redistribution,
- contribution scoring,
- agent reputation,
- trust scoring,
- or network-wide optimization.

These MAY be introduced in later versions.

---

# 5. Normative Language

The keywords **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are normative.

---

# 6. Core Field Concepts

v0.3 introduces four main concepts.

```text
Region
Observation Window
Raw Observation
Field Snapshot
```

Optional derived indicators MAY be attached to a Field Snapshot.

---

# 7. Region

A **Region** is a logical observation boundary.

A Region MAY represent:

- an application,
- organization,
- workload,
- business domain,
- agent group,
- network segment,
- security zone,
- geographic deployment,
- or another explicitly defined observation area.

Example:

```text
finance-01
```

or:

```text
document-processing
```

A Region MUST have a stable identifier within the applicable observation domain.

Region identifiers do not imply physical geography.

---

# 8. Region Assignment

Observable records used in field aggregation SHOULD be associated with a Region.

Examples include:

```text
Trace.region
Authority.region
Receipt.region
```

Implementations MAY infer Region membership from topology or participant registration when an individual record does not contain a region field.

However, inferred Region membership MUST be distinguishable from explicitly recorded Region membership when this distinction materially affects interpretation.

---

# 9. Observation Window

A **Field Snapshot** MUST represent a bounded observation interval.

The interval is defined by:

```text
window_start
window_end
```

with:

```text
window_start < window_end
```

Example:

```text
window_start:
2026-10-03T09:00:00+09:00

window_end:
2026-10-03T09:05:00+09:00
```

The interval MAY represent:

- one second,
- one minute,
- five minutes,
- one hour,
- or another implementation-defined duration.

Implementations SHOULD keep observation-window semantics consistent when comparing multiple snapshots.

---

# 10. Field Snapshot

A **Field Snapshot** is an immutable or reproducible summary of observable network records for one Region during one Observation Window.

Conceptually:

```text
FieldSnapshot(
    region,
    time window,
    raw observations,
    derived indicators
)
```

The canonical schema SHOULD be:

```text
schemas/field-snapshot-v0.3.schema.json
```

---

# 11. Minimum Field Snapshot

A v0.3 Field Snapshot MUST include:

```text
snapshot_id
region
window_start
window_end
observations
```

Example:

```json
{
  "schema_version": "0.3",
  "snapshot_id": "7f2c02b3-364e-47ae-9d70-fd18d9cf7801",
  "region": "finance-01",
  "window_start": "2026-10-03T09:00:00+09:00",
  "window_end": "2026-10-03T09:05:00+09:00",
  "observations": {
    "trace_count": 120,
    "receipt_count": 8,
    "authority_request_count": 14,
    "authority_grant_count": 6,
    "authority_deny_count": 8,
    "active_agent_count": 17
  }
}
```

---

# 12. Raw Observation Metrics

v0.3 defines the following minimum observation metrics.

## 12.1 trace_count

Number of qualifying Trace records in the Region and Observation Window.

```text
trace_count >= 0
```

---

## 12.2 receipt_count

Number of qualifying Receipt records in the Region and Observation Window.

```text
receipt_count >= 0
```

---

## 12.3 authority_request_count

Number of observed authority requests during the window.

```text
authority_request_count >= 0
```

---

## 12.4 authority_grant_count

Number of authority decisions that granted authority during the window.

```text
authority_grant_count >= 0
```

---

## 12.5 authority_deny_count

Number of authority decisions that denied authority during the window.

```text
authority_deny_count >= 0
```

---

## 12.6 active_agent_count

Number of distinct participants that produced qualifying observable activity during the window.

```text
active_agent_count >= 0
```

---

# 13. Optional Resource Metrics

A Field Snapshot MAY include aggregate resource usage.

Example:

```json
{
  "resources": {
    "tokens": 28400,
    "cost": 1.84,
    "compute_units": 93.4
  }
}
```

Resource metrics MUST indicate measured or reconstructable usage.

Implementations MUST NOT silently invent missing resource values.

Unknown usage SHOULD remain absent or explicitly unknown.

---

# 14. Optional Flow Metrics

v0.3 MAY include minimal causal-flow observations.

Examples:

```text
incoming_trace_count
outgoing_trace_count
cross_region_trace_count
causal_edge_count
```

These metrics MAY later support vector-like flow estimation.

However, v0.3 does not define a full spatial vector field.

---

# 15. Observation vs Interpretation

This distinction is a core invariant of v0.3.

Examples of observations:

```text
trace_count = 120
receipt_count = 8
authority_request_count = 14
authority_deny_count = 8
```

These are measured or reconstructed facts.

Examples of interpretations:

```text
activity_pressure = 0.72
effective_pressure = 0.41
authority_friction = 0.57
```

These are derived indicators.

Therefore:

> **Observation MUST NOT be represented as interpretation, and interpretation MUST NOT be represented as raw observation.**

---

# 16. Core Field Invariants

## ZN-FIELD-001 — Region and Window Required

Every Field Snapshot MUST identify:

```text
region
window_start
window_end
```

and:

```text
window_start < window_end
```

A field value without spatial or logical scope and time scope is not a valid v0.3 Field Snapshot.

---

## ZN-FIELD-002 — Metrics Must Derive From Observable Records

Every raw Field Snapshot metric MUST be derivable from observable Zero Network records or explicitly identified external measurement sources.

A Field Snapshot MUST NOT present guessed values as observed facts.

Examples of qualifying Zero Network records include:

- Trace,
- Receipt,
- Authority Record,
- participant registry events,
- resource accounting records.

---

## ZN-FIELD-003 — Derived Metrics Must Be Marked as Derived

Any metric computed from other observations MUST be represented separately from raw observations.

Example:

```json
{
  "observations": {
    "trace_count": 120,
    "receipt_count": 8
  },
  "derived": {
    "activity_pressure": 0.72
  }
}
```

The following is discouraged:

```json
{
  "observations": {
    "trace_count": 120,
    "activity_pressure": 0.72
  }
}
```

because it mixes measurement and interpretation.

---

## ZN-FIELD-004 — Counts Must Not Be Negative

Count-based metrics MUST be zero or greater.

Examples:

```text
trace_count >= 0
receipt_count >= 0
active_agent_count >= 0
```

Negative counts are invalid.

---

## ZN-FIELD-005 — Snapshot Scope Must Be Internally Consistent

Records counted toward a Field Snapshot MUST fall within the declared Region and Observation Window according to the implementation's documented inclusion rules.

A record outside the declared time window MUST NOT be silently counted.

A record from another Region MUST NOT be silently counted unless cross-region aggregation is explicitly represented.

---

# 17. Derived Field Indicators

v0.3 defines three OPTIONAL derived indicators.

These indicators are intentionally simple.

They are not universal physical laws.

Implementations MAY use different normalization functions, but MUST document them.

---

## 17.1 Activity Pressure

Activity Pressure estimates observable network activity intensity.

Conceptually:

```text
activity_pressure
← trace density
```

A minimal implementation MAY derive it from:

```text
trace_count
÷
observation duration
```

optionally normalized to an implementation-defined range.

Example:

```text
0.0 to 1.0
```

If normalization is used, its method MUST be documented.

---

## 17.2 Effective Pressure

Activity does not necessarily mean external effect.

Effective Pressure estimates externally effective activity.

Conceptually:

```text
effective_pressure
← Receipt activity
+ Authority usage
+ Resource consumption
```

A minimal implementation MAY begin with Receipt density alone.

More advanced weighting is outside v0.3.

---

## 17.3 Authority Friction

Authority Friction estimates the degree of resistance around permission requests.

A minimal form MAY be:

```text
authority_friction
=
authority_deny_count
/
authority_request_count
```

when:

```text
authority_request_count > 0
```

Example:

```text
14 requests
8 denies

authority_friction ≈ 0.5714
```

When no authority requests occur, implementations SHOULD represent friction as unavailable or explicitly define their zero-request behavior.

They MUST NOT silently divide by zero.

---

# 18. Derived Metric Metadata

Derived indicators SHOULD identify their derivation method.

Example:

```json
{
  "derived": {
    "activity_pressure": {
      "value": 0.72,
      "method": "trace_rate_normalized_v1"
    },
    "authority_friction": {
      "value": 0.5714,
      "method": "deny_count/request_count"
    }
  }
}
```

This allows future implementations to compare values without assuming identical formulas.

---

# 19. Example — Quiet Region

```json
{
  "region": "archive-01",
  "window_start": "2026-10-03T09:00:00+09:00",
  "window_end": "2026-10-03T09:05:00+09:00",
  "observations": {
    "trace_count": 3,
    "receipt_count": 0,
    "authority_request_count": 0,
    "authority_grant_count": 0,
    "authority_deny_count": 0,
    "active_agent_count": 1
  }
}
```

This represents low observable activity.

v0.3 does not label it:

```text
safe
stable
healthy
```

unless a higher interpretation layer explicitly makes that determination.

---

# 20. Example — High Activity, Low External Effect

```json
{
  "region": "research-01",
  "window_start": "2026-10-03T09:00:00+09:00",
  "window_end": "2026-10-03T09:05:00+09:00",
  "observations": {
    "trace_count": 420,
    "receipt_count": 4,
    "authority_request_count": 11,
    "authority_grant_count": 4,
    "authority_deny_count": 7,
    "active_agent_count": 32
  }
}
```

Interpretation MAY suggest:

```text
high activity
low external effect
```

But v0.3 stores the observation independently from that interpretation.

---

# 21. Example — Low Activity, High Effective Impact

Consider:

```text
trace_count = 12
receipt_count = 9
```

with several high-authority actions.

This illustrates an important principle:

> **Trace volume alone is not sufficient to estimate external impact.**

Future versions MAY combine:

- authority scope,
- resource consumption,
- action class,
- monetary exposure,
- or environmental impact

into stronger Effective Pressure models.

v0.3 deliberately does not standardize such weighting.

---

# 22. Cross-Region Observation

A record MAY cause activity across multiple Regions.

Example:

```text
finance-01
    ↓
payment-gateway
```

A future flow model may represent this as a directional edge.

v0.3 MAY count cross-region activity using:

```text
cross_region_trace_count
```

but MUST NOT duplicate one event into multiple ordinary region counts without documented semantics.

---

# 23. Snapshot Provenance

A Field Snapshot SHOULD record how it was produced.

Recommended fields include:

```text
generated_at
collector_id
source_record_count
source_digest
```

Example:

```json
{
  "generated_at": "2026-10-03T09:05:02+09:00",
  "collector_id": "collector-finance-01",
  "source_record_count": 148,
  "source_digest": "sha256..."
}
```

These fields allow a snapshot to be audited or regenerated.

---

# 24. Snapshot Immutability

Once a Field Snapshot is declared authoritative for a completed observation window, it SHOULD NOT be silently modified.

Corrections SHOULD produce:

- a replacement snapshot,
- a revision,
- or an explicit correction record.

Historical observation must remain distinguishable from later reinterpretation.

---

# 25. Late-Arriving Records

Distributed systems may receive records after an observation window closes.

v0.3 does not mandate one correction strategy.

Implementations MAY:

1. ignore late records,
2. revise the snapshot,
3. issue a corrected snapshot,
4. maintain provisional and finalized snapshots.

The chosen behavior MUST be documented.

A finalized snapshot SHOULD indicate whether late-arrival correction is possible.

---

# 26. Missing Data

Absence of data MUST NOT automatically be interpreted as zero activity.

For example:

```text
collector unavailable
```

is not equivalent to:

```text
trace_count = 0
```

Implementations SHOULD distinguish:

```text
zero
unknown
unavailable
partial
```

where materially relevant.

---

# 27. Observation Completeness

A Field Snapshot MAY include an observation state.

Recommended values:

```text
complete
partial
provisional
```

### complete

The implementation considers the observation window sufficiently collected.

### partial

Known records are missing.

### provisional

The window may still receive late-arriving data.

Future schemas MAY formalize this field.

---

# 28. Minimal Aggregation Procedure

A minimal v0.3 collector MAY operate as follows:

```text
1. Select Region
2. Select Observation Window
3. Read qualifying Trace records
4. Read qualifying Receipt records
5. Read qualifying Authority records
6. Determine active participants
7. Count raw events
8. Aggregate optional resource values
9. Produce Field Snapshot
10. Compute optional derived indicators
```

No machine-learning model is required.

---

# 29. Field Observation Architecture

```text
Trace ─────────┐
               │
Receipt ───────┤
               │
Authority ─────┼──→ Field Collector
               │          │
Participants ──┤          ▼
               │    Raw Observations
Resources ─────┘          │
                          ▼
                    Field Snapshot
                          │
                          ▼
                   Derived Metrics
```

Future AI Meteorology layers MAY consume Field Snapshots.

---

# 30. Field Snapshot as Sensor Output

A Field Snapshot should be understood as a sensor product.

It answers questions such as:

- How active was this Region?
- How many effective actions occurred?
- How many agents were active?
- How much authority was requested?
- How much authority was denied?
- How much observable resource usage occurred?
- How much traffic crossed boundaries?

It does NOT answer:

- Is the network dangerous?
- Is an agent malicious?
- Is a storm forming?
- Should authority be restricted?
- What will happen next?

Those questions belong to higher layers.

---

# 31. AI Meteorology Compatibility

v0.3 is the first version explicitly designed to feed a future AI Meteorology layer.

Possible mappings include:

```text
trace density
→ activity pressure

Receipt density
→ effective activity

authority request density
→ permission pressure

grant / deny ratio
→ authority friction

active agent density
→ actor concentration

resource usage
→ effective energy input

cross-region flow
→ network wind
```

These mappings are conceptual.

v0.3 does not define meteorological truth claims from them.

---

# 32. Observation Before Forecast

AI Zero Network follows this progression:

```text
v0.1
Existence

v0.2
Authority

v0.3
Observation

future
Interpretation

future
Prediction

future
Intervention
```

This ordering is intentional.

Prediction without stable observation creates false confidence.

Intervention without reliable observation creates unnecessary control.

Therefore:

> **Observation precedes interpretation.  
> Interpretation precedes prediction.  
> Prediction precedes intervention.**

---

# 33. Minimum v0.3 Conformance Requirements

An implementation claiming v0.3 field-observation conformance MUST:

### Requirement 1

Produce Field Snapshots tied to a defined Region.

### Requirement 2

Use bounded Observation Windows.

### Requirement 3

Keep raw observations distinguishable from derived indicators.

### Requirement 4

Derive raw metrics from observable records rather than undocumented estimates.

### Requirement 5

Prevent records outside the declared Region or time window from silently contaminating ordinary snapshot counts.

### Requirement 6

Represent count metrics as non-negative values.

### Requirement 7

Document any derived metric formula or normalization method used.

---

# 34. Recommended v0.3 Metrics

Minimum recommended observations:

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
resource_usage
incoming_trace_count
outgoing_trace_count
cross_region_trace_count
causal_edge_count
```

Optional derived indicators:

```text
activity_pressure
effective_pressure
authority_friction
```

---

# 35. v0.3 Failure Examples

The following behaviors are non-conforming.

## FAIL-FIELD-001 — Missing Region

```text
Field Snapshot has metrics
but no Region.
```

---

## FAIL-FIELD-002 — Invalid Window

```text
window_end <= window_start
```

---

## FAIL-FIELD-003 — Negative Observation

```text
trace_count = -1
```

---

## FAIL-FIELD-004 — Derived Metric Presented as Raw Fact

```text
observations.activity_pressure = 0.9
```

without clearly identifying it as derived.

---

## FAIL-FIELD-005 — Out-of-Window Record Counted

A record from:

```text
09:06
```

is included in a snapshot whose window ended at:

```text
09:05
```

without explicit late-arrival or revision semantics.

---

## FAIL-FIELD-006 — Undocumented Derived Formula

A snapshot reports:

```text
effective_pressure = 0.91
```

but provides no documented method or derivation identifier.

---

# 36. Data Minimization

Field Observation SHOULD aggregate rather than expose unnecessary event content.

For example, a collector generally needs:

```text
event type
region
timestamp
actor identifier
authority result
resource amount
```

rather than full message bodies or private reasoning.

The Field Layer SHOULD reduce visibility into individual content when aggregate observations are sufficient.

---

# 37. Privacy Boundary

Field-level observation MUST NOT require private chain-of-thought.

AI Zero Network continues to prefer externally observable state transitions.

The goal is:

> **Observe the atmosphere without reading every mind inside it.**

---

# 38. Minimum Field Law

AI Zero Network v0.3 can be reduced to four rules:

> **No field value without a Region.**  
> **No snapshot without a time window.**  
> **No observation without observable evidence.**  
> **No interpretation disguised as observation.**

---

# 39. AI Zero Network v0.3 Definition

AI Zero Network v0.1 asked:

> **Can an actor exist observably?**

v0.2 asked:

> **Can its authority be traced to a valid origin?**

v0.3 asks:

> **Can the collective state of many actors be observed as a field?**

The answer is expressed through:

```text
Region
+
Observation Window
+
Observable Records
+
Aggregation
+
Field Snapshot
```

In compact form:

> **Records become measurements.  
> Measurements become a field.**

This is the minimum Field Observation layer of AI Zero Network.
