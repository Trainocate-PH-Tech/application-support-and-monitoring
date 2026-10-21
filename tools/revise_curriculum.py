"""Reviewed curriculum: pacing, reusable command examples and learner activities.

Applied once to authored outlines and walkthroughs before rendering any artifact.
"""
from guided_exercises import step, L

SYNTAX_CHECK = '''syntax_rc=0
for script in "$HOME"/support-lab/bin/*.sh; do
    [[ -f "$script" ]] || continue
    bash -n "$script" || syntax_rc=1
done
printf 'syntax_exit=%s\\n' "$syntax_rc"'''

FOUNDATION = r'''mkdir -p "$HOME/support-lab/bin"
if [[ -e "$HOME/support-lab/bin/triage.sh" ]]; then
    printf 'Keep existing triage.sh; inspect it before editing.\n'
else
    cat > "$HOME/support-lab/bin/triage.sh" <<'SCRIPT'
#!/usr/bin/env bash
set -u
service=${1:-support-tomcat}
printf 'UTC=%s service=%s\n' "$(date -u +%FT%TZ)" "$service"
df -h "$HOME"
systemctl is-active "$service"
service_rc=$?
printf 'service_exit=%s\n' "$service_rc"
SCRIPT
fi
bash -n "$HOME/support-lab/bin/triage.sh" && chmod 750 "$HOME/support-lab/bin/triage.sh"
"$HOME/support-lab/bin/triage.sh" > "$HOME/support-lab/evidence/m1-04/first-script.txt"
cat "$HOME/support-lab/evidence/m1-04/first-script.txt"'''

HEALTH = r'''#!/usr/bin/env bash
set -u
if (( $# > 2 )); then
    printf 'Usage: %s [service [http(s)-url]]\n' "$0" >&2
    exit 2
fi
service=${1-support-tomcat}
url=${2-http://127.0.0.1:8080/loyalty/health}
if [[ -z "$service" || "$service" == -* || "$service" == *[[:space:]]* ]]; then
    printf 'Invalid service\n' >&2; exit 2
fi
case "$url" in
    http://?*|https://?*) ;;
    *) printf 'Invalid URL\n' >&2; exit 2 ;;
esac
failed=0
log() { printf '%s %s\n' "$(date -u +%FT%TZ)" "$1"; }
for tool in systemctl curl timeout date; do
    command -v "$tool" >/dev/null || exit 2
done
probe_args=(--fail --silent --show-error --max-time 5)
if timeout 5 systemctl is-active --quiet "$service"; then
    log 'service=OK'
else
    log 'service=FAIL'; failed=1
fi
if curl "${probe_args[@]}" "$url" >/dev/null; then
    log 'endpoint=OK'
else
    log 'endpoint=FAIL'; failed=1
fi
exit "$failed"'''

# Topic-specific diagrams replace repetitive workflow slides without changing numbering.
DIAGRAMS = {
    (1, 1): ('Which identity can traverse this path?', ['File: rw-r----- (640)', 'Owner rw; group r', 'Parents need search (x)'], 'Check every parent directory before changing the file mode.'),
    (1, 3): ('Locate the storage limit', ['Volume / loop image', 'Partition → filesystem', 'Quota / inodes / access'], 'A larger device does not automatically enlarge its filesystem.'),
    (2, 3): ('Read the plan before proposing an index', ['Before: ALL / 100,000 rows', 'After: ref / 1,000 rows', 'Verify: time + same result'], 'Illustrative EXPLAIN fields: type describes access; rows is an estimate. Measure actual work on the same input; an index also costs writes and space.'),
    (2, 4): ('A wait becomes a cycle', ['A holds row 1; wants 2', 'B holds row 2; wants 1', 'Victim rolls back'], 'Ordinary blocking has a waiter; a deadlock has a cycle. Verify both sessions after release.'),
    (2, 7): ('Observe before releasing the blocker', ['A: BEGIN + UPDATE', 'B: waits; Observer samples', 'A rollback → B rollback'], 'Sleeping sessions may own open transactions. Preserve the blocking relation before cleanup.'),
    (3, 3): ('Monitoring must preserve unknown states', ['Read bounded window', 'Validate → calculate', 'OK / ALERT / NO_DATA'], 'No valid records is unknown, not zero errors. A successful parse does not prove freshness.'),
}


