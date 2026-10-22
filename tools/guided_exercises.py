"""Authored walkthroughs, separate from slide outlines; consumed by build_course.py."""
GUIDES={}
def step(title,where,action,code='',expected='',trouble='',language='bash'):
    return dict(title=title,where=where,action=action,code=code,expected=expected,trouble=trouble,language=language)
def guide(m,n,prerequisites,steps,cleanup,files,challenge=False):
    GUIDES[m,n]=dict(prerequisites=prerequisites,steps=steps,cleanup=cleanup,files=files,challenge=challenge)
S=step
L='Learner · application server · Bash terminal'
I='Instructor · application server · Bash terminal'
W='Learner · local workstation · Bash terminal'
SQL='Learner · application server · interactive MySQL client'
TSQL='Learner · SQL Server query window (T-SQL)'

guide(1,1,'Instructor access through the supplied key; a unique learner account name and team name assigned by the instructor; a workstation with OpenSSH. No existing learner login is required.',[
S('Generate your own SSH key',W,'Run this only if this course-specific key does not already exist. Accept a passphrase and keep the private file on your workstation. Send only the displayed public key to the instructor.',
r'''ssh-keygen -t ed25519 -f "$HOME/.ssh/support_lab_ed25519"
cat "$HOME/.ssh/support_lab_ed25519.pub"''','Two key files exist; only the .pub file is shared.','If asked to overwrite a key, answer no and ask the instructor to confirm which existing key to use.'),
S('Open the instructor session','Instructor · local workstation → application server','Using the instructor key at ~/pem/okada.pem, connect. The following steps run on the server after login.',
r'''chmod 600 ~/pem/okada.pem
ssh -i ~/pem/okada.pem ubuntu@47.131.221.162
whoami
id
hostname
date -u +%FT%TZ''','whoami reports ubuntu, not root. Hostname and timestamp depend on the server.','If SSH fails, check the key path, network access and host identity with the instructor; do not change the key permissions on a shared copy.'),
S('Create the learner and team',I,'The instructor enters the assigned names at the prompts. Keep these variables in this terminal for the next two steps. Use a new account for each learner.',
r'''read -r -p 'Assigned learner name: ' learner
read -r -p 'Assigned team group: ' team
sudo adduser --disabled-password --gecos '' "$learner"
sudo groupadd -f "$team"
sudo usermod -aG "$team" "$learner"
sudo chmod 750 "/home/$learner"
sudo install -d -m 700 -o "$learner" -g "$learner" "/home/$learner/.ssh"''','The account and home directory exist; no unrestricted sudo grant is added.','If the account already exists, stop and inspect id ACCOUNT rather than recreating or replacing its files.'),
S('Install the public key',I,'Paste the learner’s single public-key line at the prompt. These instructions assume the newly created account has no existing authorized_keys file.',
r'''read -r -p 'Learner PUBLIC key (one line): ' learner_public_key
printf '%s\n' "$learner_public_key" | sudo tee "/home/$learner/.ssh/authorized_keys" >/dev/null
sudo chown "$learner:$learner" "/home/$learner/.ssh/authorized_keys"
sudo chmod 600 "/home/$learner/.ssh/authorized_keys"
sudo stat -c '%U %G %a %n' "/home/$learner/.ssh" "/home/$learner/.ssh/authorized_keys"''','Directory mode is 700 and key-file mode is 600; both belong to the learner.','Stop if the pasted text starts with BEGIN PRIVATE KEY or contains multiple lines. Never install a private key here.'),
S('Connect with your own account',W,'Open a second workstation terminal. Enter your assigned account name; leave the instructor session open.',
r'''read -r -p 'Your assigned learner account: ' learner
ssh -i "$HOME/.ssh/support_lab_ed25519" "$learner@47.131.221.162"
whoami
id
printf 'HOME=%s\n' "$HOME"''','The new SSH session identifies your learner account and team group.','If a recently added group is missing, reconnect. If authentication fails, the instructor checks the public key, ownership and SSH server logs.'),
S('Create private evidence and confirm access',L,'You are now in your learner SSH session. Run the checks, then ask the instructor to test access from a different learner account.',
r'''mkdir -p ~/support-lab/evidence/m1-01
umask 077
printf 'private lab note\n' > ~/support-lab/private.txt
stat -c '%U %G %a %n' ~/support-lab/private.txt
id > ~/support-lab/evidence/m1-01/identity.txt
date -u +%FT%TZ >> ~/support-lab/evidence/m1-01/identity.txt''','The private file is mode 600; an unrelated learner cannot read it.','If mode differs, set chmod 600 on this file and inspect umask. Changing permission does not change disk capacity.'),
S('Perform the second-user check',I,'Use the account variables retained in the instructor session. Enter a different learner account that exists.',
r'''read -r -p 'A different learner account: ' other
sudo -u "$other" cat "/home/$learner/support-lab/private.txt"''','Permission denied is the intended result. Record it; do not loosen permissions to make this check succeed.','If contents are readable, inspect both the directory modes and file ownership before continuing.')],
'Leave learner accounts and keys in place for subsequent exercises. Close only redundant sessions with exit. Do not delete accounts or remove SSH access during class.',
['identity.txt — learner identity and UTC timestamp','access-notes.md — permission results and answers to the challenge questions'])

guide(1,2,'Complete learner access. The instructor has supplied the absolute course folder; shared/fixtures/support-fixtures.tar.gz is readable.',[
S('Create and navigate your workspace',L,'Use a fresh practice directory; if it already contains previous work, rename it before repeating the exercise.',
r'''mkdir -p ~/support-lab/files-practice/{incoming,work,archive}
cd ~/support-lab/files-practice
pwd
ls -lah
cd /var/log
pwd
cd -''','You return to ~/support-lab/files-practice. cd - prints the previous directory.','Run pwd before any relative path operation; cd affects this terminal only.'),
S('Create, copy and rename a file',L,'Keep the filename quoted because it contains a space.',
r'''printf 'alpha\nbeta\n' > 'incoming/status report.txt'
cp -i -- 'incoming/status report.txt' work/
mv -- 'work/status report.txt' work/status.txt
head -n 1 work/status.txt
ln -s status.txt work/latest
ls -l work
readlink work/latest''','head prints alpha; latest points to status.txt.','If ln reports File exists on a repeat attempt, inspect the existing link instead of overwriting it blindly.'),
S('Inspect packages and command lookup',I,'Learners observe this shared-host package change. Explain that apt-get update refreshes package metadata, then install the named diagnostic packages.',
r'''sudo apt-get update
apt-cache search '^lsof$'
sudo apt-get install -y curl netcat-openbsd dnsutils lsof sysstat
dpkg-query -S /usr/bin/lsof''','Installation completes or reports the packages already installed; package ownership is printed.','If apt fails, resolve repository/network/lock errors before proceeding; learners should not start parallel package installations.'),
S('Check the tools as a learner',L,'Return to the course directory explicitly before using shared paths.',
r'''cd "$COURSE_ROOT"
printf '%s\n' "$PATH"
command -v curl nc dig lsof pidstat
tar -tzf shared/fixtures/support-fixtures.tar.gz
mkdir -p ~/support-lab/fixtures
tar -xzf shared/fixtures/support-fixtures.tar.gz -C ~/support-lab/fixtures''','Tool paths print; the archive contains application.log, latency.csv and filenames/.','If the archive is missing, confirm COURSE_ROOT rather than guessing a relative directory.'),
S('Compress a copy and observe a broken link',L,'Remove only the practice target you created. Answer y to its deletion prompt.',
r'''printf 'compress me\n' > ~/support-lab/files-practice/work/compression.txt
gzip -k ~/support-lab/files-practice/work/compression.txt
gzip -dc ~/support-lab/files-practice/work/compression.txt.gz
rm -i -- ~/support-lab/files-practice/work/status.txt
ls -l ~/support-lab/files-practice/work/latest
cat ~/support-lab/files-practice/work/latest''','gzip prints compress me; the final cat fails because the link’s target was removed. That failure is expected.','If gzip asks to overwrite an existing archive during a repeat, inspect your previous output first.')],
'Keep ~/support-lab/fixtures for later exercises. Leave the broken link as evidence or remove that link only with rm -i; retain the original incoming file.',
['file-notes.md — directory navigation, package paths, archive listing and broken-link explanation'])

guide(1,3,'Instructor has installed parted, quota and cloud-guest-utils. Reserve the shared storage lab; no other team may use its disposable mounts at the same time.',[
S('Record the actual limiting layer',L,'Capture your identity and filesystem inventory before accepting the phrase “user disk cap” as a diagnosis.',
r'''id
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS
findmnt -T "$HOME"
df -hT "$HOME"
df -i "$HOME"
quota -s''','You can identify the device, filesystem, byte usage and inode usage. quota may report no configured limit or a missing tool.','Missing quota output is not proof that every filesystem is quota-free. Ask the instructor to inspect quota configuration.'),
S('Inspect privileged storage evidence',I,'Do not change the root filesystem. Explain what each result can and cannot establish.',
r'''sudo repquota -a
sudo lsof +L1''','Results may be empty on a healthy host; deleted-open files, if present, have link count below one.','If permission or tooling prevents a check, record it as unavailable, not as a healthy result.'),
S('Create the disposable partition lab',I,'From COURSE_ROOT, read the helper and run its create operation. Record the loop device printed by the script.',
r'''cd "$COURSE_ROOT"
less shared/scripts/storage-lab.sh
sudo shared/scripts/storage-lab.sh create
sudo lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS
sudo df -hT /var/lib/support-storage-lab/mount''','A roughly 192 MiB image is mounted at the lab path; root storage remains separate.','If the lab already exists, stop and check whether another team owns it. Never substitute a root-disk device.'),
S('Grow and compare capacity',I,'Read the grow branch aloud: image/device capacity, partition growth, then ext4 growth. The helper runs these stages consecutively; it does not pause interactively.',
r'''sudo shared/scripts/storage-lab.sh grow
sudo lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS
sudo df -hT /var/lib/support-storage-lab/mount''','The disposable image is 320 MiB and its filesystem capacity increases; df is smaller than raw device size because of metadata.','If growth fails, keep the device mounted for inspection and record the failing stage; do not rerun commands against another device.'),
S('Observe quota and deleted-open-file demonstrations','Instructor performs; learners record observations','Follow the numbered procedures in [Storage demonstrations](../../shared/instructor/storage.md). Complete quota allocation and deleted-open-file demonstrations one at a time. Learners fill a table: symptom, df bytes, df inodes, quota result, diagnosis and correction.',expected='Quota enforcement can reject a learner write despite free filesystem space. Deleted-open data can consume space after its filename disappears.',trouble='If the instructor cannot reproduce the required condition, record the limitation. Do not claim the demonstration succeeded.'),
S('Explain the real EBS sequence','Team discussion; no AWS changes','Use the EBS section of the storage guide to draw volume → partition → filesystem. Add quota/user permissions as separate checks. Explain how the procedure differs for ext4, XFS and LVM.',expected='Your decision tree chooses a fix only after identifying the limiting layer.',trouble='Do not infer the historical EC2 problem from today’s expanded filesystem alone.')],
'Instructor runs sudo shared/scripts/storage-lab.sh cleanup after evidence is saved. Follow each demonstration’s own quota/image cleanup. If unmount reports busy, find the open process and close it before retrying; never delete a mounted image.',
['storage-before-after.txt — observed capacities and quota results','storage-decision-tree.md — diagnosis sequence and EBS explanation'])

