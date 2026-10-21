# Application Support and Monitoring

Three training days for beginner-to-intermediate application support teams. Each day includes **390 instructional minutes**, a one-hour lunch and two 15-minute breaks. Advanced challenge banks are optional extensions.

| Day | Slides | Exercises and agenda |
|---|---|---|
| 1 — Linux fundamentals and incident triage | [PowerPoint](module1/Module1.pptx) · [PDF](module1/Module1.pdf) | [Module 1](module1/README.md) |
| 2 — MySQL and SQL Server diagnostics | [PowerPoint](module2/Module2.pptx) · [PDF](module2/Module2.pdf) | [Module 2](module2/README.md) |
| 3 — Automation and major incidents | [PowerPoint](module3/Module3.pptx) · [PDF](module3/Module3.pdf) | [Module 3](module3/README.md) |

[Instructor/master package](Application-Support-Training.zip) · [Student package](Application-Support-Student.zip). The master includes answers, authoring sources, setup tooling and the tested WAR. Distribute the student package to learners: it includes exercises, practice references and decks with sanitized speaker notes. Both exclude private keys. Keep the master directory inaccessible to learner accounts.

## Start here

- Instructor: [setup and delivery](shared/instructor/setup-and-delivery.md), [storage labs](shared/instructor/storage.md), [separate SQL Server setup](shared/instructor/sqlserver-setup.md), [scenario cards and rubric](shared/instructor/scenarios.md).
- Learner: read the [terminal/setup guide](shared/learner-start.md), then start with Module 1 exercise 01; use individual SSH credentials and save work under `~/support-lab`.
- Reference: [Linux command desk reference](shared/linux-command-reference.md), [outline coverage](COVERAGE.md), [technical sources](shared/SOURCES.md), [validation report](VALIDATION.md).
- Software: [sample application](shared/app/README.md), [script interfaces](shared/scripts/README.md), [synthetic fixtures](shared/fixtures/README.md), [report templates](shared/templates/incident-report.md).

All fixtures represent fictional training incidents. The package contains setup tools but does not provision cloud resources automatically. Privileged shared-host changes are instructor-controlled. Use the student archive for learner distribution; the root PowerPoint decks are instructor editions. Each day schedules 370 minutes plus 20 minutes for checkpoints and recovery. Required practice, demonstrations and optional extensions are labeled.

## Test server

The test server is hosted at AWS. The original instructor connection is:

```bash
chmod 600 okada.pem
ssh -i okada.pem ubuntu@47.131.221.162
```

`ubuntu` is a sudo-capable account, **not the root account**. Keep the private key on the instructor workstation and do not distribute it with course materials. Learners use their own accounts and keys, created during the supervised access exercise.

The inspected host has Ubuntu 26.04, about 2 GB RAM and a 120 GB disk with an expanded root filesystem. Recheck before delivery. The recommended shared classroom application host has 8 GB RAM; SQL Server uses a separate supported host. The present storage layout does not prove why a user previously ran out of space; the course distinguishes quota, permission, inode, filesystem and partition issues.

## Rebuild course assets

```bash
python -m pip install -r tools/build-requirements.txt
python tools/build_course.py
# Markdown-only updates without rebuilding decks:
python tools/build_course.py --documents-only
python tools/test_course.py
python tools/test_guided_materials.py
python tools/render_decks.py
python tools/package_course.py
python tools/test_revision.py
```

The slide outline source is `tools/build_course.py`; the 27 guided walkthroughs are authored in `tools/guided_exercises.py`. Reviewed pacing, shared command snippets and additional activities are in `tools/revise_curriculum.py`, applied before rendering both slides and handouts. The exported `course-content.json` is for outline inspection. Markdown-only regeneration preserves slide files and fixtures. Rebuilding regenerates decks, exercise Markdown, module guides and synthetic fixtures. It does not overwrite the separate instructor procedures, application code or validation report. PowerPoint speaker notes contain detailed delivery guidance and answer reasoning.

See the [learner-visible rubric](shared/assessment-rubric.md) for partial-credit anchors and individual checks. Beginner timing still needs the instructor’s timed pilot; automated validation does not establish teaching effectiveness.