def apply_revision(modules, guides):
    # 370 scheduled minutes plus an explicit 20-minute checkpoint/recovery reserve.
    durations = {1:[40,60,45,75,50,35,25,40], 2:[35,40,35,40,15,40,40,50,75], 3:[60,55,40,20,35,20,110,30]}
    for m, labs in modules.items():
        for n, lab in enumerate(labs,1):
            if isinstance(lab['minutes'], int): lab['minutes'] = durations[m][n-1]
            g=guides[m,n]
            g['previous']=labs[n-2]['slug'] if n>1 else None
            g['next']=labs[n]['slug'] if n<len(labs) else None
            g['difficulty']='Independent assessment' if g['challenge'] else ('Foundation' if m==1 and n<5 else 'Guided application')
            g['delivery']='Core practice' if isinstance(lab['minutes'],int) else 'Optional extension'
            g['sessions']='Application-server Bash; workstation only where labeled'
            if m==2: g['sessions']='Bash plus labeled MySQL or SQL Server query windows'
            g['repeat']='Keep earlier submissions. Reopen existing scripts; back up edited files before replacing them. Recheck the baseline and confirm the shared-stack slot before repeating instructor demonstrations.'

    g=guides[1,4]
    g['steps'].append(step('Build your first evidence script',L,
        'Spend 20 minutes here. Explain the shebang, quoted variables, default argument, redirection and immediate capture of $?. The application may not be installed yet: NOT_ACTIVE is a valid observation. The last printf makes this a collector, not a health-status interface. Read every line, then run it.',
        FOUNDATION,'An executable script and timestamped evidence exist before the incident challenge. Syntax checking completes before execution.',
        'Fix a reported syntax error before running the script. A denied or unavailable service check must be reported as unknown, not healthy.'))
    g['steps'].append(step('Inspect and execute your saved script',L,
        'Read your saved script. Explain which line captures the service status and which command determines the overall script exit. Syntax-check before executing from another directory.',
        r'''cat "$HOME/support-lab/bin/triage.sh"
if bash -n "$HOME/support-lab/bin/triage.sh"; then
    cd "$HOME"
    ./support-lab/bin/triage.sh support-tomcat
    printf 'collector_exit=%s\n' "$?"
fi''',
        'The collector runs from another directory and reports the service check separately.',
        'Do not execute if the syntax check reports an error.'))
    g['steps'].append(step('Change the input, then choose your own check',L,
        'Predict the output for a deliberately nonexistent service. Run triage.sh with that service as its argument and save the result. Then add a read-only memory check without copying a reference solution. Explain why service_exit and the script’s overall exit status can differ.',
        expected='Your notes include the prediction, observed status and a justified additional command.', trouble='Use man or --help to find an option; record the help used.'))
    g['files'] += ['triage.sh — your first evidence collector','first-script.txt — output and explanation of service_exit']
    modules[1][3]['concepts'].append('Create and execute a small Bash evidence collector before the incident challenge.')
    modules[1][3]['checks'].append('Run triage.sh with two service arguments and explain the captured statuses.')
    modules[1][3]['title']='Command investigations and first Bash script'
    modules[1][3]['output']='Pipelines, archive check and triage.sh with two-input test evidence.'

    g=guides[1,8]
    s=g['steps'][1]
    s.update(title='Extend your existing evidence script', action='Reuse triage.sh from exercise 04. Back it up before editing. Add bounded recent service errors and timestamps; preserve denied-command statuses. Do not replace it with a reference solution.', code=r'''cp -p "$HOME/support-lab/bin/triage.sh" "$(mktemp "$HOME/support-lab/bin/triage-backup-XXXXXX")"
nano "$HOME/support-lab/bin/triage.sh"
bash -n "$HOME/support-lab/bin/triage.sh" && "$HOME/support-lab/bin/triage.sh"''')
    next(s for s in g['steps'] if s['title']=='Investigate within the time budget')['action']='Use 5 minutes to extend your script, 25 for investigation and recovery, and 10 for reporting. Record each hypothesis, discriminating check and observation.'
    modules[1][7]['title']='Linux incident challenge with your evidence script'

    # Show complex storage variants separately instead of implying all are mandatory live labs.
    g=guides[1,3]
    g['delivery']='Core: diagnose and compare growth; demonstration: quota; extensions: deleted-open files and inodes'
    g['steps'][4]['title']='Observe quota allocation; compare additional storage symptoms'
    g['steps'][4]['action']='After the growth demonstration, the instructor cleans up its image. Observe the quota demonstration and complete the [storage worksheet](../../shared/storage-worksheet.md). Deleted-open-file and inode demonstrations are optional extensions with their own cleanup.'
    g['steps'][5]['action']='Using the [storage worksheet](../../shared/storage-worksheet.md), draw volume → partition → filesystem. Treat quota and permissions as separate checks. EBS administration is an instructor demonstration; no AWS changes are required.'
    g['steps'].append(step('Choose the limiting layer independently','Learner · storage worksheet',
        'Case A: device 120 GiB, partition 8 GiB, filesystem 7.7 GiB, no quota. Case B: filesystem 70% free, quota usage equals hard limit. Case C: bytes available but inodes 100% used. For each, choose the next observation, propose one scoped correction and state what must be verified.',
        expected='Three separate diagnoses; no blanket repartitioning recommendation.',trouble='A lack of permission is not proof of a full disk.'))

    # A learner-owned installation/configuration task remains practical without sudo.
    guides[1,5]['steps'].insert(2,step('Repair a copied service configuration',L,
        'Work on this intentionally broken training unit only. Before editing, annotate the service user, Java dependency, startup path and restart policy. Replace /missing/startup.sh using the effective installed unit as evidence; do not install the copy. Explain which installer stages create the service user, deploy the WAR and configure database access.',
        r'''practice_dir=$(mktemp -d "$HOME/support-lab/unit-practice-XXXXXX")
cp "$COURSE_ROOT/shared/templates/service-practice.service" "$practice_dir/support-tomcat.service"
systemctl cat support-tomcat
nano "$practice_dir/support-tomcat.service"
cat "$practice_dir/support-tomcat.service"''',
        'Each learner submits an annotated corrected unit and a readiness test proposal.', 'If the live unit is unavailable, the instructor supplies its rehearsed capture. Do not guess a production path.'))
    guides[1,5]['files'].append('corrected-unit.md — copied unit, correction evidence and verification proposal')
    guides[1,7]['delivery']='Core: process, listener and endpoint checks; platform cards: choose one; remaining cards: extension'
    for s in guides[1,7]['steps']:
        if 'Platform incident cards' in s['action']: s['action']='Choose one [platform incident card](../../shared/fixtures/platform-incidents.md). State facts, a competing explanation and a discriminating check. Other cards are optional extensions. The instructor may demonstrate read-only firewall inspection.'

    guides[2,7]['delivery']='Core: blocking timeline; guided evidence: Query Store and job history; live plan changes/jobs: extension'
    guides[2,7]['sequence']='| Order | Session | Action |\n|---|---|---|\n| 1 | A | Open transaction and update |\n| 2 | B | Begin transaction; issue bounded conflicting update |\n| 3 | Observer | Capture blocker while B waits |\n| 4 | A | Roll back |\n| 5 | B | Roll back even after timeout; verify state |'
    for s in guides[2,7]['steps']:
        if any(x in s['title'].lower() for x in ('query store','plan','job','statistic','index change')):
            s['title']='Live extension — '+s['title']
    guides[2,4]['sequence']='| Order | Session | Action |\n|---|---|---|\n| 1 | A | Begin; update the first row |\n| 2 | B | Begin; issue conflicting update |\n| 3 | Observer | Capture the wait before the timeout |\n| 4 | A then B | Roll back both sessions |\n| 5 | A and B | Follow the separate deadlock sequence; roll back both afterward |'
    guides[2,7]['steps']=[s for s in guides[2,7]['steps'] if s['title']!='Interpret deterministic regression evidence']
    guides[2,7]['steps'].append(step('Compare captured Query Store and job evidence',L,
        'Core guided evidence task: read the two fixture files. Compute duration and logical-read changes for query 17; identify the failed job step separately. Explain one alternative to a missing index and which observation would distinguish it. Live plan and job steps above are optional extensions.',
        'cat "$COURSE_ROOT/shared/fixtures/query-store.csv"\ncat "$COURSE_ROOT/shared/fixtures/job-history.csv"',
        'A quantitative before/after comparison and separate job diagnosis; neither fixture is claimed as live evidence.', 'Units are microseconds and execution intervals must be comparable.'))
    modules[2][6]['checks']=['Capture a blocking relation and roll back both sessions.','Compare Query Store duration/reads and identify the failed job step using live or explicitly synthetic evidence.']

    g=guides[2,9]
    g['prerequisites']='Complete the preceding database exercises. Use the concealed database-performance evidence case supplied by the instructor. No live fault injection is required for this assessment.'
    g['steps'][0]['expected']='A report exists before opening the synthetic case; roles and start time are recorded.'
    g['steps'][1]['code']='cp -i "$COURSE_ROOT/shared/templates/database-report.md" ~/support-lab/evidence/m2-09/database-report.md\ncat "$COURSE_ROOT/shared/fixtures/database-incident.md"'
    g['steps'][1]['expected']='The worksheet and synthetic case are available; do not confuse case evidence with live baseline checks.'
    g['steps'][4].update(action='Preserve the initial case evidence with your pre-change reasoning. Record additional evidence supplied by the instructor in a separate file; keep capture times and provenance.', code='cp -i "$COURSE_ROOT/shared/fixtures/database-incident.md" "$HOME/support-lab/evidence/m2-09/case-before.md"', expected='Original and additional evidence remain distinguishable.', trouble='Do not substitute unrelated live collector output for case evidence.')
    g['steps'][5].update(where='Team proposal; instructor releases synthetic evidence', action='Submit the proposed scoped correction, supporting evidence, owner, rollback trigger and comparable verification criteria. No privileged change is performed for this case.')
    g['steps'][1]['action']='Copy the worksheet without overwriting an earlier report. Read shared/fixtures/database-incident.md. Keep this synthetic case separate from the optional healthy live baseline.'
    g['steps'][2]['trouble']='Confirm which capture belongs to this case; unrelated fixtures are not additional evidence.'
    g['steps'][2]['action']='Investigate why a report became slower after a release. Use the linked evidence case, test at least two plausible explanations and justify a scoped correction. Roles rotate; no fault name or solution is provided.'
    g['steps'][3]['action']='Use 10 minutes for impact and roles, 25 for analysis, 15 for a remediation proposal and validation criteria, and 25 for reporting and individual review.'
    g['steps'][-1]['action']='Request the instructor’s post-change evidence only after submitting a hypothesis and proposed change. Compare the same workload, rows, duration and reads before/after. Record residual uncertainty and a rollback trigger. Submit the database-health script outline with timeouts and unknown states.'
    g['cleanup']='This case uses synthetic evidence; do not modify the shared database. Close any optional baseline clients and unset SQLCMDPASSWORD. Preserve submitted pre-change reasoning and post-change comparisons.'
    modules[2][8]['concepts']=['Quantify changes in workload, query cost and result equivalence.','Test competing causes with discriminating evidence.','Define a reversible correction and bounded database-health checks.']
    modules[2][8]['tricks']=['Do three unblocked snapshots rule out all intermittent blocking?','Does a plan change alone prove which repair is correct?']
    modules[2][8]['output']='A case report with calculations, alternative hypotheses, before/after comparison and a database-health design.'
    modules[2][8].update(scenario='A reporting request regressed after a release while ordinary player lookup remains responsive. Distinguish competing database causes using a separate synthetic incident pack.',checks=['Quantify the report regression and test at least two explanations.','Propose a scoped change and compare instructor-released before/after evidence.','Submit a bounded database-health automation design and an individual explanation.'], answer='Case D: execution count and returned rows are stable; reads and per-call duration rose after a plan changed. No observed blocker explains the sampled window. Compare plan/statistics/deployment evidence before proposing an index. Post-change capture is consistent with reduced work but does not prove which production change would be best. See the concealed case D release card.')

    g=guides[3,1]
    g['prerequisites']='Your Module 1 triage.sh and first-script notes; a healthy shared stack; Bash, curl, timeout, systemctl and an editor.'
    g['steps'][0].update(action='Review your Module 1 collector. Extend its observations into a new health-check interface. Preserve an existing my-health.sh; edit only after inspecting it.',code=r'''mkdir -p ~/support-lab/bin
cat "$HOME/support-lab/bin/triage.sh"
if [[ ! -e "$HOME/support-lab/bin/my-health.sh" ]]; then
    cp "$HOME/support-lab/bin/triage.sh" "$HOME/support-lab/bin/my-health.sh"
fi
nano "$HOME/support-lab/bin/my-health.sh"''')
    g['steps'][1].update(code=HEALTH,action='Adapt your collector using this scaffold. Add available-memory and disk reporting yourself. Define 0 healthy, 1 failed probe, 2 invalid arguments or missing tools. Explain why the quoted probe_args array passes each option separately. Bounded probes prevent a missing service response from hanging your check.')
    g['steps'].insert(4,step('Test your own validation and array behavior',L,
        'Predict each status first. Invalid argument counts and unsupported URLs must return 2 before any network probe. Inspect the array expansion in your script; explain why an unquoted string is not equivalent.',
        r'''~/support-lab/bin/my-health.sh support-tomcat http://127.0.0.1:8080/loyalty/health extra
printf 'extra_argument_exit=%s\n' "$?"
~/support-lab/bin/my-health.sh support-tomcat file:///etc/passwd
printf 'invalid_url_exit=%s\n' "$?"
~/support-lab/bin/my-health.sh '' http://127.0.0.1:8080/loyalty/health
printf 'empty_service_exit=%s\n' "$?"''',
        'All three return 2. Your test transcript names your own script and observed result.', 'Do not substitute reference-script results for your implementation.'))
    modules[3][0]['title']='Extend your Bash script into a health check'
    modules[3][0]['checks']=['Your script returns 0 for healthy checks, 1 for an unreachable endpoint and 2 for invalid arguments or missing tools.','Explain the quoted option array; submit actual results from your own script.']

    # Preserve earlier reports before all template copies, including repeat runs.
    for g in guides.values():
        for s in g['steps']:
            if s['code'].lstrip().startswith('cp ') and 'shared/templates/' in s['code']:
                s['code']=s['code'].replace('cp ', 'cp -i ',1)
                s['action']='Before copying: if prompted to overwrite, answer n, retain your earlier file and use a dated backup before editing. '+s['action']
    for s in guides[3,8]['steps']:
        if 'bash -n' in s['code']: s['code']=SYNTAX_CHECK

    # Every guided lesson ends with a transfer task requiring independent selection.
    for g in guides.values():
        if not g['challenge']:
            g['steps'].append(step('Transfer the method without copying','Learner · individual review', 'Choose one input, path, service name or evidence assumption from this exercise and predict how a changed value would affect the result. Use only learner-owned files or permitted read-only checks. Choose the command yourself, run it, then explain the observed difference to a partner. If only synthetic evidence is available, request a changed capture and label the result simulated.', expected='An individual prediction, a chosen check and an evidence-based explanation are recorded in the exercise notes.', trouble='A changed input must not mutate shared services or another learner’s files. Ask for a fixture variant when necessary.'))

    # Deck snippets are complete walkthrough blocks, never filtered/truncated command lines.
    for m,labs in modules.items():
        for n,lab in enumerate(labs,1):
            g=guides[m,n]
            for s in g['steps']: s['code']=s['code'].strip()
            lab['steps']=[s['title'] for s in g['steps']]
            lab['commands']='\n\n'.join(s['code'] for s in g['steps'] if s['code'])
            candidates=[s for s in g['steps'] if s['code'] and not s['where'].startswith('Instructor') and len(s['code'].splitlines())<=7 and max(map(len,s['code'].splitlines()))<=105]
            g['slide_step']=candidates[0] if candidates else None
    guides[1,4]['slide_step']=next(s for s in guides[1,4]['steps'] if s['title']=='Inspect and execute your saved script')
    guides[3,8]['slide_step']=next(s for s in guides[3,8]['steps'] if 'bash -n' in s['code'])
