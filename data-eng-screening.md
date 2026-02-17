# 3 Data Engineering Screening Questions — Instant Rejection Tier

---

## Administration Guide

### Prepare Before the Call

1. **Role scope:** These questions are designed for data engineers working in batch ETL/ELT and warehouse-centric roles. For streaming-heavy or ML platform roles, supplement or substitute accordingly. *(Example streaming substitute for Q3: "Explain the difference between at-least-once and exactly-once delivery semantics. How does your system handle it, and what are the tradeoffs?")*

2. **Timing:** Allow approximately 5 minutes per question (15 minutes total).

3. **Order:** Ask them in sequence — Q1 (systems thinking) → Q2 (operational reasoning) → Q3 (design decision-making). They escalate in applied complexity.

4. **Concept over terminology:** Throughout this screen, evaluate candidates on demonstrated understanding, not vocabulary. A candidate who clearly describes a concept without using the standard industry term has met the bar. This applies to all three questions.

5. **Probe and reject protocol:** All Reject criteria assume the candidate has been given the follow-up probe if their initial answer was borderline. No candidate should be rejected without the opportunity to clarify through the probe.

### Reference During the Call

6. **Follow-up probing:** Let the candidate give their initial answer uninterrupted. If their response is borderline between Reject and Pass, ask the **one** suggested follow-up probe included with each question. If they still can't clear the Reject bar after the probe, that is your signal. Do not coach them toward the answer.

7. **Early termination:** If a candidate clearly falls into the 🔴 Reject tier on any question, you may end the screen. You do not need to ask all three.

8. **Note-taking:** For each question, record the tier (Reject / Pass / Strong) and write one sentence capturing the candidate's key point or most notable gap. This enables calibration discussions across interviewers and supports defensible hiring decisions.

---

## Question 1: "Walk me through what happens when you run a SQL query that joins two large tables — in whatever system you've used most. What's happening under the hood?"

**Why this works:** This is fundamental knowledge that any working data engineer encounters daily. It tests whether they actually understand the systems they use or are just writing declarative SQL without knowing what it triggers. Anchoring to their own system prevents penalizing people who work in managed/declarative environments while still demanding real systems-level thinking.

**Suggested follow-up probe (if borderline):** "If one table was very small and the other was very large, would the system handle that differently?"

### Scoring Rubric

**🔴 REJECT — Cannot describe any physical mechanism by which the system executes the join beyond logical row matching.**
- Says "it matches rows on the join key" and cannot go deeper
- No awareness that different join strategies or physical execution approaches exist
- Has never used `EXPLAIN`, query execution plans, or any equivalent — and doesn't know what they are
- Cannot describe any concept of how data moves, is distributed, or is organized to make the join possible

**🟡 PASS — Demonstrates working knowledge of at least one physical execution mechanism and shows awareness that systems make strategic choices.**
- Can describe at least one join strategy concretely (hash join, broadcast join, shuffle, sort-merge, nested loop) even if they only know the one relevant to their primary system
- Understands that the engine makes optimization decisions based on data size, statistics, or table structure
- Can reference execution plans as a tool they've used, even if they can't recite the full anatomy of one
- Mentions at least one of: data shuffling/redistribution, partitioning effects, or memory/resource implications

> **Minimum passing example:** *"In Spark, when you join two big tables it has to shuffle the data across the cluster so rows with the same join key end up on the same partition. If one table is small enough, it'll broadcast it to every node instead so you skip the shuffle. I've checked this in the Spark UI to see which plan it chose when joins were running slow."*
>
> *This is one example of a passing answer. Equivalent answers using different systems, tools, or terminology are equally valid.*

**🟢 STRONG — Demonstrates deep, cross-cutting systems understanding. Look for several of the following signals:**
- Explains multiple join strategies and articulates *when* the optimizer selects each one
- Distinguishes between logical plan and physical plan
- Discusses partition pruning, statistics collection, broadcast thresholds, or spill-to-disk behavior
- Can speak across systems (e.g., "In Spark this works differently than in Postgres because of distributed shuffling")
- References real debugging experiences — "I saw this go wrong when statistics were stale and the planner chose a nested loop on a 2B-row table"

---

## Question 2: "You have a pipeline that runs daily, and one day it re-processes data that was already loaded, creating duplicates in your target table. How do you detect this, fix it, and prevent it from happening again?"

