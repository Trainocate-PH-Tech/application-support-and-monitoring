# Assessment rubric

Team score: 100 points. Pass: 70, with evidence, the required script (or Module 2 design) and recovery verification present. Unscoped destructive actions require remediation regardless of total. Optional extensions do not replace core outputs.

| Criterion | Missing: 0 | Partial | Full credit |
|---|---|---|---|
| Evidence: 25 | No usable observations | 12: relevant outputs but missing UTC, provenance or limitations | 25: relevant, timestamped, attributed, reviewed evidence with IDs and limitations |
| Diagnosis: 25 | Guess without evidence | 12: plausible layer but alternatives untested | 25: supported explanation, competing hypothesis tested, uncertainty explicit |
| Recovery: 20 | No scoped action or verification | 10: reasonable action but weak rollback or business check | 20: minimal scoped action, rollback, comparable business verification |
| Automation: 20 | No runnable script/design | 10: happy path works; adverse cases untested | 20: bounded checks, quoted data, documented statuses and adverse-case results |
| Communication: 10 | No usable handover | 5: timeline or ownership incomplete | 10: impact, facts, ownership, timeline and actionable handover |

Use the nearest anchor and explain the evidence supporting it. Module 1 requires the evidence collector; Module 2 requires a database-check design; Module 3 requires executable automation. A simulated recovery must be labeled synthetic.

## Individual check

Each learner must run or explain one permitted diagnostic command, interpret one observation and explain one verification or rollback choice. Record each as demonstrated or needs remediation. A team pass does not replace an individual's outstanding remediation; repeat the relevant task after feedback.

## Hint record

Record 0 (independent), 1 (question narrowing), 2 (interpretation prompt), or 3 (directed reference). Do not subtract automatic points for seeking help. Report assisted and independent performance separately; use a fresh individual prompt to check transfer.

## Worked scoring example — unrelated practice incident

A team captures a synthetic endpoint timeout with UTC and request ID, records the affected route and proposes a bounded dependency check. It verifies the route after a simulated correction but omits rollback. Its script works only on the healthy case. The handover names an owner and next update; the team has not tested an alternative cause.

Evidence 25 + diagnosis 12 + recovery 10 + automation 10 + communication 10 = **67/100**. Feedback: test one alternative, add rollback, and run adverse-case script tests. This example demonstrates scoring; it is not an answer to a final incident.
