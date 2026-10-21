# Cross-Correlation Between Application and Database

[Hands-on exercise](APP_DB_CORRELATION_EXERCISE.md) · [Module 2](module2/README.md)

**Environment:** Ubuntu Bash for evidence analysis; optional access to an application's approved read-only health endpoint. No live application or database is required for the supplied scenarios. The existing course application does not implement connection pooling; pooled behavior below is explicitly synthetic.

## Section: Define user impact and establish the timeline

1. Record affected operation, users/reports impacted, start/end time, response codes, frequency, and whether writes may have succeeded despite a timeout.
2. Normalize timestamps to UTC while preserving original time zones. Record clock-skew uncertainty and capture windows.
3. Inspect the supplied evidence in Bash:

   ```bash
   cat shared/fixtures/db-topics/app-db/provenance.txt
   cat shared/fixtures/db-topics/app-db/context.txt
   cat shared/fixtures/db-topics/app-db/requests.tsv
   ```

4. These four requests are distinct scenarios, not a time-series trend. Two have status 504. That is 50% of this supplied sample, not a production error-rate estimate or count of unique affected users.

## Section: Join using explicit request and database-operation identifiers

1. Search one request using fixed-string matching:

   ```bash
   grep -Fn 'r101' shared/fixtures/db-topics/app-db/requests.tsv
   grep -Fn 'r101' shared/fixtures/db-topics/app-db/db.tsv
   ```

2. Verify both request ID and database-operation ID. A substring search is discovery, not an exact relational join; the utility uses exact TSV fields.
3. Request IDs are not automatically present in MySQL slow logs or SQL Server DMVs. Real correlation requires tracing/instrumentation, appropriately recorded session context, or other explicit identifiers. Pooled connections can serve many requests; one connection ID alone is not a permanent request mapping.
4. If only timestamps match, state the correlation as tentative. Do not join unrelated fixture directories.

## Section: Reconcile application latency and SQL duration

1. For each supplied request, calculate:

   ```text
   component_total_ms = pool_ms + sql_ms + downstream_ms + other_ms
   residual_ms = http_ms - component_total_ms
   ```

2. Fixture timings are sequential, nonoverlapping, and already include all attempts. Do not multiply `sql_ms` by `attempts` again.
3. Compare the four cases:

   | Request | HTTP ms | Main observed component | Next investigation |
   |---|---:|---|---|
   | r100 | 60 | SQL 35 ms; other 25 ms | Healthy comparator for this sample only |
   | r101 | 5000 | Pool wait 4000 ms; SQL 40 ms | Pool occupancy, waiters, connection hold duration |
   | r102 | 3000 | SQL 2800 ms | Query/plan/wait evidence for the matching operation |
   | r103 | 4500 | Downstream 4200 ms; SQL 40 ms | Dependency timeout and retry behavior |

4. All residuals are zero in these fixtures. In real traces, spans may nest or overlap; summing them can double-count. A residual is missing or mismatched measurement, not automatically network latency.

## Section: Investigate pool exhaustion and retries

1. For r101, read the accompanying pool snapshot: active 10, maximum 10, pending 8. Together with 4000 ms acquisition time, this supports pool contention at that instant.
2. Compare database connections/running work and application pool occupancy at the same time. MySQL `max_connections` is not an application pool's maximum size.
3. Investigate connection leaks, long-held transactions, downstream work while holding connections, and excessive concurrency. Fast SQL alone does not rule these out.
4. Count attempts separately from unique requests. Evaluate bounded backoff, timeout budgets, cancellation, and idempotency with the application owner. Do not automatically increase pool size or replay timed-out writes.

## Section: Check APIs and downstream dependencies safely

1. Inspect status, timeout phase, DNS/connect/TLS timing, and dependency spans before sending a new request.
2. For an explicitly approved read-only health URL, run once from the affected application network:

   ```bash
   read -r -p 'Approved read-only health URL: ' HEALTH_URL
   curl --silent --show-error --output /dev/null \
     --connect-timeout 3 --max-time 10 \
     --write-out 'http=%{http_code} dns_s=%{time_namelookup} connect_s=%{time_connect} tls_s=%{time_appconnect} first_byte_s=%{time_starttransfer} total_s=%{time_total}\n' \
     "$HEALTH_URL"
   curl_rc=$?
   printf 'curl exit=%s\n' "$curl_rc"
   ```

3. Capture both exit code and HTTP status. Curl can exit 0 for HTTP errors without a fail option. The timing fields are cumulative milestones, not components to add. Avoid `-k`, credentials in URLs, write endpoints, and retry loops.
4. A successful health endpoint does not prove the checkout dependency or business operation is healthy. No response or restricted access is unavailable evidence, not fabricated timing.

## Section: Correlate deployment and summarize evidence

1. Put deployment markers alongside request and database observations. Release A7 precedes these fixtures, but no release diff or mechanism proves causation.
2. Separate facts, hypotheses, missing measurements, and proposed next checks. Name the owning application/database/dependency team for each action.
3. Report request-level impact and timing units, retry scope, exact versus tentative joins, clock uncertainty, and instrumentation gaps.
4. Continue with the [exercise](APP_DB_CORRELATION_EXERCISE.md) to build an offline Bash reconciliation utility and test missing matches.