guide(1,4,'The extracted fixtures from Module 1 exercise 02 are available. No root access is needed.',[
S('Inspect the evidence without editing it',L,'Start in the extracted fixture directory; q leaves less.',
r'''cd ~/support-lab/fixtures
less application.log
head -n 4 application.log
tail -n 4 application.log
wc -l application.log''','Seven lines exist: six requests and one malformed record.','If the file is missing, return to exercise 02 and extract the archive; do not generate replacement logs.'),
S('Compare a naive search with parsed status',L,'Run both searches and explain why they differ.',
r'''grep -n ERROR application.log
grep -n 'status=5[0-9][0-9]' application.log
awk '{for(i=1;i<=NF;i++) if($i ~ /^path=/) print $i}' application.log | sort | uniq -c | sort -nr''','ERROR matches three lines, but status=5xx matches two. /player appears three times.','An ERROR word inside a successful request is a deliberate trap; inspect the status field.'),
S('Extract and transform fields',L,'Explain each pipeline stage before executing it.',
r'''tail -n +2 latency.csv | cut -d, -f2 | sort -n
sed -n '2,6p' application.log
printf 'seen\n' | tee ~/support-lab/evidence/m1-04/pipeline.txt
date -u +%FT%TZ''','Numeric latencies are 5, 25, 30, 80, 1500 and 2100. tee writes to screen and file.','Do not apply cut to general quoted CSV without checking its format.'),
S('Handle unusual filenames safely',L,'Use NUL delimiters to preserve spaces and newlines. Create a new extraction directory for verification.',
r'''find filenames -type f -print0 | xargs -0 -r wc -c
mkdir -p ~/support-lab/archive
find filenames -type f -print0 | tar --null -T - -czf ~/support-lab/archive/selected.tar.gz
verify_dir=$(mktemp -d "$HOME/support-lab/archive/verify-XXXXXX")
tar -xzf ~/support-lab/archive/selected.tar.gz -C "$verify_dir"
diff -r filenames "$verify_dir/filenames"''','diff prints nothing and returns 0 when names and contents match.','If files differ, inspect extraction paths and delimiters instead of editing the original fixtures.'),
S('Observe an expected nonzero pipeline result',L,'Capture the status immediately; restore your prior pipefail setting afterward.',
r'''previous_pipefail=$(set +o | grep pipefail)
set -o pipefail
grep 'NO_SUCH_REQUEST' application.log | wc -l
pipeline_rc=$?
printf 'pipeline_exit=%s\n' "$pipeline_rc"
eval "$previous_pipefail"''','wc prints 0 and pipeline_exit is 1: grep found no matches, rather than a command error.','If you print another command first, $? changes; repeat while capturing it immediately.')],
'Leave original fixtures unchanged. Keep your archive and evidence; you may remove only the newly created verification directory after recording its contents. Restore pipefail as shown.',
['pipeline.txt — tee output','pipeline-notes.md — annotated commands, counts and exit-code explanations'])

guide(1,5,'Instructor has rehearsed setup on a dedicated Ubuntu x86_64 training host with adequate capacity. Installation is one shared operation; learners need read access to the course and service journal.',[
S('Inspect the setup stages',I,'Display the setup script before running it. Identify package installation, checksum verification, app account creation, WAR build and systemd setup.',
r'''cd "$COURSE_ROOT"
less shared/scripts/setup-ubuntu.sh
shared/scripts/preflight.sh''','The host matches the setup assumptions. Learners can explain which operations need sudo.','If host capacity or platform differs, stop and use the instructor preparation guide; do not force the installer.'),
S('Install the shared stack',I,'Run once for the class. Downloads may take several minutes; do not launch another installer while it runs.',
r'''sudo shared/scripts/setup-ubuntu.sh --training-host
setup_rc=$?
printf 'setup_exit=%s\n' "$setup_rc"''','Exit 0 is printed only after application readiness succeeds.','On failure, preserve the output and inspect the reported stage. Do not continue as though deployment succeeded.'),
S('Inspect service identity and logs',L,'Use these read-only checks after the instructor confirms setup success.',
r'''systemctl cat support-tomcat
systemctl status support-tomcat --no-pager
journalctl -u support-tomcat --since '10 minutes ago' --utc --no-pager
ss -lnt''','The unit runs as supportapp and the HTTP listener is bound to loopback port 8080.','If journal access is denied, ask for the training journal group and reconnect; do not use blanket sudo.'),
S('Verify readiness and business data',L,'Save the responses including the request-ID header.',
r'''curl -i http://127.0.0.1:8080/loyalty/live
curl -i http://127.0.0.1:8080/loyalty/health
curl -i 'http://127.0.0.1:8080/loyalty/player?id=1'
curl -i http://127.0.0.1:8080/loyalty/report''','Healthy requests return 200. Player 1 is Synthetic Player One with 100 points; report count is 1000 and total is 10000.00.','If /live works but /health fails, investigate the authenticated database path before restarting Tomcat.'),
S('Open a browser through SSH forwarding',W,'Use a new workstation terminal and your own key. Local port 18080 avoids conflict with a local development server. Keep this session open while browsing.',
r'''read -r -p 'Assigned learner account: ' learner
ssh -N -L 18080:127.0.0.1:8080 -i "$HOME/.ssh/support_lab_ed25519" "$learner@47.131.221.162"''','Open http://127.0.0.1:18080/loyalty/health on your workstation; the tunnel command normally shows no output.','If local port 18080 is occupied, choose a free local port and change the browser URL to match.')],
'Press Ctrl-C in the tunnel terminal to close forwarding. Leave Tomcat/MySQL running for the following exercises; do not uninstall shared packages.',
['baseline.txt — service state, listeners and HTTP results','components.md — application/database diagram and request-ID explanation'])

guide(1,6,'A healthy stack from exercise 05; journal access; a reserved instructor-controlled fault slot.',[
S('Capture the healthy baseline',L,'Record time and a readiness response before the instructor changes anything.',
r'''date -u +%FT%TZ
curl -i http://127.0.0.1:8080/loyalty/health''','HTTP 200 establishes the before-state.','If already unhealthy, ask the instructor to resolve the pre-existing fault first.'),
S('Introduce and observe a startup fault',I,'This guided exercise names the fault; final assessments will not. Tell learners when injection is complete.',
r'''cd "$COURSE_ROOT"
sudo shared/scripts/fault.sh startup''','A deliberate service-start error is expected; the instructor announces that the investigation can begin.','If a saved fault already exists, stop and coordinate ownership before resetting it.'),
S('Locate the failing startup configuration',L,'Do not restart the service yet. Inspect the effective unit and journal.',
r'''systemctl status support-tomcat --no-pager
systemctl cat support-tomcat
journalctl -u support-tomcat -n 60 --utc --no-pager''','status may return nonzero. The training drop-in points to a nonexistent executable.','If you only inspect the main unit file, you may miss the override; use systemctl cat.'),
S('Reset, then introduce a different failure',I,'Reset the startup fault before injecting permissions. Wait for health to return before the next injection.',
r'''sudo shared/scripts/fault.sh reset
curl --fail -i http://127.0.0.1:8080/loyalty/health && sudo shared/scripts/fault.sh permissions''','Readiness is healthy between faults; the permission fault affects configuration readability.','If readiness has not recovered, do not inject another fault.'),
S('Inspect runtime symptoms and file access',L,'Capture the request ID and journal. Ask the instructor to run the privileged path checks shown next.',
r'''curl -i http://127.0.0.1:8080/loyalty/health
journalctl -u support-tomcat --since '5 minutes ago' --utc --no-pager''','HTTP 503 accompanies a file-access error even though Tomcat can be active.','A running process alone does not establish application health.'),
S('Verify permissions, restore and retest',I,'Compare the service identity with file ownership, then restore the saved configuration.',
r'''sudo namei -l /etc/support-lab/app.properties
sudo stat -c '%U %G %a %n' /etc/support-lab/app.properties
sudo shared/scripts/fault.sh reset
curl -i http://127.0.0.1:8080/loyalty/health
curl -i 'http://127.0.0.1:8080/loyalty/player?id=1' ''','Before reset the root-owned config is 600; restored access is root:supportapp mode 640. HTTP checks recover.','Do not print the configuration contents or replace the mode with 777.')],
'Instructor confirms fault reset and healthy business requests. Keep the two fault timelines separate; leave the shared services running.',
['startup-timeline.md — startup evidence and repair verification','permission-timeline.md — runtime error, ownership evidence and recovered request IDs'])

guide(1,7,'Healthy application; sysstat/lsof/network utilities installed; instructor available for privileged observations and a brief fault.',[
S('Measure resources over an interval',L,'Capture a baseline. Explain available versus free memory and load versus CPU percentage.',
r'''uptime
free -h
ps -eo pid,ppid,user,comm,pcpu,pmem --sort=-pcpu | head
top -b -n 1 | head -n 20
pidstat 1 3''','Measurements vary with the host; there is no fixed “correct” CPU value.','If pidstat is missing, ask for sysstat installation. A single sample is insufficient for root-cause claims.'),
S('Observe bounded CPU and file handles',I,'Start one bounded worker while learners repeat pidstat. Then inspect Tomcat handles; do not start multiple workers.',
r'''timeout 15s bash -c 'while :; do :; done' &
worker_pid=$!
sudo lsof -p "$(systemctl show -p MainPID --value support-tomcat)" | head
wait "$worker_pid"
worker_rc=$?
printf 'worker_exit=%s\n' "$worker_rc"''','The synthetic loop ends after 15 seconds; timeout normally returns 124.','If the service PID is 0, inspect service state instead of passing that PID to lsof.'),
S('Test network layers in order',L,'Keep the target local for these probes. Record what each check establishes.',
r'''getent hosts localhost
dig localhost
nslookup localhost
ping -c 2 127.0.0.1
traceroute -m 3 127.0.0.1
ss -lnt
nc -vz -w 2 127.0.0.1 3306
curl --max-time 5 -i http://127.0.0.1:8080/loyalty/health''','DNS, ICMP, listeners, TCP and HTTP provide different evidence; health should be 200 before injection.','A DNS resolver may treat localhost differently from getent; explain the lookup path rather than inventing an outage.'),
S('Compare TCP with authenticated readiness',I,'Inject only after the previous checks finish. Learners repeat nc and curl while the fault is active.',
r'''sudo shared/scripts/fault.sh db-auth
nc -vz -w 2 127.0.0.1 3306
curl -i http://127.0.0.1:8080/loyalty/health
sudo shared/scripts/fault.sh reset''','TCP still connects while application readiness returns 503; reset restores the credentials.','If TCP also fails, investigate that separate observation instead of assuming all symptoms match the intended scenario.'),
S('Analyze platform evidence','Learner · Markdown evidence review','Read [Platform incident cards](../../shared/fixtures/platform-incidents.md). For DNS, TLS, firewall and SELinux, write the next discriminating check. Instructor may show installed ufw/nft rules and authorized AWS security-group views without changing them.',expected='You distinguish Ubuntu live observations from Red Hat/Windows synthetic evidence.',trouble='Do not run platform-specific commands blindly or disable security controls as a shortcut.')],
'Instructor verifies the active fault is reset and /health returns 200. The bounded CPU worker should already have exited; retain observations, not an active load generator.',
['resource-baseline.txt — interval observations','connectivity-table.md — layer, evidence, limitation and next check'])

