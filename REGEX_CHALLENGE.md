# Live log regex challenge

## Setup

Run `python log_generator.py` from this directory. It prints `Running application...` and appends continuously to `generator.log` until you press Ctrl+C. Python 3 and GNU `grep` are required; no Python packages are needed.

Change `SEED = 42` in the script to choose another reproducible sequence. `INTERVAL_SECONDS` controls the delay between lines (default: 0.1 seconds). Timestamps are simulated incident times, not the current clock. Each run restarts the seeded sequence and IDs, but appends to the existing file. For a fresh attempt, stop the generator and move the previous log and evidence file aside before restarting.

In a second terminal in the same directory, replace `EXPRESSION` with your single extended regular expression:

```bash
export LC_ALL=C
tail -n 0 -f generator.log | grep --line-buffered -E 'EXPRESSION' >> challenge-evidence.txt
```

`tail -n 0` collects only new arrivals. To also show matches on screen, omit the redirection during practice. `--line-buffered` makes redirected matches available immediately; it does not change regex syntax. Start collecting when the instructor starts the timer and press Ctrl+C in this terminal when the instructor ends it. Stop the generator separately afterward.

The stream mixes space-separated key/value records, JSON, pipe-separated records, and plain text. Only space-separated key/value records are eligible. Those records have this exact field order, single spaces, and a final quoted message with no embedded quotes:

```text
TIMESTAMP id=ID level=LEVEL env=ENV service=SERVICE host=HOST path=PATH status=STATUS duration_ms=DURATION client=CLIENT request=REQUEST code=CODE message="MESSAGE"
```

Durations are nonnegative decimal integers without leading zeros. Other fields may contain deliberate near-matches or malformed values.

## The question

**Using one `grep -E` regular expression and the techniques from [REGEX_EXERCISE.md](REGEX_EXERCISE.md) and its linked primer, how many correct original log lines can you collect within the time limit set by the instructor that satisfy every condition below?**

- Timestamp is within **2026-10-21 10:15:00–10:19:59 UTC**, inclusive.
- Environment is exactly `prod`, service exactly `checkout`, and severity exactly `WARN` or `ERROR`.
- Host is exactly `app-01` or `app-02`, and path exactly `/checkout`.
- Status is a valid three-digit 5xx value, and `duration_ms` is **at least 2000**, including values above 9999.
- Client is exactly `203.0.113.8`.
- Code is exactly `UPSTREAM_TIMEOUT` or `DB_DEADLOCK`.
- Message is exactly one of `payment timeout`, `deadlock detected`, or `retry exhausted` (case-sensitive).

Match the entire record. Accept any nonempty ID and request token without spaces; do not filter by particular IDs or request numbers. Use only the taught anchors, literals, escaped periods, character classes, grouping, alternatives, and repetition. No lookarounds, PCRE, or extra filtering commands.

Submit your expression and `challenge-evidence.txt`. Count saved lines with `cat challenge-evidence.txt | grep -c '^'`. The score is the number of qualifying lines collected during the timed attempt; false positives and duplicate submissions of the same captured event do not count. Expected totals depend on the instructor's time limit and when collection starts.
