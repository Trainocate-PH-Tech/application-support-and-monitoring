# Linux command desk reference

Examples assume GNU/Linux and synthetic training data. Substitute actual paths deliberately. `sudo` changes privilege; it does not make an incorrect target correct. Commands that change files, packages or services belong in the approved training workspace or supervised lab.

| Command | Useful support example | Interpretation / common trap |
|---|---|---|
| ssh | `ssh -i my-key.pem learner@host` | Authenticate as a named account; key possession does not imply root |
| sudo | `sudo systemctl status support-tomcat` | Use only granted operations; shell redirection happens before sudo |
| pwd / cd | `pwd`; `cd /var/log`; `cd -` | Absolute vs relative paths; cd affects this shell |
| ls | `ls -lah` | Hidden files and ownership; do not parse ls for arbitrary filenames |
| mkdir | `mkdir -p ~/support-lab/evidence` | Creates directories, not disk partitions |
| cp / mv | `cp -i -- 'status report.txt' work/` | Quote paths; -i asks before overwrite |
| rm | `rm -i -- ./disposable.txt` | Deletes a directory entry; open descriptors may retain data |
| touch | `touch new.log` | Creates an empty file or updates timestamps |
| chmod | `chmod 640 config.properties` | Owner read/write, group read, others none |
| chown | `sudo chown root:supportapp config.properties` | Ownership is distinct from mode and quota |
| ln | `ln -s status.txt latest` | A symlink stores a path and can dangle |
| id | `id`; `id -u` | Check current effective identity and refreshed groups |
| history | `history 10` | Useful locally; history may contain sensitive command arguments |
| printenv | `printenv PATH` | Inspect a named variable; avoid dumping all environment secrets |
| apt-get | `sudo apt-get install lsof` | Ubuntu; dnf is a Red Hat comparison, not interchangeable |
| find | `find . -xdev -type f -mmin -15 -print0` | Scope filesystem and time criteria; NUL preserves names |
| grep | `grep -n 'status=5[0-9][0-9]' application.log` | Exit 1 means no matches, 2 means error |
| awk | `awk '{print $1}' application.log` | Field parsing; define malformed-row behavior |
| sed | `sed -n '2,6p' application.log` | Prints a range; avoid -i on source evidence |
| cut | `cut -d, -f2 latency.csv` | Simple delimiter split, not general quoted CSV parsing |
| sort | `sort -n latencies.txt` | Numeric versus lexical order |
| uniq | `sort ids.txt \| uniq -c` | Counts adjacent groups; sorting changes chronology |
| wc | `wc -l application.log` | Counts newlines, not necessarily business requests |
| xargs | `find . -type f -print0 \| xargs -0 -r wc -c` | NUL input; -r avoids execution on empty input |
| less | `less application.log` | Search with /pattern, n for next, q to quit |
| tail | `tail -F application.log` | Follow name across replacement; Ctrl-C stops the viewer |
| head | `head -n 20 application.log` | A sample is not the whole incident window |
| tee | `check \| tee report.txt` | Writes screen and file; use pipefail to retain upstream failure |
| date | `date -u +%FT%TZ` | UTC timestamps reduce cross-system ambiguity |
| tar | `tar -tzf evidence.tar.gz` | Inspect member paths before extracting |
| gzip | `gzip -dc application.log.gz` | Decompress to stdout; does not package multiple files |
| systemctl | `systemctl cat support-tomcat` | Includes drop-ins; enable is different from start |
| journalctl | `journalctl -u support-tomcat --since '15 minutes ago' --utc` | Time window and privileges determine visible evidence |
| top | `top -b -n 1` | Point-in-time sample; compare intervals before declaring cause |
| ps | `ps -eo pid,user,comm,pcpu,pmem --sort=-pcpu` | Avoid unrestricted process arguments in evidence bundles |
| free | `free -h` | Available memory matters more than free alone |
| uptime | `uptime` | Load averages are not CPU percentages |
| df | `df -hT`; `df -i` | Bytes and inodes are different resources |
| du | `du -x -h --max-depth=1 /approved/path` | Privileges and mount boundaries affect totals |
| lsof | `sudo lsof +L1` | Finds open files with link count below one |
| pidstat | `pidstat 1 3` | Interval process statistics; requires sysstat package |
| lsblk | `lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS` | Device and partition sizes differ from filesystem capacity |
| findmnt | `findmnt -T /path` | Identifies the mount actually containing a path |
| quota | `quota -s` | User limits; missing output alone is not proof of absence |
| ss | `ss -lnt` | Local TCP listeners; does not prove remote reachability |
| curl | `curl --fail --max-time 5 -i URL` | HTTP status, transport error and response body are separate evidence |
| nc | `nc -vz -w 2 127.0.0.1 3306` | TCP reachability, not database authentication |
| ping | `ping -c 2 host` | ICMP can be filtered while application TCP works |
| traceroute | `traceroute -m 5 host` | Missing hop replies do not necessarily mean broken forwarding |
| nslookup / dig | `dig hostname`; `nslookup hostname` | Compare resolver, response code and intended name |
| cron / crontab | `crontab -l`; `crontab -e` | Minimal environment; absolute paths and overlap locks matter |

## Shell operators to explain before using

- `>` overwrites stdout destination; `>>` appends. `2>` redirects stderr; `2>&1` follows the current stdout destination, so order matters.
- `|` connects stdout to the next command's stdin; stderr is not automatically piped.
- `&&` runs the next command after success; `||` runs it after failure. `A && B || C` is not a general if/else substitute.
- `"$value"` preserves one argument; unquoted expansion may split and glob. Single quotes prevent expansion.
- `$(command)` substitutes captured stdout and strips trailing newlines. Capture `$?` immediately after the command whose result you need.
- A script needs an appropriate interpreter and readable content; direct execution also needs execute permission. `bash script.sh` and `./script.sh` are related but not identical invocations.

See the [18-task challenge bank](fixtures/command-challenges.md), [Bash manual](https://www.gnu.org/software/bash/manual/bash.html) and the installed `man` pages for option details.
