# Exercise: Slow MySQL Query Investigation

[Companion guide](MYSQL_SLOW_QUERY_ANALYSIS.md) · [Reference utility](shared/scripts/mysql-slow-report.sh)

**Time:** 60–90 minutes plus optional live setup. **Deliverables:** your executable Bash utility, its private evidence/report directory, completed interpretation, and any live cleanup record. All shell blocks run in Bash; follow the guide for SQL-client commands. The fixture path is usable without a live database.

## Section: Prepare the workspace

1. Enter the repository directory on the Linux host:

   ```bash
   read -r -p 'Absolute repository directory: ' COURSE_ROOT
   cd "$COURSE_ROOT"
   ```

   Stop if the directory is wrong. Install no server just to read the fixtures. Required tools are Bash, GNU coreutils, grep, and awk; the contention collector also requires `jq`. Slow-query grouping uses `mysqldumpslow` when available and labels it unknown otherwise.

2. Create a new private workspace each time:

   ```bash
   umask 077
   mkdir -p "$HOME/support-lab"
   WORK_DIR=$(mktemp -d "$HOME/support-lab/mysql-slow-XXXXXX")
   cp -R "$COURSE_ROOT/shared/fixtures/db-topics/mysql-slow" "$WORK_DIR/input"
   INPUT="$WORK_DIR/input"
   cd "$WORK_DIR"
   cat "$INPUT/provenance.txt"
   ```

   Work on these copies. A new shell requires setting `WORK_DIR` and `INPUT` to the paths you created. Do not overwrite original repository fixtures.

## Section: Perform the investigation

1. Follow the guide's settings inspection. For live work, record original values before the instructor enables a short slow-log capture; restore them before moving on.
2. Load the separate `analysis_orders` table through the guide, verify 100000 rows, and capture a plain `EXPLAIN` plus the customer-42 result. If MySQL is unavailable, label the live portion unperformed and use the supplied log for the ranking exercise.
3. On a dedicated training instance, compare the administrator-created index, then remove that index and verify original query results. Record evidence rather than asserting a fixed elapsed-time improvement.
4. In the synthetic log, compare the frequent report group against the single slowest delay. Which should you investigate first, and what information would change your choice?

## Section: Inspect evidence manually before automating

1. Run these bounded fixture checks:

   ```bash
   tail -n 12 "$INPUT/slow.log"
   grep -n '^# Query_time:' "$INPUT/slow.log"
   awk '/^# Query_time:/ {n++;t+=$3;r+=$9} END {printf "entries=%d seconds=%.2f examined=%.0f\n",n,t,r}' "$INPUT/slow.log"
   ```

2. Record the expected findings: **Four complete entries; total query time 6.60 seconds; 300000 rows examined. When `mysqldumpslow` is available, the three similar reports total approximately 3.6 seconds versus one 3-second delay.**
3. Write a manual report containing the source, time window, facts, competing explanation, missing evidence, and next read-only check. `>` replaces a file; `>>` appends. A successful command is not a database-health verdict.

## Section: Understand the input contract

The utility accepts **local evidence only**:

```text
mysql-slow-report.sh INPUT_DIR OUTPUT_PARENT
```

- `provenance.txt`: source and scenario label.
- `slow.log`: complete conventional MySQL slow-log records.

TSV files use literal tabs, the exact first-line header, and one record per line. No embedded tabs, multiline cells, quoted CSV, or empty cells are supported. Numeric fields use decimal points, without thousands separators. Special negative blocker IDs are allowed; ordinary numeric measurements must be nonnegative. Header-only tables represent unavailable observations; missing files and malformed rows fail validation. A zero-byte TSV has no schema and is invalid. Timestamps used for comparison are normalized UTC strings; JSON timestamps use `YYYY-MM-DDTHH:MM:SSZ`.

Use the supplied format when manually normalizing reviewed live output; do not rename raw sqlcmd output to `.tsv` and assume it matches. Record the real provenance and units, retain source captures separately, and never fabricate rows to satisfy the schema. The collector snapshots files individually, not atomically across changing input files. Use a completed evidence directory.

## Section: Create your Bash utility

1. Open a new file in your workspace:

   ```bash
   nano mysql-slow-report.sh
   ```

2. Paste the script below without the Markdown fences. Save with Ctrl-O, Enter, then exit with Ctrl-X. The first line is the shebang. Read the script in four parts as you enter it: argument/file checks, snapshot creation, analysis, and report output.