guide(2,1,'Module 1 stack is healthy. The EC2 training administrator is developer with password password; alternatively, use a per-team account with the diagnostic grants in the setup guide.',[
S('Create a protected client configuration',L,'Open nano after creating the file with restrictive permissions. Enter the four configuration lines below in the editor; use the EC2 training credentials shown below, or your assigned team credentials. Save with Ctrl-O, Enter; exit with Ctrl-X.',
r'''umask 077
touch "$HOME/.support-lab.cnf"
chmod 600 "$HOME/.support-lab.cnf"
nano "$HOME/.support-lab.cnf"''','The file exists with mode 600. Do not paste its contents into submitted evidence.','If the file already has valid credentials, inspect/edit locally rather than overwriting another configuration.'),
S('Enter the client settings','Learner · nano editor for ~/.support-lab.cnf','This is configuration text, not shell commands. These examples use the local EC2 administrator developer with password password. Use your assigned team credentials instead when provided.',
r'''[client]
user=developer
password=password
host=localhost''','The file contains the EC2 training login or your assigned team login.','Account host matching matters; do not switch localhost to 127.0.0.1 unless the instructor created the matching account.','ini'),
S('Run the bounded health check',L,'Return to Bash. Capture status immediately; do not log the configuration file.',
r'''stat -c '%a %n' "$HOME/.support-lab.cnf"
cd "$COURSE_ROOT"
MYSQL_CNF="$HOME/.support-lab.cnf" shared/scripts/db-health.sh
check_rc=$?
printf 'db_health_exit=%s\n' "$check_rc"''','Mode is 600; healthy output includes engine version, SELECT 1 result, connection counters and exit 0.','Exit 2 means configuration prerequisites failed; client access-denied and connection-timeout errors require different checks.'),
S('Enter MySQL and identify the session',L,'Open the interactive client. The next step runs at the mysql> prompt.',
r'''mysql --defaults-extra-file="$HOME/.support-lab.cnf"''','The mysql> prompt appears.','If the prompt never appears, verify credentials privately and the MySQL service; do not run SQL in Bash.'),
S('Capture a read-only baseline',SQL,'Run each statement and record its meaning. Then type exit to return to Bash.',
r'''SELECT UTC_TIMESTAMP(), CURRENT_USER(), VERSION();
SHOW FULL PROCESSLIST;
SHOW GLOBAL STATUS LIKE 'Threads_connected';
SHOW VARIABLES LIKE 'max_connections';
SHOW VARIABLES LIKE 'log_error';
exit''','Identity and version print; connection headroom is assessed against the configured limit.','Visibility depends on privileges. A denied query is unavailable evidence, not proof that no sessions exist.','sql'),
S('Inspect service and full diagnostics',L,'You should now be back at the Bash prompt. Read the instructor-designated MySQL error log only with the granted access.',
r'''cd "$COURSE_ROOT"
systemctl status mysql --no-pager
journalctl -u mysql --since '15 minutes ago' --utc --no-pager
mysql --defaults-extra-file="$HOME/.support-lab.cnf" < shared/sql/mysql/diagnostics.sql''','Read-only checks execute; error-log destinations may be a file, journal or stderr depending on setup.','If journal access is denied, ask the instructor to capture the relevant window; do not broaden privileges yourself.')],
'Exit any open mysql client. Keep the mode-600 client file for later exercises and exclude it from submissions. No server configuration changes were required.',
['db-baseline.txt — time, version, identity, counters and check statuses','db-baseline-notes.md — interpretation and unavailable evidence'])

guide(2,2,'Working team MySQL client configuration from exercise 01; instructor administrative MySQL access; mysqldumpslow installed on the application host.',[
S('Record the original logging configuration','Instructor · administrative MySQL client','Keep this same administrative session open until settings are restored. Save session variables as well as a private written record of the printed values.',
r'''SET @saved_slow = @@GLOBAL.slow_query_log;
SET @saved_threshold = @@GLOBAL.long_query_time;
SET @saved_output = @@GLOBAL.log_output;
SELECT @saved_slow, @saved_threshold, @saved_output;
SHOW GLOBAL VARIABLES LIKE 'slow_query_log_file';''','The original ON/OFF value, threshold, output destination and file path are recorded before changes.','If the admin session closes, restore from the written record; session variables do not survive reconnects.','sql'),
S('Enable a short capture window','Instructor · same administrative MySQL client','These are temporary lab changes. FILE ensures this exercise produces a log that mysqldumpslow can read.',
r'''SET GLOBAL log_output = 'FILE';
SET GLOBAL slow_query_log = ON;
SET GLOBAL long_query_time = 0.2;''','Settings change successfully on the training database.','On access denied, stop; learners must not acquire administrative privileges to continue.','sql'),
S('Open a fresh learner connection',L,'Use a fresh client so it inherits the new global threshold.',
r'''mysql --defaults-extra-file="$HOME/.support-lab.cnf"''','mysql> appears in a new session.','An existing session may retain its old long_query_time; do not assume a global change modifies it.'),
S('Create bounded slow-query evidence',SQL,'Run one deliberate delay and one report query. Exit afterward.',
r'''SET SESSION long_query_time = 0.2;
SELECT SLEEP(0.3);
SELECT COUNT(*), SUM(amount) FROM support_lab.transactions WHERE player_id=42;
exit''','The intentional SLEEP query exceeds the threshold. The report may be too fast to enter the slow log on this host.','Do not enlarge the workload to force severe slowness; use the supplied synthetic log for deterministic ranking.','sql'),
S('Inspect the capture and rank the fixture',L,'Instructor shows the new record from the previously identified live log path. In your shell, summarize the supplied synthetic log two ways.',
r'''cd "$COURSE_ROOT"
mysqldumpslow -s t -t 5 shared/fixtures/mysql-slow.log
mysqldumpslow -s c -t 5 shared/fixtures/mysql-slow.log''','The similar report queries group into three executions, totaling approximately 3.6 seconds; the single delay takes 3 seconds.','If the live record is absent, instructor checks log_output, threshold and minimum examined-row settings; do not fabricate a capture.'),
S('Restore the exact original values','Instructor · original administrative MySQL client','Restore all three settings, then verify the values. Learners record that restoration occurred.',
r'''SET GLOBAL slow_query_log = @saved_slow;
SET GLOBAL long_query_time = @saved_threshold;
SET GLOBAL log_output = @saved_output;
SELECT @@GLOBAL.slow_query_log, @@GLOBAL.long_query_time, @@GLOBAL.log_output;''','Values match the first step.','If a saved variable is NULL because this is a different connection, stop and use the recorded original values explicitly.','sql')],
'Complete the restoration step even if capture failed. Close learner capture sessions; retain logs according to the instructor retention policy rather than deleting database log files.',
['slow-query-ranking.md — frequency, total/average time, rows examined and next check','logging-change-record.md — original values, capture window and restoration confirmation'])

guide(2,3,'Seeded support_lab with 100,000 transactions; no idx_transactions_player index from a previous team; instructor controls CREATE/DROP INDEX.',[
S('Connect and record the baseline',L,'Open the client; run the following SQL step at mysql>.',
r'''mysql --defaults-extra-file="$HOME/.support-lab.cnf"''','The client connects with the assigned team login.','Resolve authentication before investigating query performance.'),
S('Inspect data and the estimated plan',SQL,'Record both the plan and business result before changing an index.',
r'''USE support_lab;
SELECT COUNT(*) FROM transactions;
SHOW INDEX FROM transactions;
EXPLAIN SELECT COUNT(*),SUM(amount) FROM transactions WHERE player_id=42;
SELECT COUNT(*),SUM(amount) FROM transactions WHERE player_id=42;''','Data count is 100000; the player-42 result is 1000 and 10000.00. Initial plan details depend on engine statistics.','If idx_transactions_player already exists, ask the instructor to restore the baseline before comparing.','sql'),
S('Apply the approved training index','Instructor · administrative MySQL client','Create only this named lab index, then announce completion to learners.',
r'''CREATE INDEX idx_transactions_player ON support_lab.transactions(player_id);''','The named index is created.','If an index already exists, inspect it first; do not drop unrelated indexes.','sql'),
S('Compare after-state without assuming faster timing',SQL,'Repeat the same query and inspect access method, key and estimated rows.',
r'''EXPLAIN SELECT COUNT(*),SUM(amount) FROM transactions WHERE player_id=42;
SELECT COUNT(*),SUM(amount) FROM transactions WHERE player_id=42;
exit''','Business results remain the same; the plan can use the new index.','An unchanged plan requires investigation of selectivity/statistics; command success alone is not proof of benefit.','sql'),
S('Restore the exercise baseline','Instructor · administrative MySQL client','Remove only the index created in this exercise.',
r'''DROP INDEX idx_transactions_player ON support_lab.transactions;
SHOW INDEX FROM support_lab.transactions;''','The training index is absent and the original primary key remains.','If another team is using the index experiment, coordinate before cleanup.','sql')],
'Instructor drops the named training index after evidence is captured. Learners exit the client and retain before/after plans. Do not delete the seeded tables.',
['plan-comparison.md — before/after plan fields, identical results and index tradeoffs'])

