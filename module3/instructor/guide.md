# Module 3 instructor guide

Keep this answer key separate from student handouts. Rehearse setup and fault reset before class. Speaker notes include the same reasoning for live delivery. Review [shared setup](../../shared/instructor/setup-and-delivery.md), [scenario cards/rubric](../../shared/instructor/scenarios.md) and [storage procedures](../../shared/instructor/storage.md).

## Extend your Bash script into a health check

Slides 5–9. Time: 60.

**Expected reasoning:** Capture the status immediately after the command. Explicit if command; then branches make expected failures clear. The reference health checker validates the disk threshold and reports each check instead of stopping at the first unhealthy service.

**Hint ladder:** First ask which layer the evidence describes. Next ask for a discriminating command from the worksheet. Finally point to the relevant fixture or reference script; do not reveal the hidden fault immediately.

**Acceptance:** Your script returns 0 for healthy checks, 1 for an unreachable endpoint and 2 for invalid arguments or missing tools. Explain the quoted option array; submit actual results from your own script.

**Submission:** A documented executable Bash health checker and test transcript.

**Guided walkthrough checkpoints:**

1. Create a script you can edit — You have your own editable script; the shared original is unchanged.
2. Implement the check interface — The script uses arguments, defaults, a function, a loop, conditions and a documented status.
3. Check syntax before execution — Healthy checks return 0. Syntax success normally produces no output.
4. Test an expected failure without changing services — The endpoint check fails promptly and the script returns 1.
5. Test your own validation and array behavior — All three return 2. Your test transcript names your own script and observed result.
6. Compare with the reference implementation — The reference returns 2 for invalid configuration. Your report distinguishes this from an unhealthy service.
7. Transfer the method without copying — An individual prediction, a chosen check and an evidence-based explanation are recorded in the exercise notes.

**Exercise-specific recovery:** Leave the shared service running. Keep your executable script and test transcript; remove no system files. Return to COURSE_ROOT before the next exercise.

**Instructor execution sheet:**


## Automated evidence collection

Slides 10–14. Time: 55.

**Expected reasoning:** mktemp adds uniqueness; umask 077 restricts access. Nonzero capture results set partial=1 while preserving the rest of the bundle. Do not collect unrestricted environment/process argument data. Structured sensitive values may need stronger, format-aware redaction.

**Hint ladder:** First ask which layer the evidence describes. Next ask for a discriminating command from the worksheet. Finally point to the relevant fixture or reference script; do not reveal the hidden fault immediately.

**Acceptance:** Failed checks remain visible in the manifest. Bundle contains no credentials or environment dumps and is reviewed before sharing.

**Submission:** A reviewed evidence archive, manifest and evidence index.

**Guided walkthrough checkpoints:**

1. Collect a bounded evidence bundle — Exit 0 means all capture commands succeeded; 1 means a useful partial bundle; 2 means creation/packaging failed.
2. Inspect the exact bundle — The archive is private to your account; the manifest lists each capture’s exit code.
3. Interpret missing permissions — Your evidence index labels inaccessible data and empty data differently.
4. Inspect and exercise masking with synthetic input — Both synthetic values become [REDACTED].
5. Write an evidence index — A reviewer can locate evidence and understand gaps without rerunning the incident.
6. Transfer the method without copying — An individual prediction, a chosen check and an evidence-based explanation are recorded in the exercise notes.

**Exercise-specific recovery:** Keep the reviewed bundle and index. The extraction directory contains copies and may be removed after review; do not delete the only incident archive or broadly clean other evidence.

**Instructor execution sheet:**


## Log parsing and threshold monitoring

Slides 15–19. Time: 40.

**Expected reasoning:** The supplied policy counts status >=500 as server failures and latency >= threshold as slow. A rate equal to the threshold alerts. NO_DATA is unknown, not green. HTTP 4xx monitoring may be added separately according to business context.

**Hint ladder:** First ask which layer the evidence describes. Next ask for a discriminating command from the worksheet. Finally point to the relevant fixture or reference script; do not reveal the hidden fault immediately.

**Acceptance:** Fixture result is 6 requests, 2 errors, 33.33%, 2 slow, 1 malformed, ALERT. Empty input yields NO_DATA and exit 2, never healthy.

**Submission:** A monitoring CSV and a written policy with denominator and no-data semantics.

**Guided walkthrough checkpoints:**

1. Run the known fixture — CSV: 6 requests, 2 errors, 33.33 percent, 2 slow, 1 malformed, ALERT; exit 1.
2. Create isolated boundary inputs — Three small test files exist; the empty file is intentionally zero bytes.
3. Compare healthy, empty and malformed cases — Healthy returns OK/0; empty and malformed-only inputs return NO_DATA/2.
4. Parse a current journal window — Live results vary with traffic; non-request startup lines count as malformed.
5. Document the monitoring policy — Someone else can explain why each fixture alerts or does not alert.
6. Transfer the method without copying — An individual prediction, a chosen check and an evidence-based explanation are recorded in the exercise notes.

