# Case D — Reporting regression

Independent Module 2 assessment. All data below is synthetic and belongs to this case only. Do not join unrelated course fixtures into this incident. Do not modify the live class database.

## Briefing

At 02:05 UTC a report becomes slow after release R18. Player lookup remains responsive. The report returns the same 1,000 rows. Operators suggest a lock, increased traffic or a changed query plan. Evaluate at least two explanations before requesting a change.

## Captured evidence

Both intervals are 60 seconds, for the same report and parameter value. The supplied durations are averages, not percentiles.

| Measure | 01:59 UTC baseline | 02:05 UTC incident |
|---|---:|---:|
| Executions | 100 | 100 |
| Rows returned per call | 1,000 | 1,000 |
| Average duration, ms | 60 | 900 |
| Average logical reads | 220 | 21,000 |
| Average CPU, ms | 25 | 510 |
| Plan identifier | 3 | 8 |
| Player lookup average, ms | 30 | 32 |

Three request snapshots at 02:05:10, :20 and :30 show the reporting query executing, blocking_session_id=0 and no active lock wait. These samples do not cover the entire interval. Synthetic plan summaries: plan 3 uses a keyed lookup; plan 8 scans a larger input. Actual plan XML, statistics timestamps and the release SQL diff have not yet been supplied. No database authentication errors appear in this captured window.

## Required work

1. Compute duration and read amplification, and compare execution counts.
2. Rank two plausible causes. State what the sampled absence of blocking can and cannot prove.
3. Request additional evidence that distinguishes plan choice, changed predicates and statistics. State the expected finding for each hypothesis before requesting it.
4. Propose one reversible change, its scope, owner and rollback trigger. Do not assume a new index is the only solution.
5. Ask the instructor for a post-change capture after recording your proposal. Compare the same workload and results; distinguish demonstrated improvement from proof of the underlying cause.
6. Submit your database worksheet and an automation outline with bounded checks and explicit unknown states. Each learner explains one calculation and one rejected hypothesis independently.

Optional hints are in the exercise. Instructor release cards are deliberately absent from the student package.
