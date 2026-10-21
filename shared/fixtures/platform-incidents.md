# Synthetic platform evidence cards

These captures are fictional, not collected from EC2. Work on one card during the core resource/network lesson; use the others as extensions. Do not execute Windows or SELinux commands on Ubuntu.

For each card, submit: facts and UTC window; two possible explanations; one discriminating check with a predicted outcome for each explanation; a scoped proposed correction with rollback; and a business recovery test. Missing evidence remains unknown. Instructor interpretation is supplied after the attempt.

## DNS

At 01:10 UTC, `dig db.training.invalid` returns NXDOMAIN. A TCP connection to `10.20.0.15:3306` succeeds. The deployed database URL uses `db.training.invalid`; the previous release used `mysql.training.internal`. The `.invalid` suffix is reserved for this synthetic scenario.

What does the TCP observation establish? Which effective configuration and resolver evidence would you request before proposing a change?

## TLS

At 01:15 UTC, curl to the synthetic payment endpoint reports certificate expiry. The captured certificate has `notAfter=Oct 19 23:59:59 2026 GMT`; the sampled client clock is Oct 20 UTC. TCP 443 connects. No server clock or SNI capture has been supplied.

Which missing observations distinguish an incorrect clock from the wrong or expired certificate? How will your recovery test preserve trust verification?

## SELinux on Red Hat

Mode: Enforcing. The configuration file is mode 640, owner tomcat:tomcat. An audit entry contains `avc: denied { read } ... comm="java" name="app.properties" ... tcontext=unconfined_u:object_r:default_t:s0`. The service's effective groups and the intended path policy have not been captured.

Which two permission mechanisms need separate evidence? What observation would justify a labeling change?

## IIS and SQL Server

At 01:20 UTC, `/loyalty` returns 200 while IIS time-taken rises from 80 to 8000 ms. App CPU is 12%; SQL host CPU is 18%. Request 74 waits on LCK_M_X with blocking_session_id 61. Session 61 is sleeping with open_transaction_count=1; its last command is a deployment-tool update. App logs show pool checkout delay 7000 ms.

Draw a possible causal timeline. Which transaction owner and resource observations would you request before a recovery action? Is HTTP 200 sufficient proof of recovery?

## SQL Server CPU

Two samples show SQL process CPU 92% and 94%. Query 17 ran 400 times in a minute with average CPU 120,000 microseconds, duration 140,000 microseconds and plan 8. Baseline: 100 calls/minute, CPU 20,000 microseconds, plan 3. Synthetic plan summaries show a 100,000-row scan versus a 1,000-row seek; no XML plan is supplied.

Quantify changes in call rate and work per call separately. What measurements would distinguish a workload change from a plan regression?

## CPU and I/O

A two-vCPU host has load average 8, sampled user CPU 8%, I/O wait 60% and many tasks in D state. No storage latency or provider metrics are supplied.

State a hypothesis supported by the samples and an alternative. Which observation is needed before recommending more CPU?
