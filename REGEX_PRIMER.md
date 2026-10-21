# Regex with `grep` in Linux

A regular expression (regex) describes a text pattern. `grep` reads input one line at a time and prints each whole line containing a match. It does not interpret a log's fields or understand incidents: your pattern supplies those rules.

These examples use Bash and GNU `grep` on Linux, with fictional logs. Start in a learner-owned directory:

```bash
mkdir -p ~/support-lab/regex
cd ~/support-lab/regex
export LC_ALL=C
```

`LC_ALL=C` gives predictable ASCII ranges and character classes for these examples.

## How a pipeline works

```bash
cat primer.log | grep -E 'level=ERROR( |$)'
```

`cat` writes the file to standard output; `|` sends that output to `grep` as standard input. `-E` enables extended regular expressions (ERE). Single quotes keep the shell from interpreting regex characters. The pattern finds `level=ERROR` followed by a space or the end of the line, avoiding `level=ERRORISH`.

For this practice, use `cat ... | grep ...`. In everyday work, `grep -E 'level=ERROR( |$)' primer.log` gives the same matching lines without needing `cat`.

## Patterns you need

| Syntax in `grep -E` | Meaning | Example |
|---|---|---|
| `ERROR` | Literal text anywhere in a line | Also matches `ERRORISH` |
| `^` / `$` | Beginning / end of line | `^2026-10-21T` |
| `.` | Any single character | `a.b` matches `a-b` and `a.b` |
| `\.` | A literal period | `10\.20\.0\.5` |
| `[0-9]` | One digit | `status=5[0-9][0-9]` |
| `[^ ]` | One character other than a space | `request=[^ ]+` |
| `[[:space:]]` | A whitespace character | A space, tab, etc. |
| `*` | Zero or more of the preceding item | `ab*` matches `a`, `ab`, `abb` |
| `+` | One or more of the preceding item | `[0-9]+` |
| `?` | Zero or one of the preceding item | `retries=0?1` matches `1` or `01` |
| `{n}` / `{n,m}` | Exactly n / n through m repetitions | `[0-9]{3}` |
| `(a|b)` | Grouping and alternatives | `level=(WARN|ERROR)` |
| `.*` | Any sequence of characters, including none | `level=ERROR.*status=500` |

The `^` inside `[^ ]` negates the character class; outside a class, it anchors the start of the line. A wildcard in a shell filename such as `*.log` is a different language: regex `*` repeats the item before it.

## Modes and useful flags

| Command or flag | Behavior |
|---|---|
| `grep 'pattern'` | Basic regex (BRE); grouping, alternation and some repetition syntax differ from ERE |
| `grep -E 'pattern'` | Extended regex; use this for the exercises |
| `grep -F 'text'` | Fixed strings: periods, brackets and other characters are literal |
| `-i` | Ignore letter case |
| `-v` | Print lines that do **not** match |
| `-n` | Prefix matches with input line numbers |
| `-c` | Count matching lines, not occurrences |
| `-o` | Print only matching portions rather than entire lines |
| `-A 2`, `-B 2`, `-C 2` | Include two lines after, before, or on both sides of matches |
| `-e 'first' -e 'second'` | Match either pattern (OR) |

Do not mix BRE and ERE syntax. For example, ERE uses `(WARN|ERROR)`; GNU BRE uses `\(WARN\|ERROR\)`. Use `grep -F` when you want literal text, not regex.

### AND, OR and exclusions

```bash
# AND: both fields must occur on the same line, in either order.
cat primer.log | grep -E '(^| )service=api( |$)' | grep -E '(^| )level=ERROR( |$)'

# OR: either severity.
cat primer.log | grep -E '(^| )level=(WARN|ERROR)( |$)'

# Exclude exactly the health path, not /healthcheck.
cat primer.log | grep -Ev '(^| )path=/health( |$)'
```

`a.*b` requires `a` before `b`. Chained filters express AND without requiring field order. These fixtures use single spaces, so `(^| )` and `( |$)` mark field boundaries. For logs with tabs or variable whitespace, use `(^|[[:space:]])` and `([[:space:]]|$)` instead. `grep -w` uses word boundaries, which are not equivalent to log-field boundaries around punctuation.

Regex matches text, not numbers: `duration_ms=[2-9][0-9]{3}` matches 2000–9999, but misses 10000. Numeric conditions need careful digit patterns or a numeric tool such as `awk` for general production data. `grep -E` does not support lookahead; use another filter with `-v` for exclusions.

`grep` exits with 0 for a match, 1 for no match, and 2 for an error. In Bash, a pipeline normally reports the last command's status; `set -o pipefail` also exposes earlier failures. An empty result is not automatically a broken command. Context lines from `-C` may not match the filter; avoid context flags when saving matching evidence only.

## Create the practice log

Paste this entire block. The quoted heredoc delimiter preserves the content literally. `>` creates or replaces this practice file.

