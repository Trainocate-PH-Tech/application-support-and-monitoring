# Okada assessment fixtures

Entirely fictional teaching evidence; not Okada operational records or captures from the student server. All timestamps are UTC (Asia/Manila is UTC+08:00). Files are static and must not be modified.

Read application.log.1 before application.log. Each has 360 lines; the combined stream is chronological, with one original event per line. JSON and pipe-separated decoys are ineligible. payments.log is used for exact request correlation, not chronological ordering.

baseline-slow.log and detail-slow.log represent two completed runs of the same six report SELECTs, one SLEEP probe, and one player-count query. The session long_query_time was 1.0 seconds in baseline and 0.1 seconds in detail. No index or business result changed between these fictional captures. Every statement occupies one line; each record has one timing header. The six business statements are marked /* loyalty_statement */. Rows_examined values are fixed synthetic evidence, not optimizer estimates or a prediction for the live host.

The baseline report count can be zero without implying that the reports did not execute. The 8-second SLEEP probe is deliberately slow and cannot be fixed by a transaction index.