**Why this works:** Idempotency and data quality are the bread and butter of pipeline engineering. This scenario-based question has three natural phases (detect → fix → prevent) that reveal increasing depth of experience. A data engineer who can't reason about duplicates has never owned a production pipeline.

**Suggested follow-up probe (if borderline):** "If you needed to fix the duplicates right now with a SQL query, how would you approach it?"

### Scoring Rubric

**🔴 REJECT — Cannot reason through any structured approach to detection, remediation, or prevention.**
- Has no strategy for detection beyond "someone would notice" or "check the dashboard"
- Cannot describe any deduplication technique — SQL or otherwise
- Does not understand what idempotency means (by name or concept) or why pipelines should produce the same result on re-runs
- Suggests "just don't run it twice" or "add a manual check" as a prevention strategy with no architectural safeguard
- Has never heard of or cannot describe upsert/merge patterns at any level

**🟡 PASS**

*Required — can address all three phases with at least one concrete technique each:*
- Detection: Proposes row count comparisons, duplicate checks on natural/composite keys, or data quality tests
- Fix: Describes at least one deduplication approach — `ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...)` with a delete/keep pattern, or a delete-and-reload strategy
- Prevention: Articulates a design principle — partition-based overwrites (`INSERT OVERWRITE`), merge/upsert patterns, or processing watermarks/checkpoints

*Additional Pass-tier signals that distinguish a high Pass from a low Pass:*
- Uses the word "idempotent" or clearly describes the concept without the label
- Considers who consumed the bad data downstream and whether they need to be notified or re-served

> **Minimum passing example:** *"First I'd check for duplicates by grouping on the natural key and looking for counts greater than one. To fix it, I'd use ROW_NUMBER partitioned by the key, ordered by load timestamp descending, and delete everything except row 1. To prevent it, I'd redesign the load step to use INSERT OVERWRITE on the date partition so re-runs replace data instead of appending. I'd also want to check if any downstream reports already picked up the duplicated data."*
>
> *This is one example of a passing answer. Equivalent answers using different systems, tools, or terminology are equally valid.*

**🟢 STRONG — Demonstrates battle-tested production thinking across the full incident lifecycle. Look for several of the following signals:**
- Frames detection proactively: data quality frameworks (dbt tests, Great Expectations, Monte Carlo), anomaly alerts on row counts or key uniqueness
- Discusses atomic load patterns — write to staging, validate, then swap/merge into target
- Proposes multiple prevention mechanisms and articulates tradeoffs between them (e.g., "upsert is safe but slower than partition overwrite; depends on volume and key stability")
- Thinks about root cause analysis — *why* did the pipeline re-process? Missing checkpoint? Upstream re-delivery? Scheduler retry?
- Mentions runbook creation or alerting improvements as part of "prevent" — treats it as a systems problem, not just a code fix

---

## Question 3: "You inherit a pipeline that does a full load of a 500-million-row table every night, and it's starting to time out. The business needs this data fresh every morning. Walk me through how you'd approach this."

**Why this works:** This scenario forces the candidate to demonstrate they understand both full and incremental loading approaches, can reason about tradeoffs, and can make a real architectural decision under constraints. It's extremely difficult to bluff through because the follow-up space is rich — any hand-waving about incremental loads immediately opens the door to probing on risk awareness.

**Suggested follow-up probe (if borderline):** "Let's say you switch to only loading changed records. Six months later, you discover your target table has quietly drifted — it has rows the source deleted and is missing some late-arriving records. What happened and how do you fix it?"

### Scoring Rubric

**🔴 REJECT — Cannot articulate the concept of loading only new or changed data, or cannot identify a single concrete risk of doing so.**
- Does not understand the concept of incremental loading, or describes it so vaguely that it's indistinguishable from full loading
- Proposes "just add more compute" or "increase the timeout" as the complete solution with no mention of changing the load strategy
- When probed about risks of only loading changes, cannot name even one (hard deletes missed, late-arriving data, unreliable change tracking)
- Cannot describe any mechanism for identifying changed rows at the source — no awareness of timestamp filtering, CDC, diff-based approaches, or log-based replication

