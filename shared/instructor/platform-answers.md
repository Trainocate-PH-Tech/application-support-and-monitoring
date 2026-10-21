# Synthetic platform incident cards

These are authored evidence, not output collected from the training EC2 server. For each card: state facts, probable layer, one discriminating check, a mitigation with rollback and a recovery test. Do not execute Windows or SELinux commands on Ubuntu merely because they appear here.

## DNS

At 01:10 UTC `dig db.training.invalid` returns NXDOMAIN. `nc -vz -w 2 10.20.0.15 3306` succeeds. The app URL contains `db.training.invalid`; the deployment changed it from `mysql.training.internal`. Question: what does the TCP result prove, and what does it not prove? Next checks: effective configuration and the intended resolver/name. Fix the verified name, not a permanent unreviewed hosts-file workaround. `.invalid` deliberately cannot resolve publicly.

## TLS

At 01:15 UTC curl to the synthetic payment endpoint reports certificate expiry. A captured certificate has `notAfter=Oct 19 23:59:59 2026 GMT`; server time is Oct 20 UTC. A TCP check to 443 succeeds. Confirm time, SNI/hostname, chain and certificate ownership. Renew/deploy the correct certificate and verify with normal trust validation. `curl -k` bypasses verification and is not a repair.

## SELinux on Red Hat

Mode: Enforcing. File mode: 640, owner tomcat:tomcat. Audit evidence: `avc: denied { read } ... comm="java" name="app.properties" ... tcontext=unconfined_u:object_r:default_t:s0`. Ordinary UNIX permissions appear compatible. Inspect the intended path/context with `ls -Z`, policy documentation and `ausearch -m AVC -ts recent`. Restore the appropriate policy-backed labeling after review; do not guess a type or disable enforcement. Ubuntu's supplied host does not demonstrate this SELinux policy.

## IIS + SQL Server blocking

At 01:20 UTC IIS requests to `/loyalty` return 200 but `time-taken` rises from 80 to 8000 ms. App worker CPU is 12%; SQL host CPU is 18%. Request 74 waits on LCK_M_X with blocking_session_id 61. Session 61 is sleeping, open_transaction_count=1, last command is an update from a deployment tool. App logs show pool checkout delay 7000 ms. A sleeping session can hold locks; inspect its transaction and ownership before coordinating rollback. Restarting IIS alone may only clear waiting clients. Validate lock release, pool recovery and request latency.

## SQL Server high CPU

Two interval samples show host SQL process CPU 92% and 94%. Query 17 executed 400 times in one minute, avg CPU 120,000 microseconds, avg duration 140,000 microseconds, plan 8. Baseline was 100 executions/minute, avg CPU 20,000 microseconds, plan 3. Estimated plan 8 scans 100,000 rows; plan 3 seeks about 1,000. These are synthetic plan summaries, not actual XML plans. Increased call rate and per-call work both contribute. Check deployment, parameters, statistics and logical reads; do not infer a single cause from CPU alone. A real plan is available from the live diagnostics CROSS APPLY query.

## CPU versus I/O

Load average is 8 on a 2-vCPU host; sampled user CPU is 8%, I/O wait is 60%, and many tasks are in D state. This is not evidence of an arithmetic CPU hot loop. Investigate storage latency and blocked I/O with available tools, workload context and provider metrics. `top` alone is not a complete root-cause analysis.
