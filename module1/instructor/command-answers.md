# Linux command challenge answer key

These are GNU/Linux examples. Accept alternatives that preserve the input and explain their assumptions. Run from the extracted fixture directory.

1. `monitor-log.sh application.log` reports 6 valid, 2 errors, 1 malformed. Naive ERROR finds 3 lines because a successful request contains the word in a note. Parse `status=` and numeric latency explicitly.
2. `awk '{for(i=1;i<=NF;i++) if($i~/^path=/) print $i}' application.log | sort | uniq -c | sort -k1,1nr -k2,2` gives player 3, remaining paths 1 each.
3. `tail -n +2 latency.csv | cut -d, -f2 | sort -n` gives 5,25,30,80,1500,2100. This fixture has no quoted commas; general CSV needs a real parser.
4. Extract only `request_id=` fields, `sort -u`, then count. Result 6; real multi-line request logging needs deduplication and format validation.
5. `find filenames -type f -print0 | xargs -0 -r ls -ld --`. NUL is the delimiter; names cannot contain NUL.
6. `find filenames -type f -print0 | tar --null -T - -czf selected.tar.gz`; list, extract into a new directory and compare content/name sets. Human-readable listings may escape newlines.
7. `cat -- filenames/-dangerous-name.txt` or use a path beginning `./`.
8. Without pipefail, wc usually exits 0 and the pipeline status is 0. With pipefail, grep's 1 means no match; grep 2 means an execution error. Record `$?` immediately.
9. wc counts one newline, so returns 1. `awk 'END {print NR}'` returns 2 records for this input. Define what constitutes an empty final record.
10. uniq groups adjacent equal lines; `sort | uniq -c` groups all identical lines but changes order. Preserve original order if chronology matters.
11. tail -f follows the descriptor; tail -F follows the name with retry. Rename a disposable log, create a replacement and append to both; observe behavior, then Ctrl-C.
12. The invoking shell opens the redirection target before sudo echo runs. A scoped `printf '%s\n' value | sudo tee /approved/path` changes who opens the file; it does not authorize arbitrary writes.
13. `find . -xdev -type f -mmin -15 -print`. mtime reflects content changes; ctime reflects inode metadata changes and is not creation time.
14. For normalized equal-format UTC timestamps, `awk '$1 >= "2026-10-20T01:00:01Z" && $1 < "2026-10-20T01:00:04Z"' application.log`. Mixed offsets, timestamp precision and multiline records need normalization/record-aware parsing.
15. `findmnt -T path`, `df -hT path`, `df -i path`, privileged `du -x`, `lsof +L1`, quota evidence and mount inspection. Do not delete arbitrary files before identifying ownership and recovery effects.
16. Use absolute paths and controlled PATH, inspect executable permissions/interpreter, set working directory explicitly and test under `env -i`. Do not dump secrets from environment variables.
17. `while IFS= read -r -d '' f; do printf '%s\n' "$f"; done < <(find filenames -type f -print0)`. This is Bash-specific. Word splitting and glob expansion break naive loops.
18. `set -o pipefail; your_check | tee "$HOME/support-lab/evidence/report.txt"; rc=$?` preserves upstream failure. Ensure your_check is a real command, output destination is new/approved and stderr capture is deliberate.

Bonus: tar packages records; gzip compresses a stream. curl may return 0 for HTTP 500 without --fail. ss shows listeners, nc tests TCP, ping tests ICMP and a SQL query tests authentication/database execution; none substitutes for all the others.
