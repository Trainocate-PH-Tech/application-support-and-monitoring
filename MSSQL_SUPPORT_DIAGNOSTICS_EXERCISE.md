# Exercise: SQL Server Support Investigation

[Companion guide](MSSQL_SUPPORT_DIAGNOSTICS.md) · [Reference utility](shared/scripts/mssql-diagnostics-report.sh)

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
   WORK_DIR=$(mktemp -d "$HOME/support-lab/mssql-diagnostics-XXXXXX")
   cp -R "$COURSE_ROOT/shared/fixtures/db-topics/mssql-diagnostics" "$WORK_DIR/input"
   INPUT="$WORK_DIR/input"
   cd "$WORK_DIR"
   cat "$INPUT/provenance.txt"
   ```

   Work on these copies. A new shell requires setting `WORK_DIR` and `INPUT` to the paths you created. Do not overwrite original repository fixtures.

## Section: Perform the investigation

1. If SQL Server is available, follow the guide to identify account/server and capture requests, sessions, expensive cached queries, plans, and Query Store status. Record permissions and unavailable features.
2. Have the instructor run the dedicated intentional-failure job once; read history with the supported procedure. Separate step failure from step-0 summary and record the server's time zone.
3. If the server or Agent is unavailable, use the supplied normalized snapshots and label the live sections unperformed. Do not create a fake successful capture.
4. Compare cached query 17's total work with query 18's higher per-call duration. Explain which metric you are ranking and the lifetime/visibility limitations.

## Section: Inspect evidence manually before automating

1. Run these bounded fixture checks:

   ```bash
   cat "$INPUT/requests.tsv"
   awk -F '\t' 'NR>1 && $3==0 {print "failed:",$1,"step=" $2,$4}' "$INPUT/jobs.tsv"
   awk -F '\t' 'NR>1 && $2>0 {print "query=" $1,"average_ms=" $3/$2/1000}' "$INPUT/expensive.tsv"
   ```

2. Record the expected findings: **Session 62 waits on 61. Query 17 averages 800 ms and 500 ms CPU; query 18 averages 2000 ms and 1000 ms CPU. There is one failed step and one failed job outcome, not two independent failures.**
3. Write a manual report containing the source, time window, facts, competing explanation, missing evidence, and next read-only check. `>` replaces a file; `>>` appends. A successful command is not a database-health verdict.

## Section: Understand the input contract

The utility accepts **local evidence only**:

```text
mssql-diagnostics-report.sh INPUT_DIR OUTPUT_PARENT
```

- `expensive.tsv`: `query_id`, `executions`, `total_elapsed_us`, `total_cpu_us`, `total_reads`.
- `jobs.tsv`: `job`, `step_id`, `run_status`, `message`.
- `plans.tsv`: `interval_utc`, `query_id`, `plan_id`, `executions`, `avg_duration_us`, `avg_cpu_us`, `avg_reads`.
- `provenance.txt`: source and scenario label.
- `requests.tsv`: `captured_utc`, `session_id`, `blocking_session_id`, `wait_type`, `elapsed_ms`.

TSV files use literal tabs, the exact first-line header, and one record per line. No embedded tabs, multiline cells, quoted CSV, or empty cells are supported. Numeric fields use decimal points, without thousands separators. Special negative blocker IDs are allowed; ordinary numeric measurements must be nonnegative. Header-only tables represent unavailable observations; missing files and malformed rows fail validation. A zero-byte TSV has no schema and is invalid. Timestamps used for comparison are normalized UTC strings; JSON timestamps use `YYYY-MM-DDTHH:MM:SSZ`.

Query Store rows in `plans.tsv` represent regular completed executions only, with comparable interval lengths; keep other execution types separate. Use the supplied format when manually normalizing reviewed live output; do not rename raw sqlcmd output to `.tsv` and assume it matches. Record the real provenance and units, retain source captures separately, and never fabricate rows to satisfy the schema. The collector snapshots files individually, not atomically across changing input files. Use a completed evidence directory.

## Section: Create your Bash utility

1. Open a new file in your workspace:

   ```bash
   nano mssql-diagnostics-report.sh
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
files=(provenance.txt requests.tsv expensive.tsv plans.tsv jobs.tsv)
for file in "${files[@]}"; do
    [[ -f $input/$file && -r $input/$file ]] || fail "Missing or unreadable input: $file"
