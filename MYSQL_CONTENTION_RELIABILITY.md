# MySQL Contention and Reliability Incidents

[Hands-on exercise](MYSQL_CONTENTION_RELIABILITY_EXERCISE.md) · [Module 2](module2/README.md)

**Environment:** Ubuntu Bash and MySQL 8.0/8.4. SQL blocks run at `mysql>`; Bash blocks run in the Linux shell. First follow [the diagnostic guide](MYSQL_SUPPORT_DIAGNOSTICS.md) to load `mysql_support_demo` and connect as `developer` with password `password` on the EC2 training host. No password belongs in a shell argument or submitted evidence. This account has administrator privileges; perform changes only in the explicitly labeled setup/change steps. Record UTC timestamps, host, version, and account with each capture.

## Section: Prepare writer and observer sessions

1. Use three distinct connections: writer A, writer B, observer C. The EC2 training administrator `developer` already has the writer and observer privileges needed below. Use the same login in three separate sessions; no extra grants are needed. For separate classroom writer accounts, the instructor can grant `SELECT, UPDATE` on `mysql_support_demo.orders` and provide observer diagnostics access.

   Open each writer and observer from a separate Bash terminal; enter `password` at the prompt:

   ```bash
   mysql -u developer -p mysql_support_demo
   ```
2. In each writer session:

   ```sql
   USE mysql_support_demo;
   SELECT CONNECTION_ID();
   SET SESSION innodb_lock_wait_timeout=30;
   ```

3. Record IDs and baseline amounts: order 1001 is 49.90; order 1002 is 120.00. Keep transactions open for less than a minute. The observer needs appropriate `PROCESS` and Performance Schema read access, provisioned by the administrator; insufficient visibility must be documented.

## Section: Observe a blocked session

1. Writer A locks one row:

   ```sql
   START TRANSACTION;
   UPDATE orders SET total_amount=total_amount+1 WHERE order_id=1001;
   ```

2. Writer B attempts the same row:

   ```sql
   START TRANSACTION;
   UPDATE orders SET total_amount=total_amount+1 WHERE order_id=1001;
   ```

3. While B waits, observer C runs:

   ```sql
   SELECT UTC_TIMESTAMP();
   SHOW FULL PROCESSLIST;
   SELECT w.REQUESTING_ENGINE_TRANSACTION_ID AS waiting_trx,
          rt.PROCESSLIST_ID AS waiting_session,
          bt.PROCESSLIST_ID AS blocking_session
   FROM performance_schema.data_lock_waits AS w
   LEFT JOIN performance_schema.threads AS rt ON rt.THREAD_ID=w.REQUESTING_THREAD_ID
   LEFT JOIN performance_schema.threads AS bt ON bt.THREAD_ID=w.BLOCKING_THREAD_ID;
   SELECT trx_id,trx_state,trx_started,trx_mysql_thread_id,trx_query
   FROM information_schema.innodb_trx;
   ```

4. Run `ROLLBACK;` in A, then in B after B returns or times out. A timeout need not roll back the entire transaction. Verify both original amounts.

**Expected:** B waits behind A; a blocker may be idle in the process list while holding an open transaction. Once cleanup completes, current wait rows disappear. See [data_lock_waits](https://dev.mysql.com/doc/refman/8.4/en/performance-schema-data-lock-waits-table.html).

## Section: Reproduce and inspect a deadlock

1. After completing the blocking cleanup, run in writer A:

   ```sql
   START TRANSACTION;
   UPDATE orders SET total_amount=total_amount+1 WHERE order_id=1001;
   ```

   Then run in writer B:

   ```sql
   START TRANSACTION;
   UPDATE orders SET total_amount=total_amount+1 WHERE order_id=1002;
   ```

2. In A, request B's row:

   ```sql
   UPDATE orders SET total_amount=total_amount+1 WHERE order_id=1002;
   ```

   While A waits, switch to B within 30 seconds and run:

   ```sql
   UPDATE orders SET total_amount=total_amount+1 WHERE order_id=1001;
   ```

   Execute these in separate terminals, not one combined script.
3. Expect one writer to receive error 1213. Either transaction can be selected as victim; do not assume B always loses. If instead a timeout occurs, roll back both and repeat with the correct ordering.
4. Observer C captures the latest deadlock promptly:

   ```sql
   SHOW ENGINE INNODB STATUS\G
   ```

5. Identify transaction IDs, held/requested locks, involved SQL, and victim. The latest deadlock is historical and can be replaced by another event. It is not necessarily a current wait.
6. Run `ROLLBACK;` in **both** writers, including the survivor. Verify order amounts 49.90 and 120.00, then close both sessions.

For real applications, evaluate consistent access order, shorter transactions, appropriate indexes, and bounded retry of the whole failed transaction with idempotency controls. Never retry a checkout blindly. See [InnoDB deadlocks](https://dev.mysql.com/doc/refman/8.4/en/innodb-deadlocks.html).

## Section: Diagnose replication and routing using supplied evidence

1. This repository does not configure a live replica. Start with the supplied JSON in Bash:

   ```bash
   jq . shared/fixtures/db-topics/mysql-contention/replica.json
   ```

2. On an actual authorized replica, the read-only SQL equivalent begins with:

   ```sql
   SELECT UTC_TIMESTAMP(), @@hostname, @@server_uuid, @@read_only, @@super_read_only;
   SHOW REPLICA STATUS\G
   ```

   `SHOW REPLICA STATUS` needs appropriate replication diagnostic privileges. An empty result on a standalone server is expected, not a failure. Capture each relevant channel on a multichannel deployment.
3. Read receiver and applier states independently. The fixture receiver is running, applier stopped, and error 1062 needs investigation. `Seconds_Behind_Source=NULL` is unknown, not zero. Even zero may not prove source freshness. See [SHOW REPLICA STATUS](https://dev.mysql.com/doc/refman/8.4/en/show-replica-status.html).
4. Treat `Relay_Log_File` as a DBA investigation reference. Relay logs contain received replication events pending/under application; a filename alone does not show their age or correctness. Do not delete files, reset replication, or skip a transaction.

## Section: Measure reporting freshness and user impact

1. Compare the fixture's primary last write at 03:04:50 with replica-visible write at 02:58:00: the visible-write gap is 410 seconds. At capture time 03:05:00, that replica-visible write is 420 seconds old. These are distinct measurements.
2. Identify the application's actual read/write endpoints and the affected report. Server read-only flags alone do not prove which endpoint the application uses.
3. Compare business freshness requirements against observed visibility. A report can be fast and stale at the same time.
4. Discuss temporarily routing affected reads to the writer only with the owning team: account for capacity, permissions, transaction semantics, and consistency expectations. Do not implement a routing change in this lab.
5. Report lock evidence and replication evidence as **separate incidents**. Include timestamps, affected operations, unavailable evidence, next investigation, and rollback confirmation for writer exercises.