**Exercise-specific recovery:** Keep the small test files and CSV results as evidence. No service configuration changed; do not delete the live journal or source fixture.

**Instructor execution sheet:**


## Slow-query summaries and correlation pipelines

Slides 20–24. Time: 20.

**Expected reasoning:** Multiline logs require a record-aware parser. Temporal overlap narrows investigation but does not prove the app request executed a particular SQL record. Keep original evidence and clearly label derived summaries.

**Hint ladder:** First ask which layer the evidence describes. Next ask for a discriminating command from the worksheet. Finally point to the relevant fixture or reference script; do not reveal the hidden fault immediately.

**Acceptance:** Report preserves both frequency and time rankings. Wrapper does not discard useful ALERT output because its exit code is 1.

**Submission:** A timestamped monitoring/slow-query report and its limitations.

**Guided walkthrough checkpoints:**

1. Create your report directory and source record — You have a fresh report directory and UTC capture record.
2. Produce two slow-query rankings — Similar queries group together; the report query runs three times.
3. Save an alert result without losing it — The CSV exists and reports ALERT even though exit status is 1.
4. Run the reference wrapper and inspect its manifest — With mysqldumpslow available, the wrapper retains the alert output and exits 1. Exit 2 indicates incomplete/invalid evidence.
5. Transfer the method without copying — An individual prediction, a chosen check and an evidence-based explanation are recorded in the exercise notes.

**Exercise-specific recovery:** Keep your report directory and manifest. Original logs remain unchanged. No active monitoring daemon was started by these commands.

**Instructor execution sheet:**


## Health checks, cron and safe retention

Slides 25–29. Time: 35.

**Expected reasoning:** Cron does not inherit the current terminal environment. Use protected credential files and least privilege. flock avoids concurrent runs; log job status and review errors. find -mtime +7 means more than seven completed 24-hour periods, not a calendar cutoff.

**Hint ladder:** First ask which layer the evidence describes. Next ask for a discriminating command from the worksheet. Finally point to the relevant fixture or reference script; do not reveal the hidden fault immediately.

**Acceptance:** Scheduled execution uses absolute paths and a per-user lock. Dry-run identifies only intended incident archives older than the retention boundary.

**Submission:** A reviewed cron entry, minimal-environment test and retention dry-run output.

**Guided walkthrough checkpoints:**

1. Install learner-owned scripts and test the cron environment — The script runs from /tmp without relying on your interactive PATH or working directory.
2. Back up and edit your own crontab — An editor opens for your account. Copy the template entries and replace every /home/learner01 with the actual HOME printed above.
3. Verify the saved entry and observe execution — The installed entry uses absolute paths and flock. Later scheduled entries have new timestamps.
4. Create disposable retention input — Only dummy files exist in this isolated directory; the .tar.gz name is a retention test filename, not a real archive.
5. Preview, apply and verify narrowly scoped cleanup — The old incident file is removed and unrelated.txt remains.
6. Remove only the exercise’s scheduled entries — The exercise entries are gone; previous entries remain.
7. Transfer the method without copying — An individual prediction, a chosen check and an evidence-based explanation are recorded in the exercise notes.

**Exercise-specific recovery:** Remove the exercise’s cron entries as shown unless the instructor explicitly asks to retain them. Delete the two dummy files/directory under the recorded demo_home after verification; keep real evidence and the crontab backup. Archive retention is not a database backup or restore strategy.

**Instructor execution sheet:**


## Deployment verification and maintenance boundaries

Slides 30–34. Time: 20.

**Expected reasoning:** The payment simulator can fail while database readiness remains healthy. Monitor representative business paths separately. A failed probe should emit evidence and status; restarting databases is not a safe default response.

**Hint ladder:** First ask which layer the evidence describes. Next ask for a discriminating command from the worksheet. Finally point to the relevant fixture or reference script; do not reveal the hidden fault immediately.

**Acceptance:** Gate fails on affected business functionality even when Tomcat remains active. Recovery checks cover the same function that originally failed.

**Submission:** A deployment-check script with documented scope and failure behavior.

**Guided walkthrough checkpoints:**

1. Record the business response — Player response is 1,Synthetic Player One,100 and payment simulator reports ready.
2. Create your deployment gate — Your own file checks content, not just process existence.
3. Check and run the gate — Healthy business checks pass with exit 0.
4. Test an affected business function — Your completed gate fails on the affected business route even if generic readiness remains green.
5. Restore and verify — The same business checks that failed now succeed.
6. Transfer the method without copying — An individual prediction, a chosen check and an evidence-based explanation are recorded in the exercise notes.

