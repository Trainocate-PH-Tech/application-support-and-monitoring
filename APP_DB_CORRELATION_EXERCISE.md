# Exercise: Application and Database Timeline Investigation

[Companion guide](APP_DB_CORRELATION.md) · [Reference utility](shared/scripts/app-db-correlation-report.sh)

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
   WORK_DIR=$(mktemp -d "$HOME/support-lab/app-db-XXXXXX")
   cp -R "$COURSE_ROOT/shared/fixtures/db-topics/app-db" "$WORK_DIR/input"
   INPUT="$WORK_DIR/input"
   cd "$WORK_DIR"
   cat "$INPUT/provenance.txt"
   ```

   Work on these copies. A new shell requires setting `WORK_DIR` and `INPUT` to the paths you created. Do not overwrite original repository fixtures.

## Section: Perform the investigation

1. Read the guide's timing and identifier rules. For each request, record operation, status, impact, attempts, pool time, SQL time, downstream time, and explicit database-operation match.
2. Reconcile each total using the supplied nonoverlapping buckets. Distinguish already-totaled retry time from per-attempt timings. For real overlapping spans, do not apply this arithmetic blindly.
3. Compare r101 (pool), r102 (SQL), and r103 (downstream). Request one additional measurement for each before declaring root cause.
4. Optionally run the guide's one-shot curl check against an explicitly approved read-only health endpoint. Keep this new live measurement separate from the historical fixture; never replay the synthetic checkout.

## Section: Inspect evidence manually before automating

1. Run these bounded fixture checks:

   ```bash
   grep -Fn 'r101' "$INPUT/requests.tsv" "$INPUT/db.tsv"
   awk -F '\t' 'NR>1 {print $1,"residual_ms=" $5-($6+$7+$8+$9)}' "$INPUT/requests.tsv"
   cat "$INPUT/context.txt"
   ```

2. Record the expected findings: **Four supplied requests, two HTTP errors (50% of this sample), all residuals zero, and four explicit database matches. Dominant observed durations are pool wait 4000 ms for r101, SQL 2800 ms for r102, and downstream 4200 ms for r103.**
3. Write a manual report containing the source, time window, facts, competing explanation, missing evidence, and next read-only check. `>` replaces a file; `>>` appends. A successful command is not a database-health verdict.

## Section: Understand the input contract

The utility accepts **local evidence only**:

```text
app-db-correlation-report.sh INPUT_DIR OUTPUT_PARENT
```

- `context.txt`: case boundaries and missing evidence.
- `db.tsv`: `db_operation_id`, `request_id`, `duration_ms`, `endpoint`.
- `provenance.txt`: source and scenario label.
- `requests.tsv`: `request_id`, `start_utc`, `operation`, `http_status`, `http_ms`, `pool_ms`, `sql_ms`, `downstream_ms`, `other_ms`, `attempts`, `db_operation_id`.

TSV files use literal tabs, the exact first-line header, and one record per line. No embedded tabs, multiline cells, quoted CSV, or empty cells are supported. Numeric fields use decimal points, without thousands separators. Special negative blocker IDs are allowed; ordinary numeric measurements must be nonnegative. Header-only tables represent unavailable observations; missing files and malformed rows fail validation. A zero-byte TSV has no schema and is invalid. Timestamps used for comparison are normalized UTC strings; JSON timestamps use `YYYY-MM-DDTHH:MM:SSZ`.

Use the supplied format when manually normalizing reviewed live output; do not rename raw sqlcmd output to `.tsv` and assume it matches. Record the real provenance and units, retain source captures separately, and never fabricate rows to satisfy the schema. The collector snapshots files individually, not atomically across changing input files. Use a completed evidence directory.

## Section: Create your Bash utility

1. Open a new file in your workspace:

   ```bash
   nano app-db-correlation-report.sh
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
files=(provenance.txt requests.tsv db.tsv context.txt)
for file in "${files[@]}"; do
    [[ -f $input/$file && -r $input/$file ]] || fail "Missing or unreadable input: $file"
done
mkdir -p -- "$parent" || fail "Cannot create output parent."
bundle=$(mktemp -d -- "$parent/app-db-XXXXXX") || fail "Cannot create output directory."
for file in "${files[@]}"; do cp -- "$input/$file" "$bundle/$file"; done
validate_tsv "$bundle/requests.tsv" $'request_id\tstart_utc\toperation\thttp_status\thttp_ms\tpool_ms\tsql_ms\tdownstream_ms\tother_ms\tattempts\tdb_operation_id' '4,5,6,7,8,9,10'
validate_tsv "$bundle/db.tsv" $'db_operation_id\trequest_id\tduration_ms\tendpoint' '3'
{
    printf 'DATABASE SUPPORT EVIDENCE REPORT\nCaptured UTC: %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
    cat -- "$bundle/provenance.txt"

printf 'REQUEST RECONCILIATION (sequential fixture buckets, all attempts included)\n'
awk -F '\t' 'FNR==1 {next} FILENAME==ARGV[1] {key=$1 SUBSEP $2;duration[key]=$3;next}
{n++; errors+=($4>=400);sum=$6+$7+$8+$9;key=$11 SUBSEP $1;
printf "request=%s operation=%s status=%s http_ms=%s component_ms=%.0f residual_ms=%.0f attempts=%s\n",$1,$3,$4,$5,sum,$5-sum,$10;
if(key in duration) printf "  explicit_db_match=%s sql_difference_ms=%.0f\n",$11,$7-duration[key];else print "  UNKNOWN: no explicit database-operation match";
print "  pool_ms=" $6,"sql_ms=" $7,"downstream_ms=" $8,"other_ms=" $9}
END {if(n) printf "requests=%d error_requests=%d error_percent=%.2f\n",n,errors,100*errors/n; else print "UNKNOWN: no requests"}' "$bundle/db.tsv" "$bundle/requests.tsv"
printf '\nCONTEXT\n'
cat -- "$bundle/context.txt"

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
   bash -n app-db-correlation-report.sh
   bash app-db-correlation-report.sh "$INPUT" "$WORK_DIR/reports"
   collector_rc=$?
   printf 'collector exit=%s\n' "$collector_rc"
   ```

2. Make it executable and invoke it directly:

   ```bash
   chmod u+x app-db-correlation-report.sh
   ./app-db-correlation-report.sh "$INPUT" "$WORK_DIR/reports"
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

1. In an `empty-case` copy, retain only the header in `requests.tsv`; expect unknown/no requests rather than an error-rate division by zero.
2. Remove q101 from the copied `db.tsv`; expect an unknown explicit match for r101 while preserving its application evidence.
3. Change a copied component duration and inspect the nonzero residual. State that it indicates inconsistent/incomplete measurement, not an automatically diagnosed network problem.

Run a changed case with:

```bash
./app-db-correlation-report.sh "$WORK_DIR/empty-case" "$WORK_DIR/reports"
printf 'collector exit=%s\n' "$?"
```

Also test a nonexistent input directory and an output path containing spaces. Missing input should fail; quoted paths with spaces should work. Never manufacture an access failure by changing live database-log permissions.

## Section: Submit and clean up

- Submit the executable script, reviewed report and evidence copies, and your edge-case results.
- Include calculations and explain at least one rejected assumption. Label omitted live work as unperformed.
- If you ran live changes, complete the guide's transaction, index, and logging cleanup and verify original results.
- Keep scripts and evidence in your workspace. Do not delete database logs or clear server counters as cleanup.
