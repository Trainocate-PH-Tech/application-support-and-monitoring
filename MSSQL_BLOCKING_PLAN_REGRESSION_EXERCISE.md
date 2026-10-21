# Exercise: SQL Server Blocking and Regression Investigation

[Companion guide](MSSQL_BLOCKING_PLAN_REGRESSION.md) · [Reference utility](shared/scripts/mssql-regression-report.sh)

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
   WORK_DIR=$(mktemp -d "$HOME/support-lab/mssql-regression-XXXXXX")
   cp -R "$COURSE_ROOT/shared/fixtures/db-topics/mssql-regression" "$WORK_DIR/input"
   INPUT="$WORK_DIR/input"
   cd "$WORK_DIR"
   cat "$INPUT/provenance.txt"
   ```

   Work on these copies. A new shell requires setting `WORK_DIR` and `INPUT` to the paths you created. Do not overwrite original repository fixtures.

## Section: Perform the investigation

1. Rehearse the guide's bounded two-writer blocking case if SQL Server is available. Capture the sleeping head blocker, wait state, and transaction count, then roll back both writers and verify original points.
2. Capture two wait snapshots in the same observer connection. Explain why cumulative totals are not interval waits and why a reset invalidates comparison.
3. Inspect the fixture chain and follow 63 to 62 to 61. Keep this blocking incident separate from the supplied deployment regression.
4. For query 17, compute execution-weighted baseline duration and reads, then compare plan 8. Request the missing statistics evidence, actual XML, and release diff before proposing a fix.

## Section: Inspect evidence manually before automating

1. Run these bounded fixture checks:

   ```bash
   cat "$INPUT/sessions.tsv"
   cat "$INPUT/waits-before.tsv" "$INPUT/waits-after.tsv"
   cat "$INPUT/plans.tsv"
   cat "$INPUT/context.txt"
   ```

2. Record the expected findings: **Head blocker 61 is sleeping with one open transaction. Wait deltas: LCK_M_X 12000 ms, SOS_SCHEDULER_YIELD 1000 ms, PAGEIOLATCH_SH 200 ms. Weighted baseline 60 ms and 220 reads becomes 900 ms and 21000 reads: 15× duration and approximately 95.45× reads.**
3. Write a manual report containing the source, time window, facts, competing explanation, missing evidence, and next read-only check. `>` replaces a file; `>>` appends. A successful command is not a database-health verdict.

## Section: Understand the input contract

The utility accepts **local evidence only**:

```text
mssql-regression-report.sh INPUT_DIR OUTPUT_PARENT
```

- `context.txt`: case boundaries and missing evidence.
- `plans.tsv`: `interval_utc`, `query_id`, `plan_id`, `executions`, `avg_duration_us`, `avg_cpu_us`, `avg_reads`.
- `provenance.txt`: source and scenario label.
- `sessions.tsv`: `session_id`, `blocking_session_id`, `status`, `open_transactions`.
- `waits-after.tsv`: `captured_utc`, `server_start_utc`, `wait_type`, `wait_ms`.
- `waits-before.tsv`: `captured_utc`, `server_start_utc`, `wait_type`, `wait_ms`.

TSV files use literal tabs, the exact first-line header, and one record per line. No embedded tabs, multiline cells, quoted CSV, or empty cells are supported. Numeric fields use decimal points, without thousands separators. Special negative blocker IDs are allowed; ordinary numeric measurements must be nonnegative. Header-only tables represent unavailable observations; missing files and malformed rows fail validation. A zero-byte TSV has no schema and is invalid. Timestamps used for comparison are normalized UTC strings; JSON timestamps use `YYYY-MM-DDTHH:MM:SSZ`.

Query Store rows in `plans.tsv` represent regular completed executions only, with comparable interval lengths; keep other execution types separate. Use the supplied format when manually normalizing reviewed live output; do not rename raw sqlcmd output to `.tsv` and assume it matches. Record the real provenance and units, retain source captures separately, and never fabricate rows to satisfy the schema. The collector snapshots files individually, not atomically across changing input files. Use a completed evidence directory.

## Section: Create your Bash utility

1. Open a new file in your workspace:

   ```bash
   nano mssql-regression-report.sh
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
files=(provenance.txt sessions.tsv waits-before.tsv waits-after.tsv plans.tsv context.txt)
for file in "${files[@]}"; do
    [[ -f $input/$file && -r $input/$file ]] || fail "Missing or unreadable input: $file"
