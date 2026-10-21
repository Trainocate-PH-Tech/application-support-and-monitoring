# Database triage
- Engine/version, endpoint, database, UTC window and access role:
- Impact and application request IDs:
- Connectivity, service and connection count evidence:

| Query/session | Frequency | Duration / CPU / reads (units) | Lock/blocking evidence | Plan evidence | Next action |
|---|---|---|---|---|---|

## MySQL
Slow-query frequency versus total time; rows examined versus returned; deadlock victim and survivor; replica freshness and unknowns.

## SQL Server
Wait deltas; head blocker including sleeping sessions; Query Store interval/plan comparisons; SQL Agent job and step outcome.

## Decision
Facts, alternatives, probable cause, mitigation, rollback, recovery checks and escalation request.
