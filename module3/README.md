# Module 3: Automation and Major Incident Simulation

One training day: 390 instructional minutes, 60-minute lunch and two 15-minute breaks. Advanced extensions are optional. Teams have 3–4 learners; rotate roles and schedule shared service changes.

[PowerPoint deck](Module3.pptx) · [Learner setup](../shared/learner-start.md) · [Assessment rubric](../shared/assessment-rubric.md)

## Agenda
| Exercise | Instructional minutes |
|---|---:|
| [Extend your Bash script into a health check](exercises/01-bash.md) | 60 |
| [Automated evidence collection](exercises/02-evidence.md) | 55 |
| [Log parsing and threshold monitoring](exercises/03-monitoring.md) | 40 |
| [Slow-query summaries and correlation pipelines](exercises/04-slow-pipeline.md) | 20 |
| [Health checks, cron and safe retention](exercises/05-scheduling.md) | 35 |
| [Deployment verification and maintenance boundaries](exercises/06-deployment-checks.md) | 20 |
| [Major incident simulation](exercises/07-war-room.md) | 110 |
| [Final challenges and operational handover](exercises/08-handover.md) | 30 |
| [Advanced automation challenge bank](exercises/09-automation-extension.md) | Extension |
| Checkpoints and recovery reserve | 20 |

The exercise blocks total 370 minutes. Use two 10-minute checkpoints to review evidence, recover interrupted work and confirm readiness. Demonstrations and extensions are labeled in each exercise; extensions do not displace the final assessment.

## Before starting
Read the [learner terminal/setup guide](../shared/learner-start.md). Each exercise now includes numbered actions, execution context, expected results and specific cleanup. Final challenges retain independent diagnosis with optional hints.

Use the course repository root for commands unless the exercise changes directory. Copy evidence into `~/support-lab`, never edit original fixtures. Commands marked instructor require the instructor; students do not need blanket sudo. Use individual SSH credentials. Modules 2 and 3 build on the prior day's application and evidence skills.

## Completion
Submit the deliverables listed in each required exercise. Keep passwords, private keys and unreviewed sensitive logs out of submissions. Distinguish synthetic evidence from live observations. The instructor scores evidence, diagnosis, recovery, automation and communication using the shared rubric.
