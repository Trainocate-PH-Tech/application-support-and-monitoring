# Concealed incident cards and answer key

Give students only the briefing, impact and requested outputs. Keep inject/reset commands with the instructor. Synthetic timestamps are UTC and do not describe actual customer incidents.

## A — Casino loyalty outage

Briefing: “Player lookup returns errors after a configuration change. MySQL is reported running. Confirm impact and restore service.” Inject `sudo shared/scripts/fault.sh db-auth`. Expected: service active, TCP 3306 reachable, /live healthy, /health and /player 503; journal SQLState indicates authentication failure. Learners should inspect configuration ownership/change context without dumping the password. Mitigate using reset, then verify health plus three player lookups. Decoy: an old CPU spike from before the incident is not causal.

## B — Online gaming transaction delay

Briefing: “Customer-facing requests take about 1.5 seconds; the report query has a missing index. Which observation explains the current request delay?” Inject `latency`. The app introduces 1500 ms after connection; MySQL itself need not be slow. Students correlate low SQL execution time in supplied evidence with high app duration and avoid claiming the report index is the sole cause. Reset, compare five bounded requests before/after. Use pool-exhaustion evidence as a separate hypothesis exercise, not as a feature of this app.

## C — Payment integration failure

Briefing: “Payment readiness fails while basic loyalty lookup works. The generic health endpoint is green.” Inject `payment`. /payment returns 502 and /health remains 200. The payment route is a simulator with no external financial service. Reset and verify payment plus player lookup. Recommendation: monitor dependency/business functions, not only generic readiness.

## Module 1 final

Select `startup`, `permissions` or `db-auth`. Score evidence-first triage, correct layer, minimal repair and verification. Do not reveal the fault name in student instructions. Reset between teams.

## Module 2 final

Use case D below: an independent synthetic report-performance regression. Release additional and post-change evidence only after the team records its reasoning. No live fault is required. Lock exercises remain separate, with bounded transactions and explicit rollback.

## Timed updates

Use: “At [UTC], [affected business function] affects [known scope]. Confirmed: [facts]. We are testing [hypothesis/action] owned by [role]. Mitigation status: [status]. Next update: [UTC].” No invented customer counts. At recovery, include the checks and observation interval.

## Shared assessment rubric (100 points)

| Criterion | Points | Full-credit behavior |
|---|---:|---|
| Evidence quality | 25 | UTC, provenance, relevant outputs, IDs, limitations, redaction |
| Diagnosis | 25 | Correct layer, alternatives tested, no unsupported certainty |
| Mitigation/recovery | 20 | Minimal scoped change, rollback, business verification |
| Automation | 20 | Runnable scripts, timeouts, quoted paths, statuses, adverse-case tests |
| Communication | 10 | Impact, ownership, timeline, clear handover |

Pass at 70/100 with evidence, runnable core script and recovery verification present. Unscoped destructive actions require remediation regardless of total. For Module 2, grade the health-check outline under automation; Module 3 requires executable scripts. Optional extensions can demonstrate mastery but do not replace required outputs.

## Case D — Module 2 replacement assessment

Use `shared/fixtures/database-incident.md` instead of injecting db-auth. Keep all case captures separate from unrelated fixtures and the live class database. First collect each team's timestamped pre-change reasoning.

Expected reasoning: 15× average duration, approximately 95.45× logical reads, unchanged execution rate and result count. The sample supports increased per-call database work. Three nonblocking snapshots reduce confidence in a persistent lock explanation but do not prove the absence of intermittent blocking. Plan change alone does not prove a particular repair.

Release this additional synthetic evidence only when a team requests a discriminating observation: R18 wrapped the indexed lookup column in a conversion; the statistics timestamp and parameter value were unchanged. The captured old/new query results match on this training dataset. A scoped rollback of that predicate change is a defensible proposal; discuss parameter types, broader semantic equivalence and rollout ownership before generalizing.

After a written remediation and rollback proposal, release: **02:12 UTC**, same parameter and 60-second interval, executions 100, rows/call 1,000, average duration 65 ms, average reads 230, CPU 27 ms, plan 3, player lookup 31 ms. This is a synthetic post-change capture, not proof of a live repair. Compare to both baseline and incident; require a statement about sampling limits and result equivalence. A change with a different rationale needs further evidence, not an invented successful outcome.

For individual review, ask each learner to calculate one amplification factor and describe one observation that could falsify the leading diagnosis. Hint use is recorded separately from correctness.

## Scoring anchors

Use the learner-visible [assessment rubric](../assessment-rubric.md). Preserve pre-hint work; record hint level and individual checks separately from the team score.
