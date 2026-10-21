# Regex triage exercise — solutions

Answer key for [REGEX_EXERCISE.md](REGEX_EXERCISE.md). The filename `REGEIX_EXERCISE_SOLUTION.md` intentionally follows the requested spelling.

Create `triage.log` using the exercise setup first. Use the same Bash session and `evidence` variable from that setup. If reopening a session, change to your exercise directory and run:

```bash
export LC_ALL=C
evidence="$(date -u +%F)-evidence.txt"
touch "$evidence"
```

This selects today's UTC evidence file. If continuing a collection from an earlier UTC date, set `evidence` to that original filename instead. All commands below append with `>>`; preview by running the pipeline without its final redirection. Execute each append once. IDs below are checks, not selection criteria.

## Q1 — Customer-facing checkout failures

```bash
cat triage.log |
  grep -E '^2026-10-21T10:1[5-9]:[0-5][0-9]Z ' |
  grep -E '(^| )env=prod( |$)' |
  grep -E '(^| )service=checkout( |$)' |
  grep -E '(^| )level=(WARN|ERROR)( |$)' |
  grep -E '(^| )host=app-0[12]( |$)' |
  grep -E '(^| )status=5[0-9]{2}( |$)' |
  grep -Ev '(^| )path=/(health|metrics)( |$)' |
  grep -Eiv '(^| )message="[^"]*synthetic test[^"]*"$' >> "$evidence"
```

Expected **6 lines: T02, T04, T07, T14, T17, T21**. T07's `/healthcheck` is eligible. T06 has the wrong host; T19 has the wrong severity; T20 has an invalid four-digit status. Both capitalization variants of the synthetic message are excluded.

## Q2 — Slow failures on the checkout endpoint

```bash
cat triage.log |
  grep -E '^2026-10-21T10:1[5-9]:[0-5][0-9]Z ' |
  grep -E '(^| )env=prod( |$)' |
  grep -E '(^| )service=checkout( |$)' |
  grep -E '(^| )path=/checkout( |$)' |
  grep -E '(^| )level=(WARN|ERROR)( |$)' |
  grep -E '(^| )status=5[0-9]{2}( |$)' |
  grep -E '(^| )duration_ms=([2-9][0-9]{3}|[1-9][0-9]{4,})( |$)' |
  grep -Eiv '(^| )message="[^"]*synthetic test[^"]*"$' >> "$evidence"
```

Expected **3 lines: T02, T04, T17**. `[2-9][0-9]{3}` covers 2000–9999; `[1-9][0-9]{4,}` covers all integers of at least five digits. The field boundary prevents matching a prefix of a value. This relies on the fixture's unsigned integer format without leading zeros. T06 is 1999 ms, T21 is 1500 ms, and T14 has a different path.

## Q3 — Authentication failures from one client

```bash
cat triage.log |
  grep -E '(^| )env=prod( |$)' |
  grep -E '(^| )service=auth( |$)' |
  grep -E '(^| )path=/login( |$)' |
  grep -E '(^| )client=203\.0\.113\.8( |$)' |
  grep -E '(^| )status=(401|403)( |$)' |
  grep -E '(^| )code=AUTH_FAILED( |$)' >> "$evidence"
```

Expected **2 lines: T10, T12**. Escaping each dot prevents wildcard matching; the ending boundary excludes `.80`. The lines establish two logged authentication failures attributed to this client address. They do not identify a person or establish a malicious attack; proxies or shared addresses may affect attribution. T13 is a success and is outside the requested failure evidence.

## Q4 — Database failure signals needing escalation

```bash
cat triage.log |
  grep -E '^2026-10-21T10:1[5-9]:[0-5][0-9]Z ' |
  grep -E '(^| )env=prod( |$)' |
  grep -E '(^| )service=(checkout|worker)( |$)' |
  grep -E '(^| )level=ERROR( |$)' |
  grep -E '(^| )status=5[0-9]{2}( |$)' |
  grep -E '(^| )code=(DB_DEADLOCK|DB_CONNECTION_REFUSED)( |$)' |
  grep -Eiv '(^| )message="[^"]*(retry scheduled|synthetic test)[^"]*"$' >> "$evidence"
```

Expected **4 lines: T07, T14, T15, T21**. The code boundary rejects T16's `_RETRY` suffix. The message exclusion is case-insensitive and retains `retry exhausted`. These are application-reported database failure signals. Correlate with database and network evidence before concluding which failure caused the checkout incident.

## Q5 — Follow a request through recovery

```bash
cat triage.log |
  grep -E '(^| )env=prod( |$)' |
  grep -E '(^| )service=checkout( |$)' |
  grep -E '(^| )request=req-701( |$)' >> "$evidence"
```

Expected **2 lines: T02, T09**. The request logged a 503 at 10:15:00 UTC and a 200 with `retry recovered` at 10:20:10 UTC, 5 minutes 10 seconds later. The boundary excludes `req-7010`. The later success supports recovery for this request only; it does not demonstrate system-wide recovery. `grep` preserves file order, so verify timestamps when interpreting unsorted logs.

## Verify your saved evidence

After running Q1 through Q5 exactly once into a previously empty evidence file:

```bash
cat "$evidence"
cat "$evidence" | grep -c '^2026-10-21T'
cat "$evidence" | grep -Eo 'id=T[0-9]{2}( |$)'
```

Expected total: **17 lines**. Expected ID order, grouped here by append operation:

```text
Q1: T02 T04 T07 T14 T17 T21
Q2: T02 T04 T17
Q3: T10 T12
Q4: T07 T14 T15 T21
Q5: T02 T09
```

The actual evidence file contains only the original log lines, not these labels. Repeated IDs across questions are intentional. Existing evidence or repeated appends increase the total. To check an individual question's count without appending again, rerun that question's pipeline without the redirection and add `| grep -c '^'`.