```bash
cat > primer.log <<'EOF'
2026-10-21T09:00:00Z id=P01 level=INFO service=api env=prod path=/health status=200 duration_ms=12 client=10.20.0.5 request=req-101 message="healthy"
2026-10-21T09:01:00Z id=P02 level=ERROR service=api env=prod path=/orders status=500 duration_ms=2300 client=10.20.0.5 request=req-102 message="upstream timeout"
2026-10-21T09:02:00Z id=P03 level=WARN service=api env=prod path=/orders status=504 duration_ms=999 client=10.20.0.50 request=req-103 message="retry scheduled"
2026-10-21T09:03:00Z id=P04 level=ERROR service=api env=staging path=/orders status=503 duration_ms=4000 client=10.20.0.5 request=req-104 message="Connection refused"
2026-10-21T09:04:00Z id=P05 level=ERROR service=worker env=prod path=/jobs status=500 duration_ms=10000 client=10.20.0.6 request=req-105 message="TIMEOUT contacting db"
2026-10-21T09:05:00Z id=P06 level=ERROR service=api env=prod path=/health status=503 duration_ms=2100 client=10.20.0.5 request=req-106 message="upstream timeout"
2026-10-21T09:06:00Z id=P07 level=WARN service=api env=prod path=/healthcheck status=502 duration_ms=2000 client=10.20.0.5 request=req-107 message="Connection Refused"
2026-10-21T09:07:00Z id=P08 level=INFO service=api env=prod path=/orders status=200 duration_ms=1999 client=10.20.0.5 request=req-108 message="completed"
2026-10-21T09:08:00Z id=P09 level=ERROR service=api env=prod path=/orders status=500 duration_ms=20000 client=10.20.0.5 request=req-109 message="timeout; retry exhausted"
2026-10-21T09:09:00Z id=P10 level=ERRORISH service=api env=prod path=/orders status=500 duration_ms=3000 client=10x20x0x5 request=req-110 message="synthetic near-match"
2026-10-21T09:10:00Z id=P11 level=ERROR service=api env=prod path=/orders status=5000 duration_ms=500 client=10.20.0.50 request=req-111 message="invalid status sample"
2026-10-21T09:11:00Z id=P12 level=INFO service=api env=prod path=/orders status=200 duration_ms=80 client=10.20.0.5 request=req-102 message="retry recovered"
EOF
cat primer.log
```

Each event is one line. Numeric fields contain unsigned decimal integers without leading zeros. IDs help you check your work; never filter by answer IDs to solve a scenario.

## Five challenges

Use `cat primer.log | grep ...` in every answer and return full original lines unless requested otherwise.

1. Find production API events at exactly WARN or ERROR severity with a three-digit 5xx status. Exclude exactly `/health` but retain `/healthcheck`.
2. Find production events with `duration_ms` at least 2000, including durations with five or more digits. Exclude exactly `/health`.
3. Find events whose client is exactly `10.20.0.5`, whose severity is exactly ERROR and whose status is a valid three-digit 5xx. Do not accidentally match `.50` or `10x20x0x5`.
4. In the inclusive UTC interval 09:02:00–09:07:59 on 2026-10-21, find production events whose message contains `timeout` or `connection refused`, ignoring message case.
5. Investigate `req-102`: return all and only its event lines, then separately count those lines and extract only their three-digit `status=...` tokens. Explain what the sequence shows.

## Solutions

### 1. Production API failures

```bash
cat primer.log | grep -E '(^| )env=prod( |$)' | grep -E '(^| )service=api( |$)' | grep -E '(^| )level=(WARN|ERROR)( |$)' | grep -E '(^| )status=5[0-9]{2}( |$)' | grep -Ev '(^| )path=/health( |$)'
```

Expected IDs: **P02, P03, P07, P09** (4 lines). Field boundaries reject ERRORISH and status 5000; the exact path exclusion keeps `/healthcheck`.

### 2. Slow production events

```bash
cat primer.log | grep -E '(^| )env=prod( |$)' | grep -E '(^| )duration_ms=([2-9][0-9]{3}|[1-9][0-9]{4,})( |$)' | grep -Ev '(^| )path=/health( |$)'
```

Expected IDs: **P02, P05, P07, P09, P10** (5 lines). The alternatives cover 2000–9999 and every integer of five or more digits. P10 qualifies because this question has no severity condition.

### 3. Exact client address

```bash
cat primer.log | grep -E '(^| )client=10\.20\.0\.5( |$)' | grep -E '(^| )level=ERROR( |$)' | grep -E '(^| )status=5[0-9]{2}( |$)'
```

Expected IDs: **P02, P04, P06, P09** (4 lines). Escaped periods are literal; the trailing boundary prevents a longer address from matching. Staging qualifies because no environment restriction was requested.

### 4. Bounded message search

```bash
cat primer.log | grep -E '^2026-10-21T09:0[2-7]:[0-5][0-9]Z ' | grep -E '(^| )env=prod( |$)' | grep -Ei '(^| )message="[^"]*(timeout|connection refused)[^"]*"$'
```

Expected IDs: **P05, P06, P07** (3 lines). The timestamp pattern works because the log uses fixed-width UTC timestamps. The message pattern confines the search to the final quoted message; these fixtures have no embedded quotation marks.

### 5. Request timeline

```bash
cat primer.log | grep -E '(^| )request=req-102( |$)'
cat primer.log | grep -Ec '(^| )request=req-102( |$)'
cat primer.log | grep -E '(^| )request=req-102( |$)' | grep -Eo 'status=[0-9]{3}( |$)'
```

Expected IDs: **P02, P12**; count: **2**; extracted tokens: `status=500`, then `status=200` (each with its following space). The request first failed and later logged a successful retry. These lines support recovery for this request, not proof that the whole service recovered. `grep` preserves input order; it does not sort timestamps.

Continue with [the triage exercise](REGEX_EXERCISE.md); its [separate answer key](REGEIX_EXERCISE_SOLUTION.md) includes evidence-file commands.