**🟡 PASS — Correctly identifies loading only changed data as the primary strategy, articulates a concrete mechanism, and demonstrates awareness of at least one major risk.**
- Clearly explains the shift: "Stop reloading everything; only pull new or changed records since the last run"
- Proposes a concrete change-detection mechanism: filtering on a timestamp column, CDC, or partition-based extraction
- Identifies at least one specific risk: hard deletes being invisible to incremental pulls, late-arriving data falling outside the extraction window, or change-tracking columns not being reliably populated at the source
- Suggests at least one mitigation: periodic full-load reconciliation, overlap windows on the high-water mark, or soft-delete patterns
- May also consider intermediate options — partitioned loads, partial refreshes of recent date partitions only

> **Minimum passing example:** *"I'd move to an incremental load — only pull rows where updated_at is after the last successful run. That fixes the timeout since you're moving way less data. But you have to be careful: if the source hard-deletes rows, you'll never see those disappear from your target. And if updated_at isn't reliably set on every change, you'll miss records. I'd run a full reconciliation once a week to catch any drift."*
>
> *This is one example of a passing answer. Equivalent answers using different systems, tools, or terminology are equally valid.*

**🟢 STRONG — Treats this as a systems design problem, not just a load-strategy swap. Look for several of the following signals:**
- Asks clarifying questions before answering: What's the source system? Is CDC available? What does "fresh" actually mean — can we tolerate 1 hour of latency or must it be as-of-midnight?
- Proposes a phased approach: quick win (optimize the existing full load — partitioning, parallelism, compression) vs. long-term (migrate to incremental with guardrails)
- Articulates multiple risks with specificity: silent drift from missed hard deletes, unreliable watermark columns, schema evolution breaking extraction, late-arriving data creating gaps
- Designs defensive mechanisms: weekly reconciliation job that diffs source vs. target, data quality checks on expected row counts and key completeness, alerting on anomalous batch sizes
- References specific tools or patterns: CDC via Debezium or database log replication, merge statements for upsert, `INSERT OVERWRITE` on date partitions as a hybrid approach
- Considers the broader system: Does the warehouse support efficient merge? What's the cost model? Will incremental loads create small-file problems in a data lake?

---

## Usage Notes

These three questions form a **layered filter**: Q1 tests systems understanding, Q2 tests operational and production reasoning, Q3 tests applied design decision-making. A candidate with genuine hands-on experience will find all three approachable. Someone who has inflated their resume or operated purely at a surface level will fail to clear the Reject bar on at least one.

**Decision framework:**
- **Advance** the candidate to the next interview round if they achieve Pass or Strong on all three questions.
- **Do not advance** if any question results in a Reject. Each question is an independent gate.
- There is no composite scoring. A Strong on Q1 does not compensate for a Reject on Q3.

The three-tier rubric (Reject / Pass / Strong), the minimum passing examples, and the concept-over-terminology principle collectively ensure that interviewers can make confident, defensible, and calibrated decisions — including on partial answers.

---

## Quick Reference Card
*Print or keep open during the call. See full document for complete rubrics and minimum passing examples.*

| # | Question | Follow-Up Probe | 🔴 Reject If... |
|---|----------|-----------------|------------------|
| **1** | "Walk me through what happens when you join two large tables — in whatever system you've used most. What's happening under the hood?" | "If one table was very small and the other very large, would the system handle that differently?" | Cannot describe any physical execution mechanism beyond "it matches rows on the key." No awareness of join strategies, data movement, or execution plans. |
| **2** | "Your daily pipeline re-processes already-loaded data, creating duplicates. How do you detect, fix, and prevent this?" | "If you needed to fix the duplicates right now with SQL, how would you do it?" | Cannot describe any deduplication technique. No concept of idempotency. No architectural prevention strategy beyond "don't run it twice." |
| **3** | "You inherit a 500M-row full-load pipeline that's timing out nightly. The business needs fresh data every morning. What do you do?" | "You switch to loading only changes. Six months later the target has drifted — missing rows, ghost rows. What happened?" | Cannot articulate the concept of loading only changed data. Cannot name a single risk of doing so. No awareness of change-detection mechanisms. |

**Protocol:** 5 min/question → let them answer → one probe if borderline → do not coach → record tier + one sentence per question. Stop on any 🔴. Advance on all 🟡/🟢.