guide(2,4,'Team login has UPDATE on support_lab and lock-diagnostic visibility. Open THREE SSH terminals to the same application host and label them A, B and Observer. Reserve 10 minutes with the instructor to avoid other team writes.',[
S('Open all three MySQL sessions','Learner · Bash terminals A, B and Observer','Run this connection command in each terminal. All subsequent SQL steps name the terminal where they belong.',
r'''mysql --defaults-extra-file="$HOME/.support-lab.cnf" support_lab''','Each terminal has its own mysql> prompt and independent session.','Do not run the whole exercise in a single connection; it cannot demonstrate contention.'),
S('Acquire the first lock','Session A · MySQL','Run these statements and leave the transaction open. The instructor keeps this demonstration under one minute.',
r'''SELECT CONNECTION_ID();
START TRANSACTION;
UPDATE players SET points=points+1 WHERE id=1;''','UPDATE completes; A holds a lock on player 1 until commit/rollback.','If UPDATE itself waits, another session owns a conflicting lock; ask the instructor to restore a clean baseline.','sql'),
S('Create a bounded waiter','Session B · MySQL','The UPDATE below should wait. Do not type the next task in B while it waits; switch to Observer.',
r'''SET SESSION innodb_lock_wait_timeout=30;
START TRANSACTION;
UPDATE players SET points=points+1 WHERE id=1;''','B pauses waiting for A, or reports lock-wait timeout after 30 seconds.','If B finishes immediately, verify A is still in its transaction and both use the same database/row.','sql'),
S('Capture the wait relationship','Observer · MySQL','Run while B is waiting; capture connection IDs and the requested lock.',
r'''SHOW FULL PROCESSLIST;
SELECT * FROM performance_schema.data_lock_waits;''','A blocking relationship is visible while the wait is active.','If the timeout elapsed before capture, first roll back A and B, then repeat the short sequence.','sql'),
S('Release both transactions','Session A, then Session B · MySQL','Run ROLLBACK in A first. B may finish its UPDATE after the lock releases; then run ROLLBACK in B too.',
r'''ROLLBACK;''','Both sessions return to a clean prompt and neither change is committed.','A timeout does not reliably mean the whole transaction ended; explicitly roll back both sessions.','sql'),
S('Build the deadlock in a precise order','Session A and Session B · MySQL','First run the A block. Then run the B block in the next step; do not paste both into one terminal.',
r'''START TRANSACTION;
UPDATE players SET points=points+1 WHERE id=1;''','A owns player 1.','If blocked already, roll back and restore the baseline before continuing.','sql'),
S('Acquire the second lock','Session B · MySQL','B locks a different row.',
r'''START TRANSACTION;
UPDATE players SET points=points+1 WHERE id=2;''','B owns player 2 and A owns player 1.','Confirm no other team is writing these rows.','sql'),
S('Make A request B’s row','Session A · MySQL','This statement should block. Immediately switch to B for the next step.',
r'''UPDATE players SET points=points+1 WHERE id=2;''','A waits for B.','If it times out before the next step, roll back both sessions and repeat.','sql'),
S('Complete the cycle','Session B · MySQL','Request A’s row. Either A or B can be selected as the victim; inspect both terminals.',
r'''UPDATE players SET points=points+1 WHERE id=1;''','One session reports deadlock error 1213; the other can proceed. Victim selection is not fixed.','If no deadlock occurs, check row order and whether either transaction was already rolled back.','sql'),
S('Capture the deadlock and recover','Observer, then A and B · MySQL','Observer runs the status statement. After saving evidence, run ROLLBACK separately in A and B, then the final SELECT in Observer.',
r'''SHOW ENGINE INNODB STATUS\G''','The latest detected deadlock contains the cycle and victim.','Capture promptly: a later deadlock can replace this diagnostic record.','sql'),
S('Verify restored data','Observer · MySQL','After BOTH writers have rolled back, compare the seeded values.',
r'''SELECT id,points FROM players ORDER BY id;''','Players 1, 2 and 42 have 100, 200 and 300 points if the starting data was unchanged.','A different result may reflect committed work from another team; do not overwrite it without instructor review.','sql')],
'Run ROLLBACK in A and B even after errors, then type exit in all three clients. Closing the client also releases session locks, but demonstrate explicit rollback first. Do not kill arbitrary sessions.',
['locking-timeline.md — session IDs, sequence, lock wait and deadlock evidence','lock-diagram.md — held/requested rows, victim, survivor and recovery checks'])

guide(2,5,'The synthetic replication fixture is readable. No live replica is required or installed by this course.',[
S('Read the fixture and record provenance',L,'Identify capture time, primary write time and replica-visible time before interpreting status.',
r'''cd "$COURSE_ROOT"
cat shared/fixtures/replication.json''','The file explicitly labels itself synthetic; receiver and applier states differ.','Do not run replica repair commands against the standalone class database.'),
S('Build a freshness table','Learner · evidence notes','Create columns for source, UTC time, receiver state, applier state, error and freshness confidence. Copy the supplied values and mark NULL lag as unknown.',expected='You distinguish reception from application and can explain why a report may be stale.',trouble='A NULL delay value is not zero. Missing data must remain unknown.'),
S('Choose the next investigation','Team discussion','Use the supplied relay-log filename and error as investigation leads. Describe what a DBA should inspect, what routing change could reduce impact, and what capacity/consistency risk that change creates.',expected='Your escalation asks for a specific consistency/applier investigation and a business freshness decision.',trouble='Do not recommend skipping a transaction merely because it is blocking replication.')],
'No live state was changed. Keep the original fixture unchanged and label all submitted findings as synthetic evidence analysis.',
['replication-escalation.md — freshness table, error interpretation, routing tradeoff and next checks'])

guide(2,6,'Separate SQL Server lab is ready; learner login/grants are provisioned. The application host or designated client workstation has ODBC sqlcmd available. Instructor supplies SQL_HOST and the approved certificate policy.',[
S('Set connection details in the client shell','Learner · designated SQL client host · Bash','In this shell, define SQL_HOST and SQL_LOGIN. Read the password without echoing it. Use the instructor-provided hostname, not the example text.',
r'''read -r -p 'SQL Server hostname or private IP: ' SQL_HOST
read -r -p 'Assigned SQL login: ' SQL_LOGIN
read -r -s -p 'SQL password: ' SQLCMDPASSWORD
printf '\n'
export SQL_HOST SQL_LOGIN SQLCMDPASSWORD
SQL_TLS_ARGS=()
command -v sqlcmd''','sqlcmd is found; the password is not echoed.','If not found, use the instructor-installed /opt/mssql-tools18/bin/sqlcmd or add that directory to PATH. Do not put passwords in -P arguments.'),
S('Confirm identity and database access','Learner · same SQL client Bash shell','Use a trusted server certificate. If the dedicated disposable lab uses a self-signed certificate, the instructor may explicitly direct setting SQL_TLS_ARGS=(-C) in this shell; do not bypass validation without that context.',
r'''sqlcmd "${SQL_TLS_ARGS[@]}" -S "tcp:$SQL_HOST,1433" -U "$SQL_LOGIN" -d SupportLab -b -Q 'SELECT SYSUTCDATETIME(), SUSER_SNAME(), @@VERSION;' ''','The assigned login, timestamp and SQL Server 2022 version are returned.','A TLS error differs from login failure; check the instructor certificate instructions before continuing.'),
S('Capture baseline diagnostics','Learner · same SQL client Bash shell','The course files must be present on this client host. Write output to your evidence directory, then read it.',
r'''cd "$COURSE_ROOT"
sqlcmd "${SQL_TLS_ARGS[@]}" -S "tcp:$SQL_HOST,1433" -U "$SQL_LOGIN" -d SupportLab -b -i shared/sql/sqlserver/diagnostics.sql -o "$HOME/support-lab/evidence/m2-06/sql-baseline.txt"
less "$HOME/support-lab/evidence/m2-06/sql-baseline.txt"''','Requests, sessions, waits, cached plans, Query Store and job-history results are captured. Some result sets may be empty.','Inspect any permission errors; do not treat a failed query as an empty healthy result. SQL text/plans require review before sharing.'),
S('Observe a bounded workload','Learner · second SQL client Bash shell','Set the connection variables in this second shell as in step 1. Run the workload while the first shell repeats diagnostics. Do not use production targets.',
r'''cd "$COURSE_ROOT"
sqlcmd "${SQL_TLS_ARGS[@]}" -S "tcp:$SQL_HOST,1433" -U "$SQL_LOGIN" -d SupportLab -b -i shared/sql/sqlserver/workload.sql''','The workload completes after 30 report queries. A fast host may finish before the observer captures an active request.','Use the synthetic interval evidence if live timing is inconclusive; do not increase workload without instructor direction.'),
S('Compute interval wait deltas',L,'Read the two synthetic captures and subtract earlier counters from later counters for each wait type.',
r'''cd "$COURSE_ROOT"
cat shared/fixtures/sqlserver-waits.csv''','LCK_M_X increases 12000 ms, SOS_SCHEDULER_YIELD 1000 ms and PAGEIOLATCH_SH 200 ms.','These cumulative wait deltas can exceed wall-clock time with concurrent sessions; they are not simple CPU percentages.')],
'Unset SQLCMDPASSWORD in each client shell after use. Workload.sql does not create the commented optional index. Leave SQL Server running; retain reviewed evidence.',
['sql-baseline.txt — diagnostics output','wait-deltas.md — intervals, units, arithmetic and interpretation'])

guide(2,7,'Complete SQL Server connection setup. Open three independent query sessions A, B and Observer against SupportLab using sqlcmd interactive mode or the instructor-approved query editor. Instructor controls index changes, Query Store flushing and job starts.',[
S('Prepare three independent query windows',TSQL,'In EACH window, select the database and record its session ID. For interactive sqlcmd, GO on its own line sends each batch; a query editor uses Execute.',
r'''USE SupportLab;
SELECT @@SPID AS session_id;
GO''','A, B and Observer have different session IDs.','Reusing one connection cannot create a blocking relationship.','sql'),
S('Acquire a lock in A','Session A · T-SQL','Leave this transaction open for less than one minute while the next two steps run.',
r'''BEGIN TRAN;
UPDATE dbo.Players SET points=points+1 WHERE id=1;
GO''','A’s update completes and retains its transaction lock.','If A is already blocked, ask the instructor to identify the earlier owner first.','sql'),
S('Create a bounded wait in B','Session B · T-SQL','B waits for at most 15 seconds. Switch promptly to Observer.',
r'''SET LOCK_TIMEOUT 15000;
BEGIN TRAN;
UPDATE dbo.Players SET points=points+1 WHERE id=1;
GO''','B waits, then may return lock timeout error 1222.','Do not mistake timeout for proof that A released its lock.','sql'),
S('Observe and release the blocker','Observer · T-SQL, then Session A','Run the query in Observer while B waits. After recording the chain, run ROLLBACK; followed by GO in A first. B may then finish its UPDATE; run ROLLBACK; and GO in B too, whether its UPDATE succeeded or timed out.',
r'''SELECT session_id,status,wait_type,blocking_session_id
FROM sys.dm_exec_requests WHERE blocking_session_id > 0;
GO''','The waiting request names A as blocker. A may be sleeping while retaining an open transaction.','If no row appears, repeat only after cleaning up A and confirming B is actively waiting.','sql'),
S('Compare a controlled index change','Instructor · T-SQL; learners run workload/diagnostics','Learners first capture workload.sql and diagnostics.sql results. Instructor then runs the index statement. Learners repeat the same workload and inspect Query Store.',
r'''USE SupportLab;
CREATE INDEX IX_Transactions_Player ON dbo.Transactions(player_id) INCLUDE(amount);
EXEC sys.sp_query_store_flush_db;
GO''','The new index can change reads/plan selection. Query Store runtime records may take time to populate.','If the index exists, inspect/reset the training baseline first. Do not infer regression solely from a changed plan ID.','sql'),
S('Start and inspect the intentional job failure','Instructor · T-SQL for job start; learner · T-SQL for history','Instructor executes the first batch. After a few seconds, learners execute the history batch using their own login.',
r'''EXEC msdb.dbo.sp_start_job @job_name=N'SupportLab-IntentionalFailure';
GO
EXEC msdb.dbo.sp_help_jobhistory @job_name=N'SupportLab-IntentionalFailure', @mode=N'FULL';
GO''','The live job fails intentionally with a synthetic training error. Learner history access works through SQLAgentReaderRole.','If Agent is still starting, wait; if history is denied, ask the instructor to verify the assigned role.','sql'),
S('Interpret deterministic regression evidence',L,'Read the supplied captures as a separate fictional incident. Compare duration, CPU and reads with their units; inspect the statistics query in diagnostics.sql as the next live check.',
r'''cd "$COURSE_ROOT"
cat shared/fixtures/query-store.csv
cat shared/fixtures/job-history.csv''','Query 17 has a more expensive later plan; the synthetic job has a permission error, unlike the live intentional-THROW job.','Do not combine unrelated synthetic and live faults into one claimed root cause.')],
'In A and any explicit transaction-owning session run ROLLBACK if @@TRANCOUNT > 0. Instructor drops IX_Transactions_Player from SupportLab.dbo.Transactions if this exercise created it. Both writers use explicit transactions, so rollback restores their uncommitted changes; verify player values before handing the lab to another team. Close SQL sessions and unset SQLCMDPASSWORD.',
['sql-blocking.md — sessions, head blocker and release evidence','query-store-job-report.md — live versus synthetic findings, units and next checks'])

