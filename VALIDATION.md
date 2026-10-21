# Validation report

## Content, difficulty and distribution revision — 21 October 2026

The reviewed curriculum now introduces Bash before the Day 1 incident, extends learner scripts on Day 3, labels core/demonstration/extension work and reserves 20 minutes within each 390-minute day for checkpoints. All 27 exercises include execution context, numbered actions, expected outcomes, repeat-run guidance, submissions and navigation. SQL concurrency exercises include session sequencing and rollback. Independent transfer tasks and a staged database-performance assessment replace repeated diagnosis-only patterns.

Validation for this revision:

- **24 automated checks pass:** 9 existing course checks, 7 guided-material checks and 8 revision regressions. The latter cover prerequisite/pacing consistency, learner health-script success and adverse cases, repeat-run preservation, multi-file syntax failures, exact slide/worksheet snippet agreement, both archive audiences and rendered PDF bounds.
- The health scaffold was exercised with controlled service/HTTP stubs: healthy, failed service, unavailable endpoint, extra arguments, empty service, invalid URL, missing tools and an argument containing spaces. Invalid empty arguments were corrected after a failing regression test.
- All three 50-slide decks and corresponding PDFs were rebuilt. All 150 pages were checked for off-page text and reviewed in contact sheets; revised diagrams and command slides were inspected at readable scale. Diagram examples are labeled illustrative where appropriate.
- Both distributions were rebuilt. The student archive contains all 27 exercises, required SQL references and executable shell scripts, with local links resolving inside the archive. It excludes instructor directories, setup/fault tooling, concealed answer cards and authoring sources. PowerPoint notes are replaced with learner-only guidance. ZIP integrity and private-key exclusions pass.
- The instructor master retains original runnable application assets and integration tooling, plus the revised lesson sources, execution sheets, rubric, rotation schedule and beginner-pilot checklist.

No EC2 changes, privileged administration or new application/database integration runs were performed for this revision. Existing application/reference-script behavior is unchanged; new shell teaching examples were checked in temporary workspaces with controlled probes. Original integration results below remain historical evidence. Classroom pacing, live installation, quotas/storage growth and per-learner independent administration still require an instructor rehearsal or timed pilot; they are not established by automated checks.

## Earlier guided Markdown revision

All 27 exercises now use numbered walkthroughs with explicit execution context, commands beside their instructions, expected outcomes, troubleshooting checks, submission checklists and exercise-specific recovery. Shared account/terminal setup, the 18-task command challenge bank and instructor storage demonstrations were revised alongside them. Final assessments provide guided setup and optional hints while leaving diagnosis independent.

Review corrections include implicit working-directory transitions, missing public-key/client-file steps, SQL hidden in commented Bash, unlabelled expected failures, ambiguous multi-session lock sequencing and blanket cleanup directions. SQL Server Session B now uses an explicit transaction with its own rollback, including after a timeout. The linked SQL worksheet matches that sequence. The retention walkthrough applies deletion only under a temporary HOME containing dummy files.

Verification for this revision:

- 9 existing course/script checks and 7 guided-material checks pass (16 total).
- Every exercise matches its authored walkthrough, has consecutive step numbers, and retains the 390-minute daily agenda and required/extension distinction.
- Bash command blocks in all exercises, the terminal guide and storage procedures pass syntax checking. SQL uses SQL fences rather than commented shell commands; escaped newlines are preserved for readable copy/paste.
- Nonprivileged file-navigation, unusual-filename archive/pipeline and isolated-retention walkthroughs were executed in temporary workspaces and produced the documented results.
- Local Markdown links pass; CommonMark parsing and regeneration consistency were checked. Regenerating Markdown preserves the revised handouts and leaves the slide-deck bytes unchanged.
- The ZIP was refreshed with the guided materials and authoring source; private keys remain excluded.

No EC2 changes, privileged storage demonstrations, account provisioning or cron installation were performed during this revision. Database and application runtime checks listed below belong to original authoring; they were not rerun solely for the Markdown rewrite. The revised host-administration procedures still require instructor rehearsal on the intended training hosts.