done
mkdir -p -- "$parent" || fail "Cannot create output parent."
bundle=$(mktemp -d -- "$parent/mssql-diagnostics-XXXXXX") || fail "Cannot create output directory."
for file in "${files[@]}"; do cp -- "$input/$file" "$bundle/$file"; done
validate_tsv "$bundle/requests.tsv" $'captured_utc\tsession_id\tblocking_session_id\twait_type\telapsed_ms' '2,5'
validate_tsv "$bundle/expensive.tsv" $'query_id\texecutions\ttotal_elapsed_us\ttotal_cpu_us\ttotal_reads' '1,2,3,4,5'
validate_tsv "$bundle/plans.tsv" $'interval_utc\tquery_id\tplan_id\texecutions\tavg_duration_us\tavg_cpu_us\tavg_reads' '2,3,4,5,6,7'
validate_tsv "$bundle/jobs.tsv" $'job\tstep_id\trun_status\tmessage' '2,3'
awk -F '\t' 'NR>1 && $3 !~ /^-?[0-9]+$/ {exit 2}' "$bundle/requests.tsv" || fail 'Invalid blocking session identifier.'
{
    printf 'DATABASE SUPPORT EVIDENCE REPORT\nCaptured UTC: %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
    cat -- "$bundle/provenance.txt"

printf 'ACTIVE REQUEST SNAPSHOT\n'
awk -F '\t' 'NR>1 {printf "session=%s blocker=%s wait=%s elapsed_ms=%s\n",$2,$3,$4,$5} END {if(NR==1) print "UNKNOWN: no requests supplied"}' "$bundle/requests.tsv"
printf '\nCACHED QUERY TOTALS AND AVERAGES\n'
awk -F '\t' 'NR>1 {if($2>0) printf "query=%s executions=%s avg_elapsed_ms=%.2f avg_cpu_ms=%.2f total_reads=%.0f\n",$1,$2,$3/$2/1000,$4/$2/1000,$5; else print "UNKNOWN: zero executions for query",$1} END {if(NR==1) print "UNKNOWN: no cached queries"}' "$bundle/expensive.tsv"
printf '\nJOB FAILURES (step 0 is the job outcome, not another failed step)\n'
awk -F '\t' 'NR>1 && $3==0 {if($2==0) jobs++; else steps++; print $1,"step=" $2,$4}
END {if(NR==1) print "UNKNOWN: no job history"; else printf "failed_steps=%d failed_job_outcomes=%d\n",steps,jobs}' "$bundle/jobs.tsv"

printf '\nQUERY STORE (execution-weighted; only comparable supplied intervals)\n'
awk -F '\t' 'NR>1 {key=$1 " query=" $2 " plan=" $3; n[key]+=$4; d[key]+=$4*$5; c[key]+=$4*$6; r[key]+=$4*$7}
END {if(NR==1) print "UNKNOWN: no Query Store rows";
for(k in n) if(n[k]>0) printf "%s executions=%d duration_ms=%.2f cpu_ms=%.2f reads=%.2f\n",k,n[k],d[k]/n[k]/1000,c[k]/n[k]/1000,r[k]/n[k]; else print k,"UNKNOWN: zero executions"}' "$bundle/plans.tsv" | sort

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
   bash -n mssql-diagnostics-report.sh
   bash mssql-diagnostics-report.sh "$INPUT" "$WORK_DIR/reports"
   collector_rc=$?
   printf 'collector exit=%s\n' "$collector_rc"
   ```

2. Make it executable and invoke it directly:

   ```bash
   chmod u+x mssql-diagnostics-report.sh
   ./mssql-diagnostics-report.sh "$INPUT" "$WORK_DIR/reports"
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

1. In an `empty-case` copy, retain only the header in `jobs.tsv`; expect unknown/no job history.
2. Change one copied query execution count to zero. Expect unknown average rather than divide-by-zero or a fabricated zero duration.
3. Delete a required column from a copied TSV row; expect exit 2. This is a format failure, not a database incident.

Run a changed case with:

```bash
./mssql-diagnostics-report.sh "$WORK_DIR/empty-case" "$WORK_DIR/reports"
printf 'collector exit=%s\n' "$?"
```

Also test a nonexistent input directory and an output path containing spaces. Missing input should fail; quoted paths with spaces should work. Never manufacture an access failure by changing live database-log permissions.

## Section: Submit and clean up

- Submit the executable script, reviewed report and evidence copies, and your edge-case results.
- Include calculations and explain at least one rejected assumption. Label omitted live work as unperformed.
- If you ran live changes, complete the guide's transaction, index, and logging cleanup and verify original results.
- Keep scripts and evidence in your workspace. Do not delete database logs or clear server counters as cleanup.
