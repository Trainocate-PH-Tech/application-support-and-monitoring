# Regex triage exercise

Investigate a fictional checkout incident using Bash, `cat` and GNU `grep`. Complete five independent searches and append their original matching log lines to a file named `{date}-evidence.txt`, for example `2026-10-21-evidence.txt`. Use the **UTC collection date**, which may differ from the incident date in the log.

Read [the primer](REGEX_PRIMER.md) first. The [answer key](REGEIX_EXERCISE_SOLUTION.md) is separate so you can attempt the questions without seeing the filters.

## Prepare the log and evidence file

Run this in your own practice directory. `>` replaces the sample log when you repeat this setup; `touch` preserves any existing evidence.

```bash
mkdir -p ~/support-lab/regex-triage
cd ~/support-lab/regex-triage
export LC_ALL=C
evidence="$(date -u +%F)-evidence.txt"
touch "$evidence"
cat > triage.log <<'EOF'
2026-10-21T10:14:59Z id=T01 level=ERROR env=prod service=checkout host=app-01 path=/checkout status=503 duration_ms=3000 client=203.0.113.8 request=req-700 code=UPSTREAM_TIMEOUT message="before incident window"
2026-10-21T10:15:00Z id=T02 level=ERROR env=prod service=checkout host=app-01 path=/checkout status=503 duration_ms=2000 client=203.0.113.8 request=req-701 code=UPSTREAM_TIMEOUT message="payment timeout"
2026-10-21T10:16:10Z id=T03 level=WARN env=prod service=checkout host=app-02 path=/health status=503 duration_ms=2400 client=10.0.0.1 request=req-702 code=PROBE_FAILED message="probe failed"
2026-10-21T10:17:00Z id=T04 level=WARN env=prod service=checkout host=app-02 path=/checkout status=504 duration_ms=10000 client=203.0.113.80 request=req-703 code=UPSTREAM_TIMEOUT message="payment timeout"
2026-10-21T10:18:00Z id=T05 level=ERROR env=staging service=checkout host=app-01 path=/checkout status=500 duration_ms=5000 client=203.0.113.8 request=req-704 code=DB_DEADLOCK message="deadlock"
2026-10-21T10:19:00Z id=T06 level=ERROR env=prod service=checkout host=app-03 path=/checkout status=502 duration_ms=1999 client=203.0.113.8 request=req-705 code=UPSTREAM_RESET message="connection reset"
2026-10-21T10:19:59Z id=T07 level=ERROR env=prod service=checkout host=app-01 path=/healthcheck status=500 duration_ms=9000 client=203.0.113.8 request=req-706 code=DB_DEADLOCK message="deadlock detected"
2026-10-21T10:20:00Z id=T08 level=ERROR env=prod service=checkout host=app-01 path=/checkout status=503 duration_ms=4000 client=203.0.113.8 request=req-707 code=UPSTREAM_TIMEOUT message="after incident window"
2026-10-21T10:20:10Z id=T09 level=INFO env=prod service=checkout host=app-01 path=/checkout status=200 duration_ms=120 client=203.0.113.8 request=req-701 code=OK message="retry recovered"
2026-10-21T10:16:20Z id=T10 level=ERROR env=prod service=auth host=auth-01 path=/login status=401 duration_ms=40 client=203.0.113.8 request=req-801 code=AUTH_FAILED message="invalid password"
2026-10-21T10:16:30Z id=T11 level=WARN env=prod service=auth host=auth-01 path=/login status=403 duration_ms=30 client=203.0.113.80 request=req-802 code=AUTH_FAILED message="account locked"
2026-10-21T10:17:10Z id=T12 level=WARN env=prod service=auth host=auth-01 path=/login status=403 duration_ms=35 client=203.0.113.8 request=req-803 code=AUTH_FAILED message="account locked"
2026-10-21T10:17:20Z id=T13 level=INFO env=prod service=auth host=auth-01 path=/login status=200 duration_ms=20 client=203.0.113.8 request=req-804 code=OK message="login succeeded"
2026-10-21T10:17:30Z id=T14 level=ERROR env=prod service=checkout host=app-02 path=/orders status=500 duration_ms=2500 client=198.51.100.4 request=req-7010 code=DB_DEADLOCK message="deadlock detected"
2026-10-21T10:18:10Z id=T15 level=ERROR env=prod service=worker host=worker-01 path=/jobs status=500 duration_ms=25000 client=10.0.0.2 request=req-901 code=DB_CONNECTION_REFUSED message="Connection Refused"
2026-10-21T10:18:20Z id=T16 level=ERROR env=prod service=worker host=worker-02 path=/jobs status=500 duration_ms=3000 client=10.0.0.3 request=req-902 code=DB_CONNECTION_REFUSED_RETRY message="retry pending"
2026-10-21T10:18:30Z id=T17 level=WARN env=prod service=checkout host=app-02 path=/checkout status=500 duration_ms=3500 client=198.51.100.4 request=req-903 code=DB_DEADLOCK message="retry scheduled"
2026-10-21T10:18:40Z id=T18 level=ERROR env=prod service=checkout host=app-02 path=/checkout status=500 duration_ms=3600 client=198.51.100.4 request=req-904 code=DB_DEADLOCK message="synthetic test event"
2026-10-21T10:18:50Z id=T19 level=ERRORISH env=prod service=checkout host=app-01 path=/checkout status=500 duration_ms=3000 client=203x0x113x8 request=req-905 code=DB_DEADLOCK message="malformed severity and client"
2026-10-21T10:19:10Z id=T20 level=ERROR env=prod service=checkout host=app-01 path=/checkout status=5000 duration_ms=3000 client=203.0.113.8 request=req-906 code=DB_DEADLOCK message="malformed status"
2026-10-21T10:19:20Z id=T21 level=ERROR env=prod service=checkout host=app-02 path=/checkout status=500 duration_ms=1500 client=198.51.100.4 request=req-907 code=DB_DEADLOCK message="retry exhausted"
2026-10-21T10:19:30Z id=T22 level=ERROR env=prod service=checkout host=app-02 path=/checkout status=500 duration_ms=2200 client=198.51.100.4 request=req-908 code=DB_DEADLOCK message="Synthetic Test event"
EOF
cat triage.log
```

