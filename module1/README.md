# Module 1: Linux Fundamentals and Incident Triage

One training day: 390 instructional minutes, 60-minute lunch and two 15-minute breaks. Advanced extensions are optional. Teams have 3–4 learners; rotate roles and schedule shared service changes.

[PowerPoint deck](Module1.pptx) · [Learner setup](../shared/learner-start.md) · [Assessment rubric](../shared/assessment-rubric.md)

## Agenda
| Exercise | Instructional minutes |
|---|---:|
| [Access, identity and user creation](exercises/01-access-users.md) | 40 |
| [Navigation, files and package installation](exercises/02-files-packages.md) | 60 |
| [Allocate space and diagnose disk limits](exercises/03-storage.md) | 45 |
| [Command investigations and first Bash script](exercises/04-command-investigations.md) | 75 |
| [Install and inspect the application stack](exercises/05-install-stack.md) | 50 |
| [Service failures and application log diagnosis](exercises/06-service-log-triage.md) | 35 |
| [Resource and network troubleshooting](exercises/07-resources-network.md) | 25 |
| [Linux incident challenge with your evidence script](exercises/08-first-script-capstone.md) | 40 |
| [Advanced Linux command challenge bank](exercises/09-command-challenge-bank.md) | Extension |
| Checkpoints and recovery reserve | 20 |

The exercise blocks total 370 minutes. Use two 10-minute checkpoints to review evidence, recover interrupted work and confirm readiness. Demonstrations and extensions are labeled in each exercise; extensions do not displace the final assessment.

## Before starting
Read the [learner terminal/setup guide](../shared/learner-start.md). Each exercise now includes numbered actions, execution context, expected results and specific cleanup. Final challenges retain independent diagnosis with optional hints.

Use the course repository root for commands unless the exercise changes directory. Copy evidence into `~/support-lab`, never edit original fixtures. Commands marked instructor require the instructor; students do not need blanket sudo. Use individual SSH credentials. Modules 2 and 3 build on the prior day's application and evidence skills.

## Completion
Submit the deliverables listed in each required exercise. Keep passwords, private keys and unreviewed sensitive logs out of submissions. Distinguish synthetic evidence from live observations. The instructor scores evidence, diagnosis, recovery, automation and communication using the shared rubric.
