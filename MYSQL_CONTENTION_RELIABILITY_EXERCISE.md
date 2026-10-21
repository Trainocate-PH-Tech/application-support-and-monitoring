# Exercise: MySQL Contention and Reporting Freshness

[Companion guide](MYSQL_CONTENTION_RELIABILITY.md) · [Reference utility](shared/scripts/mysql-contention-report.sh)

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
   WORK_DIR=$(mktemp -d "$HOME/support-lab/mysql-contention-XXXXXX")
   cp -R "$COURSE_ROOT/shared/fixtures/db-topics/mysql-contention" "$WORK_DIR/input"
   INPUT="$WORK_DIR/input"
   cd "$WORK_DIR"
   cat "$INPUT/provenance.txt"
   ```

   Work on these copies. A new shell requires setting `WORK_DIR` and `INPUT` to the paths you created. Do not overwrite original repository fixtures.

## Section: Perform the investigation

1. With the instructor, use writer A, writer B, and observer C exactly as described in the guide. Record connection IDs, the waiting/blocking relationship, and before/after order amounts.
2. Run the bounded deadlock demonstration. Capture the victim and latest InnoDB deadlock evidence; roll back both writers, including the survivor, and verify amounts. Without MySQL, use the abbreviated fixture and clearly label it synthetic.
3. Treat replication as a separate supplied incident. Compare receiver/applier state and errors, then calculate both latest-write gap and visible-write age. Do not configure a replica for this exercise.
4. Write one next investigation for contention and one for stale reporting. Explain why transaction skipping and routing all traffic to the writer are not automatic fixes.

## Section: Inspect evidence manually before automating

1. Run these bounded fixture checks:

   ```bash
   cat "$INPUT/locks.tsv"
   grep -nE 'DEADLOCK|Transaction|ROLL BACK' "$INPUT/innodb.txt"
   jq '{Replica_IO_Running,Replica_SQL_Running,Seconds_Behind_Source,Last_SQL_Errno,Relay_Log_File}' "$INPUT/replica.json"
   ```

2. Record the expected findings: **Waiting session 42 is blocked by 41; the historical excerpt selects transaction 502 as victim. The separate replica case has receiver Yes, applier No, error 1062, and unknown lag. Latest-write gap is 410 seconds; replica visible-write age is 420 seconds.**
3. Write a manual report containing the source, time window, facts, competing explanation, missing evidence, and next read-only check. `>` replaces a file; `>>` appends. A successful command is not a database-health verdict.

## Section: Understand the input contract

The utility accepts **local evidence only**:

```text
mysql-contention-report.sh INPUT_DIR OUTPUT_PARENT
```

- `innodb.txt`: abbreviated historical deadlock text.
- `locks.tsv`: `captured_utc`, `waiting_session`, `blocking_session`, `object_name`.
- `provenance.txt`: source and scenario label.
- `replica.json`: replication state and UTC application visibility timestamps.

TSV files use literal tabs, the exact first-line header, and one record per line. No embedded tabs, multiline cells, quoted CSV, or empty cells are supported. Numeric fields use decimal points, without thousands separators. Special negative blocker IDs are allowed; ordinary numeric measurements must be nonnegative. Header-only tables represent unavailable observations; missing files and malformed rows fail validation. A zero-byte TSV has no schema and is invalid. Timestamps used for comparison are normalized UTC strings; JSON timestamps use `YYYY-MM-DDTHH:MM:SSZ`.

Use the supplied format when manually normalizing reviewed live output; do not rename raw sqlcmd output to `.tsv` and assume it matches. Record the real provenance and units, retain source captures separately, and never fabricate rows to satisfy the schema. The collector snapshots files individually, not atomically across changing input files. Use a completed evidence directory.

## Section: Create your Bash utility

1. Open a new file in your workspace:

   ```bash
   nano mysql-contention-report.sh
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
files=(provenance.txt locks.tsv innodb.txt replica.json)
for file in "${files[@]}"; do
    [[ -f $input/$file && -r $input/$file ]] || fail "Missing or unreadable input: $file"