guide(2,8,'Healthy application and readable correlation.csv; an instructor-controlled delay-fault slot. The live app has no connection pool: pooled-app evidence is synthetic.',[
S('Read and reconcile the synthetic request timing',L,'For each request, add pool wait, SQL time and other time. Compare the sum with total HTTP time.',
r'''cd "$COURSE_ROOT"
cat shared/fixtures/correlation.csv''','For r900, 4000 + 40 + 960 = 5000 ms. Retries and pooled connection wait are supplied evidence, not live app features.','Do not infer an exact request-to-query join from coincident timestamps alone.'),
S('Measure the healthy live baseline',L,'Generate only five sequential requests and record their HTTP codes and seconds.',
r'''shared/scripts/traffic.sh http://127.0.0.1:8080/loyalty 5''','A healthy baseline has successful responses; times depend on the host.','If already failing, resolve that condition before comparing with an injected delay.'),
S('Introduce application-side delay',I,'Tell learners when the bounded fault is active.',
r'''cd "$COURSE_ROOT"
sudo shared/scripts/fault.sh latency''','The app now adds 1500 ms during the request path.','Do not stack this fault with another saved fault.'),
S('Compare latency with application evidence',L,'Repeat the same five requests and inspect the same time window.',
r'''shared/scripts/traffic.sh http://127.0.0.1:8080/loyalty 5
journalctl -u support-tomcat --since '5 minutes ago' --utc --no-pager''','Responses are roughly 1.5 seconds slower; logs provide request IDs and latency_ms.','This is not proof of slow SQL. Separate measured facts from where you suspect time was spent.'),
S('Reset and confirm the comparison',I,'Reset; learners repeat the same traffic command once more.',
r'''sudo shared/scripts/fault.sh reset
shared/scripts/traffic.sh http://127.0.0.1:8080/loyalty 5''','The added delay disappears; compare equivalent routes and sample counts.','If delay persists, inspect remaining load/configuration before declaring recovery.')],
'Instructor confirms reset. Keep the synthetic pooled-app timeline and live delay experiment in separate sections of the report.',
['correlation-timeline.md — arithmetic, IDs, live before/during/after timings and next measurement'])

guide(3,1,'A working learner workspace and healthy application. Bash, curl, systemctl and an editor are installed. Use your own bin directory, not the shared reference scripts.',[
S('Create a script you can edit',L,'Copy the starter into a learner-owned directory. Open it in nano; save with Ctrl-O, Enter and exit with Ctrl-X.',
r'''mkdir -p ~/support-lab/bin
cp "$COURSE_ROOT/shared/templates/triage-starter.sh" ~/support-lab/bin/my-health.sh
nano ~/support-lab/bin/my-health.sh''','You have your own editable script; the shared original is unchanged.','If my-health.sh already exists, copy it to a backup filename before replacing it.'),
S('Implement the check interface','Learner · editor for my-health.sh','Use the example as a scaffold. Add available-memory and disk reporting yourself. The first argument is the service, the second the URL. Review every line before saving.',
r'''#!/usr/bin/env bash
set -u
service=${1:-support-tomcat}
url=${2:-http://127.0.0.1:8080/loyalty/health}
failed=0
log() { printf '%s %s\n' "$(date -u +%FT%TZ)" "$1"; }
for tool in systemctl curl; do
    command -v "$tool" >/dev/null || exit 2
done
if systemctl is-active --quiet "$service"; then
    log 'service=OK'
else
    log 'service=FAIL'; failed=1
fi
if curl --fail --silent --max-time 5 "$url" >/dev/null; then
    log 'endpoint=OK'
else
    log 'endpoint=FAIL'; failed=1
fi
exit "$failed"''','The script uses arguments, defaults, a function, a loop, conditions and a documented status.','Keep quotes around expansions; do not paste the surrounding Markdown fences into the file.'),
S('Check syntax before execution',L,'A syntax check does not run the script. Only execute it after bash -n succeeds.',
r'''bash -n ~/support-lab/bin/my-health.sh
chmod 750 ~/support-lab/bin/my-health.sh
~/support-lab/bin/my-health.sh
script_rc=$?
printf 'script_exit=%s\n' "$script_rc"''','Healthy checks return 0. Syntax success normally produces no output.','If a line number is reported, fix that line and nearby quotes/keywords before continuing.'),
S('Test an expected failure without changing services',L,'Use an unreachable loopback port. This is a failed probe, not a request to stop the shared application.',
r'''~/support-lab/bin/my-health.sh support-tomcat http://127.0.0.1:1
script_rc=$?
printf 'script_exit=%s\n' "$script_rc"''','The endpoint check fails promptly and the script returns 1.','If it hangs, inspect whether your curl call still has a timeout.'),
S('Compare with the reference implementation',L,'Read the reference, then test its input validation. Document what your script does and does not yet handle.',
r'''less "$COURSE_ROOT/shared/scripts/health-check.sh"
DISK_LIMIT=invalid "$COURSE_ROOT/shared/scripts/health-check.sh"
reference_rc=$?
printf 'reference_exit=%s\n' "$reference_rc"''','The reference returns 2 for invalid configuration. Your report distinguishes this from an unhealthy service.', 'Do not claim your scaffold has every reference behavior until you implement and test it.')],
'Leave the shared service running. Keep your executable script and test transcript; remove no system files. Return to COURSE_ROOT before the next exercise.',
['my-health.sh — submit a copy from your learner bin directory','script-tests.md — healthy, unreachable and invalid-input results plus remaining limitations'])

guide(3,2,'Journal access and the reference collector are available. Use only synthetic secrets in masking tests; never copy real credentials into sample input.',[
S('Collect a bounded evidence bundle',L,'Capture the status immediately, then copy the printed bundle path into your notes.',
r'''cd "$COURSE_ROOT"
shared/scripts/collect-evidence.sh "$HOME/support-lab/evidence/m3-02/bundles" '20 minutes ago'
collector_rc=$?
printf 'collector_exit=%s\n' "$collector_rc"''','Exit 0 means all capture commands succeeded; 1 means a useful partial bundle; 2 means creation/packaging failed.','Read the per-command manifest before treating exit 1 as an unusable bundle.'),
S('Inspect the exact bundle',L,'At the prompt, paste the archive path printed by the collector, without the bundle= prefix. Do not choose an unrelated archive.',
r'''read -r -p 'Printed archive path: ' bundle
stat -c '%a %n' "$bundle"
tar -tzf "$bundle"
review_dir=$(mktemp -d "$HOME/support-lab/evidence/m3-02/review-XXXXXX")
tar -xzf "$bundle" -C "$review_dir"
find "$review_dir" -name manifest.tsv -exec cat {} \;''','The archive is private to your account; the manifest lists each capture’s exit code.','If extraction fails, verify the exact printed path and archive listing before retrying.'),
S('Interpret missing permissions','Learner and instructor · compare existing captures','Identify a nonzero capture status or ask the instructor to provide a capture from an account without journal access. Compare denied output with a genuinely empty window. Do not remove groups from the shared account just to create a test.',expected='Your evidence index labels inaccessible data and empty data differently.',trouble='If every capture succeeded, use the provided local test harness as the partial-failure demonstration; do not invent a failed capture.'),
S('Inspect and exercise masking with synthetic input',L,'This mirrors the collector’s simple filter. Explain why it is only a teaching example and still needs manual review.',
r'''printf 'password=synthetic-only token=dummy-token\n' | sed -E 's/((password|token|secret|authorization)[=:][[:space:]]*)[^[:space:]]+/\1[REDACTED]/Ig' ''','Both synthetic values become [REDACTED].','Values with spaces, alternate formats or secrets inside SQL may evade this pattern. Never assume the regex guarantees safe sharing.'),
S('Write an evidence index','Learner · editor','List every useful file, its UTC window, successful/partial status and why it matters. Review extracted content before submission and leave real credentials out.',expected='A reviewer can locate evidence and understand gaps without rerunning the incident.',trouble='If sensitive content appears, redact a submission copy and retain the original only under the instructor’s evidence policy.')],
'Keep the reviewed bundle and index. The extraction directory contains copies and may be removed after review; do not delete the only incident archive or broadly clean other evidence.',
['evidence-index.md — bundle path, UTC window, capture statuses and redaction review','reviewed-bundle.tar.gz — a reviewed copy of the generated archive'])