## Original authoring validation

Authoring validation performed on 20 October 2026. No installation, fault injection or storage changes were made to the training EC2 server. The earlier EC2 inspection was read-only.

## Completed checks

- **Three PowerPoint decks:** 50 slides each, 150 total; speaker notes on every slide. All decks opened and converted successfully with LibreOffice. Representative cover, agenda, lesson, command and challenge slides were visually reviewed. Rendered text was checked for off-page bounds; no off-page text was detected.
- **Course structure:** 27 exercise Markdown files, three instructor guides plus shared procedures, required outputs and outline coverage. Each daily agenda totals 390 instructional minutes; extension tasks are outside that budget. Actual classroom timing still needs rehearsal.
- **Local automated checks:** 9 test cases passed, covering shell syntax, deck dimensions/notes, local Markdown links, parser expected results and boundary cases, health-check failures/timeouts via stubs, partial evidence/redaction, pipeline alert handling and narrowly scoped retention.
- **ShellCheck 0.11.0:** all 11 reference shell scripts pass without findings. The learner starter also passes syntax checking.
- **Application build:** Maven 3.9.9 built the WAR with compiler release 17. Dependencies are pinned in pom.xml. The prebuilt WAR is included under shared/app/releases.
- **Tomcat/MySQL integration:** 16 checks passed in disposable local Docker containers using Tomcat 10.1.61 / Java 17 and MySQL 8.4.11. Checked 100,000-row seeding, JDBC readiness, player/report results, request IDs, invalid/missing IDs, payment and DB-auth faults, 1.5-second latency, configuration recovery, index plan comparison, diagnostic SQL, deadlock reproduction/cleanup and absence of the generated password in app logs. Testing exposed a temporary-table seed-query limitation; the final seed uses a reusable CTE and passes.
- **SQL Server integration:** schema, 100,000 rows, bounded workload, DMV/plan/wait/statistics diagnostics, Query Store capture, intentional SQL Agent job failure, observed blocking/timeout and rollback recovery passed on SQL Server 2022 Developer 16.0.4305.5 (CU27-GDR), Ubuntu 22.04.5 container. All 9 SQL Server integration checks passed, including execution of diagnostics as the learner role. Testing caught a SQL Agent startup race and a job-history permission mismatch; setup is now resumable and learner diagnostics use the supported job-history procedure instead of direct msdb base-table access.
- **Synthetic fixtures:** clearly labeled; application parser yields 6 valid requests, 2 server errors, 33.33% error rate, 2 slow requests and 1 malformed record. SQL Server duration/CPU units and wait capture intervals are explicit.
- **Isolation:** disposable integration containers/networks are removed by test cleanup. Course packaging explicitly excludes private keys, credentials, build caches and intermediate target directories.

## Not validated on the actual classroom hosts

The Ubuntu apt/systemd installer, systemd fault overrides, OS account creation, per-user quotas, loop-device partition growth, EBS console actions and final cron installation require instructor rehearsal on the dedicated training infrastructure. The container tests validate application/database behavior, not the host-level installer or Linux storage procedures. No end-to-end privileged storage test was performed on the authoring workstation.

SQL Server package installation on the future training VM was not executed; the SQL content was tested against the selected engine/platform family in a container. Record the exact installed classroom package versions after provisioning. Performance magnitude varies with host capacity; the provided synthetic evidence supplies deterministic regression/high-CPU interpretations when live timing is inconclusive.

The current EC2 host has about 2 GB RAM; the shared classroom baseline remains 8 GB for the application host and a separate SQL Server host. Do not treat successful local tests on a larger workstation as proof that the smaller EC2 host supports concurrent class workloads.

## Reproduce

```bash
python tools/build_course.py
python tools/test_course.py
shellcheck shared/scripts/*.sh
# Build WAR before opt-in integration checks:
mvn -B -f shared/app/pom.xml clean package
python tools/test_app_docker.py
python tools/test_sqlserver_docker.py
python tools/package_course.py
```

Docker integration tests require the images documented in their source and create only temporary local training containers. Review scripts before running. They never use the README EC2 address or key.