done
mkdir -p -- "$parent" || fail "Cannot create output parent."
bundle=$(mktemp -d -- "$parent/mysql-contention-XXXXXX") || fail "Cannot create output directory."
for file in "${files[@]}"; do cp -- "$input/$file" "$bundle/$file"; done
validate_tsv "$bundle/locks.tsv" $'captured_utc\twaiting_session\tblocking_session\tobject_name' '2,3'
command -v jq >/dev/null || fail 'Install jq before using this collector.'
jq -e 'type=="object" and (.Replica_IO_Running|type=="string") and (.Replica_SQL_Running|type=="string") and has("Seconds_Behind_Source") and (.Seconds_Behind_Source==null or (.Seconds_Behind_Source|type=="number")) and (.Last_SQL_Errno|type=="number") and (.Relay_Log_File|type=="string") and (.report_route|type=="string") and ([.captured_at,.primary_last_write,.replica_last_visible_write]|all(.[]; type=="string" and (try fromdateiso8601 catch null)!=null))' "$bundle/replica.json" >/dev/null || fail 'Malformed replication evidence.'
{
    printf 'DATABASE SUPPORT EVIDENCE REPORT\nCaptured UTC: %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
    cat -- "$bundle/provenance.txt"

printf 'CURRENT LOCK SNAPSHOT\n'
awk -F '\t' 'NR>1 {printf "%s waiting=%s blocking=%s object=%s\n",$1,$2,$3,$4} END {if(NR==1) print "UNKNOWN: no supplied waits"}' "$bundle/locks.tsv"
printf '\nHISTORICAL DEADLOCK EXCERPT\n'
if grep -nE 'DEADLOCK|Transaction|ROLL BACK' "$bundle/innodb.txt"; then :; else
    rc=$?; (( rc == 1 )) || fail 'Cannot search InnoDB evidence.'
    printf 'UNKNOWN: no matching deadlock evidence\n'
fi
printf '\nSEPARATE REPLICATION CASE\n'
jq -r '"receiver=\(.Replica_IO_Running) applier=\(.Replica_SQL_Running) lag_seconds=\(if .Seconds_Behind_Source == null then "UNKNOWN" else .Seconds_Behind_Source end)",
"route=\(.report_route) relay_log=\(.Relay_Log_File) error=\(.Last_SQL_Errno)",
"capture=\(.captured_at) primary_last_write=\(.primary_last_write) replica_visible=\(.replica_last_visible_write)",
"Latest-write gap seconds=\((.primary_last_write|fromdateiso8601)-(.replica_last_visible_write|fromdateiso8601))",
"Replica visible-write age seconds=\((.captured_at|fromdateiso8601)-(.replica_last_visible_write|fromdateiso8601))"' "$bundle/replica.json"
printf 'Write timestamps are application evidence, not a replacement for replication metrics.\n'

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
   bash -n mysql-contention-report.sh
   bash mysql-contention-report.sh "$INPUT" "$WORK_DIR/reports"
   collector_rc=$?
   printf 'collector exit=%s\n' "$collector_rc"
   ```

2. Make it executable and invoke it directly:

   ```bash
   chmod u+x mysql-contention-report.sh
   ./mysql-contention-report.sh "$INPUT" "$WORK_DIR/reports"
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

1. In an `empty-case` copy, retain only the header in `locks.tsv`; expect unknown/no supplied waits, not proof the server has none.
2. Change the copied replica lag from `null` to `0` using an editor. Explain why the still-stopped applier and old visible-write timestamp prevent a healthy conclusion.
3. Break the JSON syntax in another copy; expect exit 2. Restore the copy before continuing.

Run a changed case with:

```bash
./mysql-contention-report.sh "$WORK_DIR/empty-case" "$WORK_DIR/reports"
printf 'collector exit=%s\n' "$?"
```

Also test a nonexistent input directory and an output path containing spaces. Missing input should fail; quoted paths with spaces should work. Never manufacture an access failure by changing live database-log permissions.

## Section: Submit and clean up

- Submit the executable script, reviewed report and evidence copies, and your edge-case results.
- Include calculations and explain at least one rejected assumption. Label omitted live work as unperformed.
- If you ran live changes, complete the guide's transaction, index, and logging cleanup and verify original results.
- Keep scripts and evidence in your workspace. Do not delete database logs or clear server counters as cleanup.