guide(3,3,'Synthetic application.log is readable. Understand that this parser accepts a bounded input window; it does not choose freshness automatically.',[
S('Run the known fixture',L,'The command intentionally produces an alert. Capture its status without stopping the exercise.',
r'''cd "$COURSE_ROOT"
shared/scripts/monitor-log.sh shared/fixtures/application.log 10 1000
monitor_rc=$?
printf 'monitor_exit=%s\n' "$monitor_rc"''','CSV: 6 requests, 2 errors, 33.33 percent, 2 slow, 1 malformed, ALERT; exit 1.','If your result differs, confirm that the original fixture has not been edited.'),
S('Create isolated boundary inputs',L,'These files belong to this exercise’s evidence folder, not the original fixture directory.',
r'''printf 'status=200 latency_ms=10\n' > ~/support-lab/evidence/m3-03/healthy.log
: > ~/support-lab/evidence/m3-03/empty.log
printf 'malformed record\n' > ~/support-lab/evidence/m3-03/malformed.log''','Three small test files exist; the empty file is intentionally zero bytes.','Do not redirect into a real application log.'),
S('Compare healthy, empty and malformed cases',L,'Run each check and record its immediate exit status.',
r'''for case_name in healthy empty malformed; do
    "$COURSE_ROOT/shared/scripts/monitor-log.sh" "$HOME/support-lab/evidence/m3-03/$case_name.log" 10 1000
    monitor_rc=$?
    printf '%s exit=%s\n' "$case_name" "$monitor_rc"
done''','Healthy returns OK/0; empty and malformed-only inputs return NO_DATA/2.','NO_DATA is not proof that the service is healthy; inspect the data source and time window.'),
S('Parse a current journal window',L,'Capture recent application messages with their original message text. Record the capture time separately.',
r'''date -u +%FT%TZ > ~/support-lab/evidence/m3-03/captured-at.txt
journalctl -u support-tomcat --since '5 minutes ago' --utc -o cat --no-pager > ~/support-lab/evidence/m3-03/window.log
"$COURSE_ROOT/shared/scripts/monitor-log.sh" ~/support-lab/evidence/m3-03/window.log 10 1000''','Live results vary with traffic; non-request startup lines count as malformed.','If there are no requests, ask the instructor to permit a few bounded healthy probes; do not report NO_DATA as zero errors.'),
S('Document the monitoring policy','Learner · notes','Specify the window, valid-record rule, 5xx definition, denominator, inclusive thresholds and behavior for stale/missing data. Add a freshness check as an extension.',expected='Someone else can explain why each fixture alerts or does not alert.',trouble='A parser’s success does not prove that its input is recent.')],
'Keep the small test files and CSV results as evidence. No service configuration changed; do not delete the live journal or source fixture.',
['monitor-policy.md — definitions, thresholds, no-data and freshness handling','monitor-results.txt — fixture and boundary-case outputs'])

guide(3,4,'mysqldumpslow is installed; Module 3 exercise 03 is complete. Synthetic slow and application logs are available.',[
S('Create your report directory and source record',L,'Use a unique output directory. The variable summary_dir remains in this terminal for the next steps.',
r'''mkdir -p ~/support-lab/summary
summary_dir=$(mktemp -d "$HOME/support-lab/summary/run-XXXXXX")
date -u +%FT%TZ > "$summary_dir/captured-at.txt"
printf '%s\n' "$summary_dir"
cd "$COURSE_ROOT"''','You have a fresh report directory and UTC capture record.','If the terminal changes, re-enter the exact printed path; shell variables are not shared automatically.'),
S('Produce two slow-query rankings',L,'Compare frequency ordering with time ordering.',
r'''mysqldumpslow -s t -t 5 shared/fixtures/mysql-slow.log > "$summary_dir/slow-time.txt"
mysqldumpslow -s c -t 5 shared/fixtures/mysql-slow.log > "$summary_dir/slow-count.txt"
cat "$summary_dir/slow-time.txt"
cat "$summary_dir/slow-count.txt"''','Similar queries group together; the report query runs three times.','Do not grep SELECT lines and discard multiline record context.'),
S('Save an alert result without losing it',L,'The parser exits 1 deliberately. Retain its CSV and record status rather than discarding it.',
r'''shared/scripts/monitor-log.sh shared/fixtures/application.log > "$summary_dir/application.csv"
monitor_rc=$?
printf 'application_exit=%s\n' "$monitor_rc" > "$summary_dir/status.txt"
cat "$summary_dir/application.csv"''','The CSV exists and reports ALERT even though exit status is 1.','A wrapper using unconditional set -e may stop here; handle expected alert statuses explicitly.'),
S('Run the reference wrapper and inspect its manifest',L,'Compare the wrapper’s timestamped directory with your manually assembled report.',
r'''shared/scripts/monitor-pipeline.sh shared/fixtures/application.log "$HOME/support-lab/monitoring" shared/fixtures/mysql-slow.log
pipeline_rc=$?
printf 'pipeline_exit=%s\n' "$pipeline_rc"''','With mysqldumpslow available, the wrapper retains the alert output and exits 1. Exit 2 indicates incomplete/invalid evidence.','Read the manifest when the slow summary is unavailable; do not label an incomplete report healthy.')],
'Keep your report directory and manifest. Original logs remain unchanged. No active monitoring daemon was started by these commands.',
['summary-index.md — output directory, source windows, status and correlation limitations','report-directory — your CSV, rankings and manifest'])

guide(3,5,'A working reference health checker; crontab and flock available. Learners may edit only their own crontab. The retention demonstration uses an isolated HOME containing dummy files.',[
S('Install learner-owned scripts and test the cron environment',L,'Keep absolute paths. The subshell below changes directory only for the test.',
r'''mkdir -p ~/support-lab/{bin,logs,evidence}
cp "$COURSE_ROOT/shared/scripts/health-check.sh" ~/support-lab/bin/
cp "$COURSE_ROOT/shared/scripts/retention.sh" ~/support-lab/bin/
(cd /tmp && env -i HOME="$HOME" PATH=/usr/bin:/bin "$HOME/support-lab/bin/health-check.sh")
check_rc=$?
printf 'minimal_environment_exit=%s\n' "$check_rc"''','The script runs from /tmp without relying on your interactive PATH or working directory.','A failed health check may legitimately return 1; a missing command/path is a different problem.'),
S('Back up and edit your own crontab',L,'Save current entries before editing. No crontab for this user is an expected message for a new account. Preserve all unrelated entries.',
r'''crontab -l > ~/support-lab/evidence/m3-05/crontab-before.txt
cat "$COURSE_ROOT/shared/templates/crontab.example"
printf 'Your HOME is %s\n' "$HOME"
crontab -e''','An editor opens for your account. Copy the template entries and replace every /home/learner01 with the actual HOME printed above.','Choose an available editor when prompted. Never use sudo crontab -e for this learner exercise.'),
S('Verify the saved entry and observe execution',L,'Save and exit the editor. Check paths and the lock file location. Allow up to five minutes while continuing the retention exercise.',
r'''crontab -l
"$HOME/support-lab/bin/health-check.sh" >> "$HOME/support-lab/logs/health.log" 2>&1
tail -n 10 "$HOME/support-lab/logs/health.log"''','The installed entry uses absolute paths and flock. Later scheduled entries have new timestamps.','The immediate manual run only tests the command; it does not prove cron fired. Verify a later timestamp after the scheduled boundary.'),
S('Create disposable retention input',L,'Use a temporary HOME so applying retention cannot touch your real evidence. Keep demo_home in this terminal.',
r'''demo_home=$(mktemp -d)
mkdir -p "$demo_home/support-lab/evidence"
printf 'dummy\n' > "$demo_home/support-lab/evidence/incident-old.tar.gz"
printf 'keep\n' > "$demo_home/support-lab/evidence/unrelated.txt"
touch -d '10 days ago' "$demo_home/support-lab/evidence/incident-old.tar.gz"
printf 'Demo HOME: %s\n' "$demo_home"''','Only dummy files exist in this isolated directory; the .tar.gz name is a retention test filename, not a real archive.','Do not replace demo_home with your actual HOME.'),
S('Preview, apply and verify narrowly scoped cleanup',L,'First review dry-run output. Apply only after confirming it names the dummy archive under the printed temporary directory.',
r'''HOME="$demo_home" "$COURSE_ROOT/shared/scripts/retention.sh" --dry-run
HOME="$demo_home" "$COURSE_ROOT/shared/scripts/retention.sh" --apply
find "$demo_home/support-lab/evidence" -maxdepth 1 -type f -print''','The old incident file is removed and unrelated.txt remains.','If another path appears, stop before --apply and inspect your variables.'),
S('Remove only the exercise’s scheduled entries',L,'Open your crontab and delete the health/retention lines added for this exercise, preserving pre-existing entries. Do not restore a whole old crontab over newer unrelated work.',
r'''crontab -e
crontab -l''','The exercise entries are gone; previous entries remain.','If unsure which lines you added, compare with crontab-before.txt before saving.')],
'Remove the exercise’s cron entries as shown unless the instructor explicitly asks to retain them. Delete the two dummy files/directory under the recorded demo_home after verification; keep real evidence and the crontab backup. Archive retention is not a database backup or restore strategy.',
['cron-verification.md — reviewed entry, manual versus scheduled timestamps and removal confirmation','retention-results.txt — dry-run, deletion and unrelated-file survival'])

guide(3,6,'A learner health script from exercise 01; healthy seeded player 1; instructor has a reserved fault slot.',[
S('Record the business response',L,'Inspect the exact successful response before writing an assertion.',
r'''curl --fail --silent --max-time 5 'http://127.0.0.1:8080/loyalty/player?id=1'
curl --fail --silent --max-time 5 http://127.0.0.1:8080/loyalty/payment''','Player response is 1,Synthetic Player One,100 and payment simulator reports ready.','If earlier transaction labs changed player points, ask the instructor to confirm the intended baseline before hard-coding an assertion.'),
S('Create your deployment gate','Learner · editor','Create ~/support-lab/bin/deployment-check.sh. Use the example to add a business assertion; also include a payment-route check yourself.',
r'''#!/usr/bin/env bash
set -u
if ! body=$(curl --fail --silent --show-error --max-time 5 'http://127.0.0.1:8080/loyalty/player?id=1'); then
    printf 'player=UNREACHABLE\n'; exit 1
fi
if [[ $body != '1,Synthetic Player One,100' ]]; then
    printf 'player=UNEXPECTED_RESULT\n'; exit 1
fi
printf 'player=OK\n'
# Add a bounded payment check here; return nonzero if it fails.
exit 0''','Your own file checks content, not just process existence.','The scaffold alone does not yet test payment. Complete that part before calling it a payment deployment gate.'),
S('Check and run the gate',L,'Make the file executable only after syntax succeeds.',
r'''bash -n ~/support-lab/bin/deployment-check.sh
chmod 750 ~/support-lab/bin/deployment-check.sh
~/support-lab/bin/deployment-check.sh
gate_rc=$?
printf 'gate_exit=%s\n' "$gate_rc"''','Healthy business checks pass with exit 0.','If output differs, inspect the response rather than weakening the assertion immediately.'),
S('Test an affected business function','Instructor injects; learner runs gate','Ask the instructor to select a known guided fault affecting authentication or the payment simulator. Run both the generic reference health check and your gate; record which detects the affected function. Do not put fault injection in your gate.',expected='Your completed gate fails on the affected business route even if generic readiness remains green.',trouble='A gate that checks only /health may miss payment failure. Add route-specific assertions.'),
S('Restore and verify',I,'Reset the instructor-selected fault, then learners rerun their gate.',
r'''cd "$COURSE_ROOT"
sudo shared/scripts/fault.sh reset''','The same business checks that failed now succeed.','Do not declare recovery based only on the service becoming active.')],
'Instructor confirms reset. Leave your deployment script in your bin directory; do not add automatic restarts, database repairs or cron scheduling to this gate.',
['deployment-check.sh — completed learner script','deployment-test-matrix.md — before/fault/after outcomes and remaining blind spots'])