The input is deliberately not globally time-sorted. Each event occupies one line; fields have the order shown and are separated by single spaces. The final `message` is quoted and contains no embedded quotes. Durations are nonnegative decimal integers without leading zeros. Some other fields deliberately contain malformed values.

## Evidence rules

- Start every search with `cat triage.log` and use `grep` filters. Do not select by `id`, hard-coded answer lists or line numbers.
- Preview each result, then run the same pipeline with `>> "$evidence"` at its end. `>>` appends; `>` would erase earlier evidence.
- Save whole original log lines, without line-number prefixes, context, headings or extracted tokens. Keep commands and interpretations in separate notes.
- Each question is independent. Include overlaps between questions; do not deduplicate the evidence file. Run each append once for a single submission. Repeating an append duplicates those results.
- For a fresh attempt, use a new directory and recreate `triage.log`; do not truncate earlier evidence.
- Q1, Q2 and Q4 use the inclusive incident window **2026-10-21 10:15:00–10:19:59 UTC**. Q3 and Q5 search the entire file.

## Five questions

### Q1 — Customer-facing checkout failures

During the incident window, collect production `checkout` events at exactly WARN or ERROR severity, from exactly `app-01` or `app-02`, with valid three-digit 5xx statuses. Exclude exactly `/health` and `/metrics`; `/healthcheck` must remain eligible. Exclude events whose message contains `synthetic test`, ignoring case. Append the evidence and report the number of matches.

### Q2 — Slow failures on the checkout endpoint

During the incident window, collect production `checkout` events on exactly `/checkout`, at exactly WARN or ERROR severity, with valid three-digit 5xx statuses and `duration_ms` **at least 2000**. Include values above 9999. Exclude messages containing `synthetic test`, ignoring case. Any host is eligible. Append the evidence and explain how you represented the numeric threshold.

### Q3 — Authentication failures from one client

Across the entire file, collect production `auth` events on exactly `/login` from exactly `203.0.113.8`, with status exactly 401 or 403 and code exactly `AUTH_FAILED`. Append the evidence. Explain why `.80` and addresses with arbitrary characters in place of dots must not match, and what these events do and do not establish about the client.

### Q4 — Database failure signals needing escalation

During the incident window, collect production events from either `checkout` or `worker`, at exactly ERROR severity, with valid three-digit 5xx statuses and code exactly `DB_DEADLOCK` or `DB_CONNECTION_REFUSED`. Exclude messages containing `retry scheduled` or `synthetic test`, ignoring case. Keep `retry exhausted`. Append the evidence and distinguish failure signals from proof of the incident's root cause.

### Q5 — Follow a request through recovery

Across the entire file, collect every production `checkout` event for exactly `req-701`, including any success after the incident window. Append the evidence. Explain the observed sequence and why `req-7010` must not appear. Do not inherit Q1's severity, status or time filters.

## Submit

Submit your `{date}-evidence.txt` plus separate notes containing the five pipelines, per-question counts, and requested explanations. Review the evidence with `cat "$evidence"`. Its records should preserve source order within each question's appended results; the combined file is grouped by question, not globally sorted by time.