**Exercise-specific recovery:** Instructor confirms reset. Leave your deployment script in your bin directory; do not add automatic restarts, database repairs or cron scheduling to this gate.

**Instructor execution sheet:**

Restore and verify

Reset the instructor-selected fault, then learners rerun their gate.

```bash
cd "$COURSE_ROOT"
sudo shared/scripts/fault.sh reset
```
## Major incident simulation

Slides 35–39. Time: 110.

**Expected reasoning:** Use instructor scenario cards. A uses db-auth; B uses latency with database decoy evidence; C uses payment while /health remains healthy. Each has distinct business recovery criteria. Grade communication of uncertainty and evidence-backed elimination of alternatives.

**Hint ladder:** First ask which layer the evidence describes. Next ask for a discriminating command from the worksheet. Finally point to the relevant fixture or reference script; do not reveal the hidden fault immediately.

**Acceptance:** Timeline links symptoms, actions and results to evidence. Updates communicate impact, current action, owner and next update time.

**Submission:** A major incident report, evidence bundle and three stakeholder updates.

**Guided walkthrough checkpoints:**

1. Prepare your submission workspace — A report exists before the fault is introduced; roles and start time are recorded.
2. Receive the incident and assign roles — You know the business symptom, allowed targets, time budget and required deliverables, but not the root cause.
3. Investigate within the time budget — Your timeline contains evidence-linked observations rather than a list of guesses.
4. Collect and inspect evidence — A full or partial bundle is available. Exit 1 can be valid partial evidence; inspect the manifest.
5. Propose one mitigation and define recovery — The instructor can review a concrete action; the report distinguishes diagnosis from speculation.
6. Verify and hand over — Recovery is supported by the affected business function and a clear observation window.

**Exercise-specific recovery:** After saving evidence, the instructor resets the assigned fault. Roll back any transactions opened during investigation in their owning sessions, close database clients and unset SQLCMDPASSWORD where used. Verify the affected business route again. Keep evidence and scripts; do not reset another team’s active scenario.

**Instructor execution sheet:**


## Final challenges and operational handover

Slides 40–44. Time: 30.

**Expected reasoning:** Useful recommendations name a signal, threshold/window, owner and response. Explicit uncertainty is preferable to invented certainty. Final rubric allocates points across evidence, diagnosis, recovery, scripts and communication.

**Hint ladder:** First ask which layer the evidence describes. Next ask for a discriminating command from the worksheet. Finally point to the relevant fixture or reference script; do not reveal the hidden fault immediately.

**Acceptance:** Next shift can reproduce checks and locate evidence. Final report distinguishes confirmed facts from probable explanations.

**Submission:** Operational handover and prioritized improvement backlog.

**Guided walkthrough checkpoints:**

1. Collect your handover inputs — Each script passes syntax checks before submission.
2. Prepare a five-minute handover — Another shift can locate evidence and repeat checks without a verbal explanation.
3. Defend a counterexample — Your explanation connects a conclusion to evidence and acknowledges uncertainty.
4. Write three actionable improvements — Each recommendation can be assigned and tested; “monitor more” is replaced by a measurable action.
5. Review and submit — The recipient can read the report, find evidence and understand residual risk.
6. Transfer the method without copying — An individual prediction, a chosen check and an evidence-based explanation are recorded in the exercise notes.

**Exercise-specific recovery:** Confirm with the instructor that simulation faults and open transactions are cleared. Remove only your exercise cron entries if still active; retain reviewed artifacts for assessment.

**Instructor execution sheet:**


## Advanced automation challenge bank

Slides 45–49. Time: Extension.

**Expected reasoning:** Parsing success says nothing about freshness; capture windows and last-event timestamps matter. Preserve exit codes immediately. Treat timeout, unavailable permissions and no data as explicit operational states. See reference tests for baseline expected behavior.

**Hint ladder:** First ask which layer the evidence describes. Next ask for a discriminating command from the worksheet. Finally point to the relevant fixture or reference script; do not reveal the hidden fault immediately.

**Acceptance:** Each new behavior has a meaningful adverse-case test. Unknown/unavailable dependencies are not reported as healthy.

**Submission:** A hardening patch, test transcript and documented remaining limitations.

**Guided walkthrough checkpoints:**

1. Create a hardening test matrix — The matrix separates OK, ALERT and UNKNOWN/invalid conditions.
2. Run the reference boundary checks — Both parser results are ALERT/1; the collector handles spaces in the output path and reports its own completeness.
3. Implement and test your extensions — Each claimed behavior has an observed pass/fail result and a bounded failure path.
4. Design database automation boundaries — The design states what the script can observe and which repairs remain operator decisions.
5. Review the final patch — Your changes are understandable and the reported checks are reproducible.

**Exercise-specific recovery:** Stop your own test processes and remove any added test cron entries. Keep the hardening patch and matrix; preserve real evidence and unrelated files.

**Instructor execution sheet:**