guide(3,8,'Complete the incident simulation. Have the report, evidence index, scripts and recovery transcript ready; no new fault is injected.',[
S('Collect your handover inputs',L,'List your own scripts and check each separately. This avoids treating later filenames as arguments to a single bash invocation.',
r'''find ~/support-lab/bin -maxdepth 1 -type f -name '*.sh' -print
for script in "$HOME"/support-lab/bin/*.sh; do
    [[ -e $script ]] || continue
    bash -n "$script" || break
done''','Each script passes syntax checks before submission.','A syntax pass is not a functional test; retain your healthy/failure transcripts too.'),
S('Prepare a five-minute handover','Learner · report editor','Summarize impact, UTC timeline, evidence paths, probable cause and confidence, mitigation, recovery tests and remaining risks. Name the next owner and next check.',expected='Another shift can locate evidence and repeat checks without a verbal explanation.',trouble='Do not present a hypothesis as a confirmed root cause just to make the report sound complete.'),
S('Defend a counterexample','Team review','Ask a peer to propose evidence that would contradict your diagnosis. Identify which captured observation distinguishes the alternatives.',expected='Your explanation connects a conclusion to evidence and acknowledges uncertainty.',trouble='If no discriminating evidence exists, state that limitation and propose the next measurement.'),
S('Write three actionable improvements','Learner · notes','For each improvement, state signal, threshold/window, owner, response and acceptance check. Separate detection, prevention and runbook improvements.',expected='Each recommendation can be assigned and tested; “monitor more” is replaced by a measurable action.',trouble='Do not invent production thresholds from a tiny training workload without labeling them provisional.'),
S('Review and submit','Learner · local review','Use the submission checklist below. Remove credentials from copies and verify that every referenced evidence file is included. Deliver a five-minute handover to the class.',expected='The recipient can read the report, find evidence and understand residual risk.',trouble='Missing evidence should be marked missing, not replaced with invented output.')],
'Confirm with the instructor that simulation faults and open transactions are cleared. Remove only your exercise cron entries if still active; retain reviewed artifacts for assessment.',
['handover.md — shift-ready incident summary','improvements.md — three owned, measurable actions','script-test-index.md — paths to scripts and their test evidence'])

def capstone(m,n,prereq,briefing,minutes,checks,files):
    steps=[
S('Prepare your submission workspace',L,'Create report copies in this exercise’s evidence directory. Open incident.md in your editor and fill the identity, scope and UTC start fields.',
rf'''cp "$COURSE_ROOT/shared/templates/incident-report.md" "$HOME/support-lab/evidence/m{m}-{n:02}/incident.md"
date -u +%FT%TZ
nano "$HOME/support-lab/evidence/m{m}-{n:02}/incident.md"''','A report exists before the fault is introduced; roles and start time are recorded.','If a prior report exists, make a dated copy before replacing it.'),
S('Receive the incident and assign roles','Team briefing with instructor',briefing+' Assign investigator, scribe/reviewer and incident lead. Only the instructor injects or resets the concealed fault.',expected='You know the business symptom, allowed targets, time budget and required deliverables, but not the root cause.',trouble='If the starting system was already unhealthy, ask the instructor to establish which symptoms belong to this scenario.'),
S('Investigate within the time budget','Learner · permitted shells/clients',minutes+' Record each hypothesis, discriminating check, observation and next action. The optional hints below suggest layers, not a solution.',expected='Your timeline contains evidence-linked observations rather than a list of guesses.',trouble='When a check is denied or returns no data, record that limitation and choose another permitted source; do not broaden privileges.'),
S('Collect and inspect evidence',L,'Use the collector as one input, not a replacement for your own reasoning. Check its manifest and preserve the returned path.',
rf'''cd "$COURSE_ROOT"
shared/scripts/collect-evidence.sh "$HOME/support-lab/evidence/m{m}-{n:02}/bundles" '20 minutes ago'
collector_rc=$?
printf 'collector_exit=%s\n' "$collector_rc"''','A full or partial bundle is available. Exit 1 can be valid partial evidence; inspect the manifest.', 'If packaging fails, preserve individual available outputs and explain the gap in your report.'),
S('Propose one mitigation and define recovery','Team decision; instructor performs privileged changes','State the supporting evidence, affected scope, rollback, responsible person and business verification before requesting the change. Do not run every fix you know.',expected='The instructor can review a concrete action; the report distinguishes diagnosis from speculation.',trouble='If evidence does not distinguish causes, request a further measurement instead of claiming certainty.'),
S('Verify and hand over','Learner · permitted probes and report editor',checks+' Record before/after outcomes, residual risks and a next owner. Review the submission checklist and optional hints without opening instructor answers.',expected='Recovery is supported by the affected business function and a clear observation window.',trouble='One green service indicator is insufficient if the original business request still fails.')]
    if m==1:
        steps.insert(1,S('Create your first evidence script',L,'Copy the starter, complete its TODOs and save it as triage.sh. Include service status, recent errors, disk use and timestamps. Keep investigating the hidden fault independently.',
r'''mkdir -p ~/support-lab/bin
cp "$COURSE_ROOT/shared/templates/triage-starter.sh" ~/support-lab/bin/triage.sh
nano ~/support-lab/bin/triage.sh
bash -n ~/support-lab/bin/triage.sh
chmod 750 ~/support-lab/bin/triage.sh
~/support-lab/bin/triage.sh''','Your script runs and captures observations without silently treating failures as healthy.','If syntax checking fails, fix it before execution. Compare the reference collector only after your first implementation.'))
    if m==2:
        steps.insert(1,S('Prepare database-specific evidence',L,'Copy the worksheet. Use the granted clients and diagnostic SQL; distinguish live evidence from the supplied fictional captures.',
r'''cp "$COURSE_ROOT/shared/templates/database-report.md" ~/support-lab/evidence/m2-09/database-report.md
"$COURSE_ROOT/shared/scripts/db-health.sh"
db_rc=$?
printf 'db_health_exit=%s\n' "$db_rc"''','A database worksheet and baseline result are available, including any failure status.','Do not place passwords in the worksheet or infer that every synthetic file is part of the same outage.'))
    guide(m,n,prereq,steps,
'After saving evidence, the instructor resets the assigned fault. Roll back any transactions opened during investigation in their owning sessions, close database clients and unset SQLCMDPASSWORD where used. Verify the affected business route again. Keep evidence and scripts; do not reset another team’s active scenario.',files,True)

capstone(1,8,'Complete Module 1 exercises 01–07. Instructor assigns one concealed fault and a shared-stack time slot.',
'The application was healthy before a change and now needs investigation.',
'Use 10 minutes for the starter script, 25 minutes for diagnosis/mitigation/recovery and 10 minutes for reporting and review.',
'Validate the affected route plus a representative player lookup; explain what changed and why.',
['triage.sh — executable learner script','incident.md — timeline and evidence-backed diagnosis','reviewed evidence bundle and completed Linux checklist'])
capstone(2,9,'Complete the live MySQL and SQL Server exercises. Instructor supplies a concealed live incident plus explicitly separate evidence packs.',
'Investigate the application/database symptoms without forcing all independent findings into one cause.',
'Use 10 minutes for role assignment and impact, 30 for investigation, 15 for mitigation/recovery and 25 for reporting/review.',
'Complete the MySQL ranking, SQL Server waits/blocking/Query Store/job worksheet, application timeline and a database-health script outline with timeouts and explicit unknown states.',
['incident.md — integrated timeline and recovery','database-report.md — MySQL and SQL Server analysis','db-health-outline.md — interface, permissions, checks, output and failure handling'])
capstone(3,7,'Complete the automation exercises. Instructor provides one incident card, allowed endpoints and a reserved team slot; scripts have passed their basic tests.',
'The instructor assigns loyalty outage, gaming delay or payment failure. Rotate incident commander, investigator and scribe; combine roles for teams of three. Write classroom stakeholder updates at minutes 15, 30 and 45 using the [stakeholder update template](../../shared/templates/stakeholder-update.md); do not send real external messages.',
'Use 10 minutes for briefing, 50 for investigation, 20 for mitigation/recovery and 30 for communications and handover preparation.',
'Use your own deployment checks on the affected business function and report the observation window. Submit three stakeholder updates, a reviewed bundle, incident report and handover notes.',
['incident.md — report with impact, timeline, evidence and confidence','updates.md — updates at minutes 15, 30 and 45','reviewed evidence bundle and script execution transcript'])

guide(1,9,'Complete the command investigations in Module 1 exercise 04. Use copies of synthetic files. This is optional extension work, not part of the 390-minute core day.',[
S('Create an isolated challenge workspace',L,'Copy fixtures into a new directory and record the path. Use that directory for the tasks.',
r'''mkdir -p ~/support-lab/challenges
challenge_dir=$(mktemp -d "$HOME/support-lab/challenges/commands-XXXXXX")
cp -a "$COURSE_ROOT/shared/fixtures/." "$challenge_dir/"
cd "$challenge_dir"
pwd''','All challenge mutations stay inside your new copy.','Do not work directly in the shared fixture directory.'),
S('Prepare an answer notebook','Learner · Markdown editor','For each of the 18 tasks in [Command challenges](../../shared/fixtures/command-challenges.md), record prediction, command, observed output, interpretation and one limitation. Work in groups of six tasks, reviewing after each group.',expected='The notebook has numbered sections 1–18 before you begin solving.',trouble='Do not open the instructor answer key during the attempt.'),
S('Solve and test counterexamples','Learner · Bash in the challenge directory','Follow the command bank step by step. Explain why a naive version fails before proposing a correction. Preserve source evidence and do not bypass an error without interpreting it.',expected='Each completed task includes a runnable approach and evidence supporting its behavior.',trouble='When stuck, use the optional hints below and the Linux desk reference. A prediction can be wrong; record what the observation taught you.'),
S('Review with another learner','Peer review','Exchange notebooks. Your reviewer runs one safe pipeline and checks one edge case, then flags missing assumptions or evidence.',expected='A second person can reproduce your result from the written steps.',trouble='Record a limitation if a command depends on GNU options or a particular log format.')],
'Keep the copied challenge workspace until review completes. Close any tail-following process with Ctrl-C. Remove only temporary files you created in that copy; leave originals untouched.',
['command-notebook.md — 18 numbered answers and counterexamples','peer-review.md — reproduction result and corrections'],True)

