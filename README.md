# python-screens - interview rubric for data engineering candidates

## 001-003 - basic checks to use during screening

## 004 - live coding exercise, 45-60mins

Event normalisation task. Candidate implements `normalise_events()` to clean and standardise messy, inconsistently-shaped event data. Tests are provided.

### Follow-up questions

Use 1-2 of these after the coding portion. Pick based on how the candidate did — if they finished cleanly, lean toward #2 or #3. If they struggled but showed good instincts, #4 works well because it doesn't penalise slow coding.

---

#### 1. "How would you test this more thoroughly?"

**What you're probing:** Quality instincts, edge case thinking.

| Level | What to look for |
|-------|-----------------|
| **Weak** | "Add more unit tests" with no specifics. Repeats variations of the existing tests without identifying gaps. |
| **Mid** | Identifies concrete edge cases: `None`/empty strings in every field, unknown currencies, malformed timestamps, duplicate `event_id`s, numeric strings vs actual numbers. Might mention testing with an empty input list or a single-element list. |
| **Strong** | All of the above, plus: mentions property-based testing (e.g. Hypothesis) to fuzz random schemas. Distinguishes between testing the normaliser itself vs testing downstream assumptions. Talks about contract tests against the upstream schema. May raise the question of what "correct" means when the spec is ambiguous — e.g. should an unknown currency raise, return `None`, or be logged and skipped? |

---

#### 2. "This works for 6 events. What breaks at 100M events per day?"

**What you're probing:** Scale intuition, batch vs stream thinking.

| Level | What to look for |
|-------|-----------------|
| **Weak** | "Use Spark" or "use a bigger machine" with no elaboration. No awareness of what specifically breaks or why. |
| **Mid** | Identifies memory as the first bottleneck (can't hold all events in a list). Suggests chunked/streaming processing. Mentions partitioning by time or user. Aware that the FX dict would need to come from an external source. May mention parallelism but stays vague on implementation. |
| **Strong** | Thinks about the problem end-to-end before proposing solutions. Asks about latency requirements (batch vs real-time). Discusses specific trade-offs: Spark/Flink/Beam for distributed processing, partitioning strategy (by event time vs ingestion time), backpressure handling, late-arriving data and watermarks, idempotency if events get replayed. Questions whether Python is still the right choice at this scale. May mention schema registry to avoid parsing surprises at volume. |

---

#### 3. "The source team keeps adding new field variants and currencies. How do you make this sustainable?"

**What you're probing:** System design, maintainability, cross-team thinking.

| Level | What to look for |
|-------|-----------------|
| **Weak** | "Add more if/else branches." Treats it purely as a code problem. No consideration of the organisational or operational side. |
| **Mid** | Suggests config-driven field mappings instead of hardcoded logic (e.g. a YAML/JSON mapping of source field names to canonical names). Moves FX rates to an external lookup (API, database, config file) instead of a static dict. Adds logging for unmapped fields so new variants are detected. |
| **Strong** | All of the above, plus: pushes the conversation upstream — advocates for a schema registry or contract between the source team and the pipeline so new fields are declared, not discovered. Discusses alerting/monitoring on unknown fields or unmapped currencies rather than silent failure. Recognises this is fundamentally an organisational problem (who owns the schema?) not just a technical one. May mention versioned schemas, backward/forward compatibility, or a dead-letter queue for events that fail normalisation. |

---

#### 4. "An analyst reports that revenue numbers look wrong for last Tuesday. Walk me through how you'd debug this in production."

**What you're probing:** Operational maturity, incident response instincts.

| Level | What to look for |
|-------|-----------------|
| **Weak** | Jumps straight to reading code. "I'd look at the normalise function." No structured approach, no mention of data checks or observability. |
| **Mid** | Has a systematic approach: check pipeline run logs for errors, compare row counts at each stage (ingestion, transformation, serving), look at whether the issue is missing data vs wrong values. Checks FX rates for that day. Looks at whether specific event types or currencies are affected. Knows to check for duplicates and late-arriving events. |
| **Strong** | All of the above, plus: starts by scoping the problem (how wrong? which products/users/regions? just Tuesday or a trend?). Uses data lineage to trace values back to source. Compares against source-of-truth totals for reconciliation. After finding the root cause, talks about prevention: data quality checks (e.g. Great Expectations), anomaly detection on output metrics, automated reconciliation against upstream totals, and alerting thresholds. May mention runbooks, incident timelines, and blameless postmortems as part of the response process. |
