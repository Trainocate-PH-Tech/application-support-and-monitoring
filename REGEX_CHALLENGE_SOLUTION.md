# Live log regex challenge solution

Run the generator in one terminal, then start this command in another at the instructor's signal:

```bash
export LC_ALL=C
tail -n 0 -f generator.log | grep --line-buffered -E '^2026-10-21T10:1[5-9]:[0-5][0-9]Z id=[^ ]+ level=(WARN|ERROR) env=prod service=checkout host=app-0[12] path=/checkout status=5[0-9]{2} duration_ms=([2-9][0-9]{3}|[1-9][0-9]{4}[0-9]*) client=203\.0\.113\.8 request=[^ ]+ code=(UPSTREAM_TIMEOUT|DB_DEADLOCK) message="(payment timeout|deadlock detected|retry exhausted)"$' >> challenge-evidence.txt
```

Press Ctrl+C when time expires, then count the collected lines:

```bash
cat challenge-evidence.txt | grep -c '^'
```

The anchors require a complete space-separated record, excluding the other formats. Literal spaces enforce field boundaries, rejecting values such as `ERRORISH`, `app-010`, `5000`, and `DB_DEADLOCK_RETRY`. Escaped periods and the following space require the exact client address, excluding `.80` and arbitrary characters in place of dots.

`1[5-9]:[0-5][0-9]` covers minutes 15–19 and seconds 00–59. `[2-9][0-9]{3}` covers 2000–9999; `[1-9][0-9]{4}[0-9]*` covers all integers of five or more digits without leading zeros. The message alternatives match only the three permitted complete messages.

This combines the incident-window, exact-field, status, and duration techniques from the exercise and its linked primer. The seeded sequence repeats, but a live attempt has no fixed answer count: collection timing and the instructor's limit determine the total. For fair comparisons, use the same seed, interval, and coordinated fresh start for each learner.