guide(3,9,'Complete the reference-script exercises and copy scripts to your own bin directory before editing. Optional extension; no production or live-host repair automation.',[
S('Create a hardening test matrix','Learner · Markdown editor','Create rows for healthy input, no data, malformed data, threshold equality, stale input, spaces in output paths, denied log access, timeout, overlapping execution and unrelated-file retention. State expected output/status before testing.',expected='The matrix separates OK, ALERT and UNKNOWN/invalid conditions.',trouble='Do not count unexecuted cases as passed.'),
S('Run the reference boundary checks',L,'Interpret both exit codes immediately. The second parser call still sees a 2100 ms request above its 2000 ms limit.',
r'''cd "$COURSE_ROOT"
shared/scripts/monitor-log.sh shared/fixtures/application.log 10 1000
first_rc=$?
shared/scripts/monitor-log.sh shared/fixtures/application.log 34 2000
second_rc=$?
printf 'first=%s second=%s\n' "$first_rc" "$second_rc"
shared/scripts/collect-evidence.sh "$HOME/support-lab/evidence/m3-09/output with spaces" '5 minutes ago' ''','Both parser results are ALERT/1; the collector handles spaces in the output path and reports its own completeness.', 'Do not assume raising the error-rate threshold disables the independent latency trigger.'),
S('Implement and test your extensions','Learner · own script copies','Add input freshness and overlap handling. Use a small local test input for stale timestamps, two local invocations for a lock, and the isolated retention HOME procedure from exercise 05. Do not change shared originals.',expected='Each claimed behavior has an observed pass/fail result and a bounded failure path.',trouble='If a dependency is unavailable, report UNKNOWN rather than returning healthy by default.'),
S('Design database automation boundaries','Learner · notes','Use replication and SQL Agent evidence to specify authenticated read-only checks, required permissions, expected states, unknown states and escalation outputs. You do not need to install a replica.',expected='The design states what the script can observe and which repairs remain operator decisions.',trouble='Do not create a fake live replication success result from the synthetic fixture.'),
S('Review the final patch','Peer review','Show your changed code and matrix to a peer. Ask them to reproduce one failure case and one recovery case.',expected='Your changes are understandable and the reported checks are reproducible.',trouble='Document remaining limitations rather than expanding scope into uncontrolled repair automation.')],
'Stop your own test processes and remove any added test cron entries. Keep the hardening patch and matrix; preserve real evidence and unrelated files.',
['hardening-tests.md — test matrix with actual results','hardened script copies and a short change explanation','database-monitor-design.md — permissions and state semantics'],True)


# Refine transitions that cross shared resources or execution contexts.
GUIDES[1,3]['steps'][4]['action'] = 'First remove the growth lab with the command below. Then follow sections C and D of [Storage demonstrations](../../shared/instructor/storage.md), which create fresh images. Do not repeat section B while a prior lab exists. Learners record symptom, bytes, inodes, quota, diagnosis and correction.'
GUIDES[1,3]['steps'][4]['where'] = I
GUIDES[1,3]['steps'][4]['code'] = 'sudo shared/scripts/storage-lab.sh cleanup'
GUIDES[1,3]['cleanup'] = 'The growth lab is removed before demonstrations C/D; each demonstration then performs its own cleanup. Confirm no lab image remains mounted. If interrupted with a growth lab still active, the instructor runs its cleanup helper after closing open handles. Do not rerun cleanup against an already removed lab or delete a mounted image.'
GUIDES[2,7]['steps'].insert(0,S(
    'Open three SQL client sessions','Learner · three SQL client Bash terminals',
    'In each terminal, repeat the connection-variable/password setup from exercise 06, including the approved SQL_TLS_ARGS choice. Launch an interactive client; omit -b here so an expected lock-timeout error does not terminate the session. Label the resulting connections A, B and Observer.',
    'sqlcmd "${SQL_TLS_ARGS[@]}" -S "tcp:$SQL_HOST,1433" -U "$SQL_LOGIN" -d SupportLab',
    'Each terminal shows its own sqlcmd prompt, ready for T-SQL and GO.',
    'If SQL_HOST, SQL_LOGIN or credentials are not set in that terminal, stop and repeat exercise 06 connection setup.'))
job_index=next(i for i,s in enumerate(GUIDES[2,7]['steps']) if s['title']=='Start and inspect the intentional job failure')
GUIDES[2,7]['steps'][job_index:job_index+1]=[
    S('Start the intentional job failure','Instructor · T-SQL',
      'Start only the named synthetic job, then tell learners when it has finished.',
      "EXEC msdb.dbo.sp_start_job @job_name=N'SupportLab-IntentionalFailure';\nGO",
      'The job is accepted for execution and fails deliberately shortly afterward.',
      'If SQL Agent is starting, wait and retry; do not create another job.','sql'),
    S('Read job history with the learner login','Learner · Observer T-SQL session',
      'After a few seconds, inspect history through the supported procedure.',
      "EXEC msdb.dbo.sp_help_jobhistory @job_name=N'SupportLab-IntentionalFailure', @mode=N'FULL';\nGO",
      'The failed step contains the synthetic training message.',
      'If history is denied, ask the instructor to check SQLAgentReaderRole; do not query protected base tables with an administrator account instead.','sql')]

release_index=next(i for i,s in enumerate(GUIDES[2,7]['steps']) if s['title']=='Observe and release the blocker')
GUIDES[2,7]['steps'][release_index]['title']='Observe the blocker'
GUIDES[2,7]['steps'][release_index]['where']='Observer · T-SQL'
GUIDES[2,7]['steps'][release_index]['action']='Run the query while B waits. Save the blocking relation before releasing either transaction in the following steps.'
GUIDES[2,7]['steps'][release_index+1:release_index+1]=[
    S('Release A’s transaction','Session A · T-SQL',
      'Release the head blocker only after the observation is recorded. B may now finish its UPDATE; it still needs its own rollback.',
      'IF @@TRANCOUNT > 0 ROLLBACK;\nSELECT @@TRANCOUNT AS open_transactions;\nGO',
      'A has zero open transactions. B either finishes or has already reported its bounded timeout.',
      'Do not assume B’s transaction ended just because A rolled back.','sql'),
    S('Release B and verify data','Session B · T-SQL',
      'Run this whether B succeeded after the release or timed out. Then verify the seeded points.',
      'IF @@TRANCOUNT > 0 ROLLBACK;\nSELECT @@TRANCOUNT AS open_transactions;\nSELECT id,points FROM dbo.Players ORDER BY id;\nGO',
      'B has zero open transactions; player 1 has 100 points and player 2 has 200 on the unchanged seed.',
      'If values differ, ask the instructor about other team writes; do not silently overwrite shared data.','sql')]

def render_exercise(m,n,lab):
    g=GUIDES[m,n]
    minutes=f"{lab['minutes']} minutes" if isinstance(lab['minutes'],int) else 'Optional extension'
    slug=f'm{m}-{n:02}'
    pieces=[f"# {lab['title']}",f"**Time:** {minutes}  \n**Working mode:** {'Guided setup; independent diagnosis' if g['challenge'] else 'Guided walkthrough'}",
        '| Difficulty | Delivery | Sessions |\n|---|---|---|\n| '+g['difficulty']+' | '+g['delivery']+' | '+g['sessions']+' |',
        '**Deliverables:** '+ '; '.join(g['files']),
        '[Walkthrough](#step-by-step-walkthrough) · [Submit](#submission-checklist) · [Recovery](#cleanup-and-recovery)',
        '## Before you start',g['prerequisites'],
        'Read the [Learner setup and terminal guide](../../shared/learner-start.md). It explains the local workstation, application-server SSH shell and database-client prompts. Set `COURSE_ROOT` in each Bash session that uses course files; an SSH session does not inherit workstation variables.',
        '## Situation',lab['scenario'],'## Learning goals','\n'.join('- '+x for x in lab['concepts'])]
    if (m,n)!=(1,1):
        pieces += ['## Prepare this exercise workspace',
            '**Where and who:** Learner · Bash on the host where the course files are installed. For SQL-client exercises, repeat this preparation on that client host if it is separate.',
            'Enter the actual absolute course directory if it has not been set in this shell. Do not paste a path copied from the authoring workstation.',
            rf'''```bash
if [[ -z ${{COURSE_ROOT:-}} ]]; then
    read -r -p 'Absolute course directory on this host: ' COURSE_ROOT
    export COURSE_ROOT
fi
if cd "$COURSE_ROOT" && test -f shared/fixtures/application.log; then
    mkdir -p "$HOME/support-lab/evidence/{slug}" && printf 'Workspace ready\n'
else
    printf 'STOP: confirm the course directory before continuing.\n' >&2
fi
```''',
            '**Expected result:** Workspace ready is printed only after the course directory and fixture are confirmed and the evidence directory is prepared.',
            '**If it differs:** Stop if `cd` or `test` fails. Confirm the instructor-provided path before running relative commands.']
    pieces += ['**Repeat run:** '+g['repeat']]
    if g.get('sequence'): pieces += ['## Session sequence',g['sequence']]
    pieces += ['## Step-by-step walkthrough']
    for i,s in enumerate(g['steps'],1):
        instructor=s['where'].startswith('Instructor')
        action=('Observe the instructor demonstration. Before the change, predict the result; after it, record the evidence and explain the verification. Execution commands are in the instructor guide. '+ ('This is an optional live extension.' if s['title'].startswith('Live extension') else '')) if instructor else s['action']
        pieces += [f"### Step {i} — {s['title']}",f"**Where and who:** {s['where']}",action]
        if s['code'] and not instructor:pieces.append(f"```{s['language']}\n{s['code'].strip()}\n```")
        pieces += [f"**Expected result:** {s['expected']}",f"**If it differs:** {s['trouble']}"]
    if g['challenge']:
        pieces += ['## Optional hints',
            '<details>\n<summary>Hint 1 — narrow the question</summary>\n\nState the affected business function, UTC window and the layer your next check tests. Compare the observation with a known baseline.\n\n</details>',
            '<details>\n<summary>Hint 2 — interpret the result</summary>\n\nSeparate transport, authentication, service state and business behavior. For command challenges, identify input format, quoting, delimiters and exit-code assumptions. Record unavailable evidence explicitly.\n\n</details>',
            '<details>\n<summary>Hint 3 — organize the next action</summary>\n\nUse the relevant prior walkthrough or reference script to collect evidence. State what would disprove your hypothesis. Ask the instructor for the next permitted observation without requesting the answer key.\n\n</details>']
    pieces += ['## Check your understanding','\n'.join(f'{i}. {q}' for i,q in enumerate(lab['tricks'],1)),
        '## Submission checklist','Save the following under `~/support-lab/evidence/'+slug+'` or reference a reviewed artifact stored elsewhere. Record UTC time and distinguish live output from synthetic fixtures.',
        '\n'.join('- [ ] '+x for x in g['files']),
        '- [ ] Include interpretation, expected failures, unavailable evidence and remaining uncertainty.\n- [ ] Review copies for credentials before sharing; never submit your private key or client password file.',
        '## Cleanup and recovery',g['cleanup'],
        '## Completion criteria','\n'.join('- [ ] '+x for x in lab['checks'])]
    navigation=['[Module agenda](../README.md)']
    if g['previous']: navigation.insert(0,'[Previous exercise]('+g['previous']+'.md)')
    if g['next']: navigation.append('[Next exercise]('+g['next']+'.md)')
    pieces += [' · '.join(navigation)]
    return '\n\n'.join(pieces)+'\n'
