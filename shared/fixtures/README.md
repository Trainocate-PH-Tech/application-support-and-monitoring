# Synthetic evidence fixtures
All records in this folder are authored teaching data, not logs collected from customers or the EC2 server. Times are UTC. Do not infer that separate files represent one actual incident unless an exercise explicitly joins them.

- application.log: six valid requests and one malformed row; HTTP status and latency are explicit fields.
- mysql-slow.log: four query executions; mysqldumpslow groups the three similar report queries.
- replication.json: stopped SQL applier despite a running receiver.
- sqlserver-waits.csv: two cumulative captures, 60 seconds apart; compute deltas.
- query-store.csv: two comparable synthetic intervals; duration/CPU are microseconds.
- job-history.csv: a failed step and aggregate job result; a different failure from the live intentional-THROW job.
- correlation.csv: synthetic pooled application, unlike the simple live app.
- platform-incidents.md: DNS/TLS/SELinux/IIS and high-CPU evidence cards.
- support-fixtures.tar.gz: starter files for Linux command practice; no executable payloads.