done
mkdir -p -- "$parent" || fail "Cannot create output parent."
bundle=$(mktemp -d -- "$parent/mssql-regression-XXXXXX") || fail "Cannot create output directory."
for file in "${files[@]}"; do cp -- "$input/$file" "$bundle/$file"; done
validate_tsv "$bundle/sessions.tsv" $'session_id\tblocking_session_id\tstatus\topen_transactions' '1,4'
validate_tsv "$bundle/waits-before.tsv" $'captured_utc\tserver_start_utc\twait_type\twait_ms' '4'
validate_tsv "$bundle/waits-after.tsv" $'captured_utc\tserver_start_utc\twait_type\twait_ms' '4'
validate_tsv "$bundle/plans.tsv" $'interval_utc\tquery_id\tplan_id\texecutions\tavg_duration_us\tavg_cpu_us\tavg_reads' '2,3,4,5,6,7'
awk -F '\t' 'NR>1 && $2 !~ /^-?[0-9]+$/ {exit 2}' "$bundle/sessions.tsv" || fail 'Invalid blocking session identifier.'
{
    printf 'DATABASE SUPPORT EVIDENCE REPORT\nCaptured UTC: %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
    cat -- "$bundle/provenance.txt"

printf 'BLOCKING CHAIN SNAPSHOT\n'
awk -F '\t' 'NR>1 {b[$1]=$2;s[$1]=$3;t[$1]=$4}
END {if(NR==1) print "UNKNOWN: no sessions supplied";
for(id in b) if(b[id]>0) {delete seen; x=id; chain=id;
while((x in b) && b[x]>0 && !seen[x]) {seen[x]=1;x=b[x];chain=chain " -> " x}
if(seen[x]) print chain,"UNKNOWN: cycle";
else if(!(x in b)) print chain,"UNKNOWN: blocker not captured";
else if(b[x]<0) print chain,"UNKNOWN: special blocker",b[x];
else print chain,"head=" x,"status=" s[x],"open_transactions=" t[x]}
for(id in b) if(b[id]<0) print "session=" id,"UNKNOWN: special blocker",b[id]}' "$bundle/sessions.tsv" | sort
printf '\nWAIT DELTAS (separate blocking case)\n'
awk -F '\t' 'FNR==1 {next} FILENAME==ARGV[1] {v[$3]=$4;start[$3]=$2;stamp[$3]=$1;next}
{n++; if(!($3 in v)||$2!=start[$3]||$4<v[$3]||$1<=stamp[$3]) print $3,"UNKNOWN: missing baseline, reset, or invalid interval";
else printf "%s delta_ms=%.0f\n",$3,$4-v[$3]}
END {if(!n) print "UNKNOWN: no after snapshot"}' "$bundle/waits-before.tsv" "$bundle/waits-after.tsv" | sort

printf '\nQUERY STORE (execution-weighted; only comparable supplied intervals)\n'
awk -F '\t' 'NR>1 {key=$1 " query=" $2 " plan=" $3; n[key]+=$4; d[key]+=$4*$5; c[key]+=$4*$6; r[key]+=$4*$7}
END {if(NR==1) print "UNKNOWN: no Query Store rows";
for(k in n) if(n[k]>0) printf "%s executions=%d duration_ms=%.2f cpu_ms=%.2f reads=%.2f\n",k,n[k],d[k]/n[k]/1000,c[k]/n[k]/1000,r[k]/n[k]; else print k,"UNKNOWN: zero executions"}' "$bundle/plans.tsv" | sort

printf '\nCASE BOUNDARIES AND DEPLOYMENT CONTEXT\n'
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
   bash -n mssql-regression-report.sh
   bash mssql-regression-report.sh "$INPUT" "$WORK_DIR/reports"
   collector_rc=$?
   printf 'collector exit=%s\n' "$collector_rc"
   ```

2. Make it executable and invoke it directly:

   ```bash
   chmod u+x mssql-regression-report.sh
   ./mssql-regression-report.sh "$INPUT" "$WORK_DIR/reports"
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

1. In an `empty-case` copy, retain only the header in `sessions.tsv`; expect unknown/no sessions.
2. Change a copied after-wait counter below its baseline, or change its server-start timestamp. Expect unknown/reset for that wait instead of a negative improvement.
3. Remove session 61 from a copied chain. Expect unknown/blocker not captured; do not relabel 62 as the head. Add a cycle in a separate copy and confirm the utility terminates with unknown/cycle evidence.

Run a changed case with:

```bash
./mssql-regression-report.sh "$WORK_DIR/empty-case" "$WORK_DIR/reports"
printf 'collector exit=%s\n' "$?"
```

Also test a nonexistent input directory and an output path containing spaces. Missing input should fail; quoted paths with spaces should work. Never manufacture an access failure by changing live database-log permissions.

## Section: Submit and clean up

- Submit the executable script, reviewed report and evidence copies, and your edge-case results.
- Include calculations and explain at least one rejected assumption. Label omitted live work as unperformed.
- If you ran live changes, complete the guide's transaction, index, and logging cleanup and verify original results.
- Keep scripts and evidence in your workspace. Do not delete database logs or clear server counters as cleanup.