```bash
#!/usr/bin/env bash
# Offline teaching collector: no database connections or remediation.
set -euo pipefail
umask 077
export LC_ALL=C
fail() { printf 'ERROR: %s\n' "$*" >&2; exit 2; }
[[ $# == 2 ]] || fail "Usage: $0 INPUT_DIR OUTPUT_PARENT"
input=$1
parent=$2
[[ -d $input ]] || fail "Not an input directory: $input"
# Validate a deliberately simple TSV contract: header, nonempty cells, numbers.
validate_tsv() {
    local file=$1 header=$2 numeric=$3
    awk -F '\t' -v header="$header" -v numeric="$numeric" '
    BEGIN { n=split(header,h,"\t"); k=split(numeric,cols,",") }
    NR==1 { if ($0!=header) exit 2; next }
    { if(NF!=n) exit 2
      for(i=1;i<=NF;i++) if($i=="" || $i ~ /\r/) exit 2
      for(i=1;i<=k;i++) if(cols[i]!="" && $(cols[i]) !~ /^[0-9]+([.][0-9]+)?$/) exit 2 }
    END { if(NR==0) exit 2 }' "$file" || fail "Malformed TSV: $file"
}
files=(provenance.txt slow.log)
for file in "${files[@]}"; do
    [[ -f $input/$file && -r $input/$file ]] || fail "Missing or unreadable input: $file"
done
mkdir -p -- "$parent" || fail "Cannot create output parent."
bundle=$(mktemp -d -- "$parent/mysql-slow-XXXXXX") || fail "Cannot create output directory."
for file in "${files[@]}"; do cp -- "$input/$file" "$bundle/$file"; done
# Recognize the conventional timing header; do not claim this parses arbitrary SQL.
awk '/^# Query_time:/ {if(NF!=9 || $3 !~ /^[0-9]+([.][0-9]+)?$/ || $5 !~ /^[0-9]+([.][0-9]+)?$/ || $7 !~ /^[0-9]+$/ || $9 !~ /^[0-9]+$/) exit 2}' "$bundle/slow.log" || fail 'Malformed slow-log timing header.'
{
    printf 'DATABASE SUPPORT EVIDENCE REPORT\nCaptured UTC: %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
    cat -- "$bundle/provenance.txt"

printf 'SLOW LOG SUMMARY\n'
awk '/^# Query_time:/ {n++;seconds+=$3;locks+=$5;examined+=$9}
END {if(n) printf "entries=%d total_query_seconds=%.2f total_lock_seconds=%.6f rows_examined=%.0f\n",n,seconds,locks,examined; else print "UNKNOWN: no timing headers"}' "$bundle/slow.log"
if command -v mysqldumpslow >/dev/null 2>&1; then
    for ranking in c at t; do
        printf '\nmysqldumpslow sort=%s\n' "$ranking"
        mysqldumpslow -s "$ranking" "$bundle/slow.log"
    done
else
    printf 'UNKNOWN: mysqldumpslow unavailable; grouped rankings not generated. Install the matching MySQL utility, then rerun.\n'
fi
printf 'Timing-header totals are observations, not CPU usage or unique incidents.\n'

    printf '\nINTERPRETATION TO COMPLETE\nObserved facts: ...\nUncertainty: ...\nNext read-only check: ...\n'
    printf 'Collector success is not a database-health verdict. Review copied evidence before sharing.\n'
} > "$bundle/report.txt"
printf 'Report: %s/report.txt\n' "$bundle"
```

3. Explain these constructs before running it:

   | Construct | Purpose |
   |---|---|
   | `#!/usr/bin/env bash` | Uses Bash for direct execution. |
   | `set -euo pipefail` | Detects many unhandled failures, unset variables, and pipeline failures. |
   | `umask 077` | Restricts newly created report files and directories. |
   | `$1`, `$2`, `$#` | Positional inputs and argument count. |
   | `"$variable"` and `--` | Preserve spaces and avoid interpreting paths as options where supported. |
   | Functions and local variables | Reuse checks without mixing their temporary values. |
   | `awk -F '\t'` | Selects TSV fields and calculates numeric results. |
   | `$(...)` | Captures output, such as the unique report directory. |
   | `{ ...; } > file` | Writes grouped output to a report. |

4. Explain where unavailable evidence becomes `UNKNOWN`, where malformed input exits `2`, and where the report still requires a human conclusion. `grep` exit 1 means no matches, not a read error.

## Section: Check syntax, run, and read the report

1. Check syntax and run with Bash:

   ```bash
   bash -n mysql-slow-report.sh
   bash mysql-slow-report.sh "$INPUT" "$WORK_DIR/reports"
   collector_rc=$?
   printf 'collector exit=%s\n' "$collector_rc"
   ```

2. Make it executable and invoke it directly:

   ```bash
   chmod u+x mysql-slow-report.sh
   ./mysql-slow-report.sh "$INPUT" "$WORK_DIR/reports"
   ```

   `./` locates the file in your current directory. Do not run it with `sh`; it uses Bash syntax. Each successful run prints a new report path and leaves prior output intact. Success is exit 0; validation errors are exit 2; other tool failures may return another nonzero code. A failed run may leave an incomplete directory: use only reports from successful runs.

3. Read the exact printed report:

   ```bash
   read -r -p 'Printed report path, without Report: prefix: ' REPORT_FILE
   cat -- "$REPORT_FILE"
   nano "$REPORT_FILE"
   ```

4. Fill in facts, uncertainty, and next check. Include live/fixture provenance and units. Review the copied inputs too; there is no automatic secret redaction. Counts and averages alone are not a diagnosis.

## Section: Test edge cases and explain the results

Prepare a separate copy for each mutation below:

```bash
cp -R "$INPUT" "$WORK_DIR/empty-case"
```

1. Make an `empty-case` copy of the input directory, then empty **only** its copied `slow.log` with `: > "$WORK_DIR/empty-case/slow.log"`. Expect unknown/no timing headers, not a healthy verdict.
2. Change a timing value in a copied log to `invalid`; expect exit 2 for a malformed header.
3. Explain why a tail cut through a record is unsuitable for reliable grouping. Preserve complete records when making an input capture.

Run a changed case with:

```bash
./mysql-slow-report.sh "$WORK_DIR/empty-case" "$WORK_DIR/reports"
printf 'collector exit=%s\n' "$?"
```

Also test a nonexistent input directory and an output path containing spaces. Missing input should fail; quoted paths with spaces should work. Never manufacture an access failure by changing live database-log permissions.

## Section: Submit and clean up

- Submit the executable script, reviewed report and evidence copies, and your edge-case results.
- Include calculations and explain at least one rejected assumption. Label omitted live work as unperformed.
- If you ran live changes, complete the guide's transaction, index, and logging cleanup and verify original results.
- Keep scripts and evidence in your workspace. Do not delete database logs or clear server counters as cleanup.
