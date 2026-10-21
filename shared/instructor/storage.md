# Guided instructor storage demonstrations

These demonstrations support Module 1 exercise 03. The instructor performs every privileged step while learners record observations. Reserve the shared lab slot. Use only the named disposable images; never substitute the EC2 root device.

**Before starting:** Know the absolute course directory and set `COURSE_ROOT` in your instructor Bash session. Install the lab prerequisites before class: parted, cloud-guest-utils, e2fsprogs, quota, lsof and python3. Keep the instructor shell open between steps that use shell variables. Stop at an unexpected error rather than pasting the remaining blocks.

## A. Diagnose the reported limit first

### Step A1 — Record the affected user and path

**Where and who:** Learner Bash on the application host.

```bash
id
findmnt -T "$HOME"
df -hT "$HOME"
df -i "$HOME"
quota -s
```

**Expected result:** A device/filesystem mapping, byte usage, inode usage and any visible quota. Record the exact failed-write message if one exists.

**If it differs:** A missing quota tool is unavailable evidence, not proof of no quota. Permission denied, disk quota exceeded and no space left on device are different clues.

### Step A2 — Add instructor-only evidence

**Where and who:** Instructor Bash; read-only checks.

```bash
sudo repquota -a
sudo lsof +L1
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS
```

**Expected result:** The instructor can explain whether the report points to capacity, inodes, quotas, access permissions or deleted-open data. Empty output may be valid on a healthy host.

**If it differs:** Record permissions/tool limitations. Do not change partition layout solely because someone describes a “user cap.”

## B. Grow a disposable partition and filesystem

### Step B1 — Inspect and create the lab

**Where and who:** Instructor Bash, course directory.

```bash
cd "$COURSE_ROOT"
less shared/scripts/storage-lab.sh
sudo shared/scripts/storage-lab.sh create
```

**Expected result:** The helper prints a loop device backed by its own 192 MiB image and a mount at `/var/lib/support-storage-lab/mount`. Press q to exit less before running the helper.

**If it differs:** If the lab already exists, check who owns the exercise before cleanup or reuse. Never redirect the helper to another disk.

### Step B2 — Capture before-state

```bash
sudo lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS
sudo df -hT /var/lib/support-storage-lab/mount
```

**Expected result:** The filesystem is smaller than the raw image because of partition/filesystem metadata. Learners record both values.

**If it differs:** Confirm the expected mount with `sudo findmnt /var/lib/support-storage-lab/mount` before proceeding.

### Step B3 — Explain and execute the three growth stages

Read the grow branch aloud: increase backing image/device capacity, expand the partition with growpart, then grow ext4 with resize2fs. The helper executes these stages consecutively; it does not pause between them.

```bash
sudo shared/scripts/storage-lab.sh grow
sudo lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS
sudo df -hT /var/lib/support-storage-lab/mount
```

**Expected result:** The image is 320 MiB and the mounted filesystem has more capacity. The host root partition is untouched.

**If it differs:** Record which stage failed and inspect the helper's stored loop association. Do not apply the same command to a different device as a guess.

### Step B4 — Clean up before the next demonstration

```bash
sudo shared/scripts/storage-lab.sh cleanup
```

**Expected result:** The lab unmounts, detaches its loop device and removes its own image/directory.

**If it differs:** A busy mount must be investigated and its users closed first. Do not delete an image while mounted.

## C. Disk pressure and deleted-open files

### Step C1 — Create a fresh image and enter a root shell

**Where and who:** Instructor Bash. A fresh lab is required after demonstration B.

```bash
cd "$COURSE_ROOT"
sudo shared/scripts/storage-lab.sh create
sudo -i
```

The following C steps run in this same root shell; `COURSE_ROOT` may not be inherited there.

```bash
mountpoint -q /var/lib/support-storage-lab/mount
```

**Expected result:** The mount check returns 0 with no output.

**If it differs:** Stop. Do not run the write test against an ordinary directory on the host root filesystem.

### Step C2 — Fill only the small disposable filesystem

```bash
dd if=/dev/zero of=/var/lib/support-storage-lab/mount/fill.bin bs=1M count=200 status=none
write_rc=$?
printf 'write_exit=%s\n' "$write_rc"
df -hT /var/lib/support-storage-lab/mount
df -i /var/lib/support-storage-lab/mount
```

**Expected result:** The bounded 200 MiB write exhausts the roughly 190 MiB filesystem and returns a nonzero result with no space left on device. Inodes need not be exhausted.

**If it differs:** Confirm that this is the fresh 192 MiB image, not the grown 320 MiB image. Do not increase the write size blindly.

### Step C3 — Remove the test file and open another

```bash
rm /var/lib/support-storage-lab/mount/fill.bin
python3 -c 'import time; f=open("/var/lib/support-storage-lab/mount/open.bin","wb"); f.write(b"x"*20*1024*1024); f.flush(); time.sleep(120)' &
held_pid=$!
sleep 2
stat -c '%s %n' /var/lib/support-storage-lab/mount/open.bin
```

**Expected result:** The new file is 20 MiB and the recorded process holds it open for up to 120 seconds. Continue promptly to the next step.

**If it differs:** If the file is missing or incomplete, inspect the process before deleting anything. Do not use an unrelated PID.

### Step C4 — Remove the name while retaining the open handle

```bash
rm /var/lib/support-storage-lab/mount/open.bin
lsof +L1 | head
df -h /var/lib/support-storage-lab/mount
du -sh /var/lib/support-storage-lab/mount
```

**Expected result:** The open file appears deleted while its data can still consume filesystem space. Compare df with du.

**If it differs:** The 120-second process may already have exited. Record that timing issue and repeat only this bounded demonstration if needed.

### Step C5 — Release the owned process and clean up

```bash
kill "$held_pid"
wait "$held_pid" 2>/dev/null || true
df -h /var/lib/support-storage-lab/mount
exit
```

**Expected result:** Space is reclaimed and exit returns to the original non-root instructor shell. If the bounded worker has already exited, kill may report no such process; confirm its completion instead of choosing another PID.

Back in the original instructor shell:

```bash
cd "$COURSE_ROOT"
sudo shared/scripts/storage-lab.sh cleanup
```

**If cleanup fails:** Inspect a busy mount and close its users first. In a real incident, coordinate a controlled reopen/restart with the owner; this exercise does not authorize arbitrary process termination.

## D. Allocate and enforce a learner quota

### Step D1 — Select a real learner and create a fresh image

**Where and who:** Instructor opens a root shell. Keep it open through D7.

```bash
sudo -i
read -r -p 'Existing learner account: ' quota_user
id "$quota_user"
```

**Expected result:** The account exists. Stop if id fails.

```bash
qdir=/var/lib/support-quota-lab
[ ! -e "$qdir" ] || exit 1
install -d -m 755 "$qdir"
truncate -s 128M "$qdir/quota.img"
qloop=$(losetup --find --show "$qdir/quota.img")
printf '%s\n' "$qloop" > "$qdir/loop"
losetup "$qloop"
```

**Expected result:** The loop device maps to this new quota.img. An existing lab directory exits this root shell instead of overwriting it.

**If it differs:** Stop before formatting. Verify the actual backing file, not a guessed device name.

### Step D2 — Format only that new loop image and mount it

```bash
mkfs.ext4 -q -O quota "$qloop"
mkdir "$qdir/mount"
mount -o usrquota "$qloop" "$qdir/mount"
quotaon -p "$qdir/mount"
```

**Expected result:** The filesystem uses ext4 internal quota metadata. Inspect whether user quota enforcement is ON.

**If it differs:** If user enforcement is OFF, run `quotaon -u "$qdir/mount"`, then repeat the status check. If it cannot be enabled, stop and investigate kernel/filesystem support; do not claim the quota demonstration worked.

### Step D3 — Set a small per-user allocation

```bash
quota_group=$(id -gn "$quota_user")
install -d -o "$quota_user" -g "$quota_group" "$qdir/mount/$quota_user"
setquota -u "$quota_user" 8192 10240 0 0 "$qdir/mount"
repquota "$qdir/mount"
```

**Expected result:** The learner has an 8 MiB soft limit and 10 MiB hard limit; block-limit units here are KiB. The inode limits are unlimited in this example.

**If it differs:** Check the learner identity and mount. Do not apply these limits to the host's real home filesystem.

### Step D4 — Reproduce the limit as the learner

```bash
runuser -u "$quota_user" -- dd if=/dev/zero of="$qdir/mount/$quota_user/test.bin" bs=1M count=12 status=none
quota_write_rc=$?
printf 'quota_write_exit=%s\n' "$quota_write_rc"
repquota "$qdir/mount"
df -h "$qdir/mount"
```

**Expected result:** The learner receives quota exceeded before writing 12 MiB even though the filesystem still has free space. The write must run as the learner; root may bypass the quota.

**If it differs:** Confirm enforcement, file ownership and effective user. Do not diagnose a quota based solely on a small file size.

### Step D5 — Allocate more and retry the same request

```bash
setquota -u "$quota_user" 16384 20480 0 0 "$qdir/mount"
runuser -u "$quota_user" -- dd if=/dev/zero of="$qdir/mount/$quota_user/test.bin" bs=1M count=12 status=none
stat -c '%s %n' "$qdir/mount/$quota_user/test.bin"
repquota "$qdir/mount"
```

**Expected result:** The 12 MiB write succeeds under the new 16/20 MiB limits. No EBS partition was needed to change this per-user limit.

**If it differs:** Inspect the actual write error and quota report before changing another layer.

### Step D6 — Unmount and detach before deleting the image

```bash
rm "$qdir/mount/$quota_user/test.bin"
umount "$qdir/mount"
losetup -d "$qloop"
```

**Expected result:** Both unmount and detach succeed. Stop if either fails.

**If it differs:** Find and close the process using the mount. Do not proceed to file deletion while the filesystem is mounted.

### Step D7 — Remove only the lab files and leave root

```bash
rm "$qdir/quota.img" "$qdir/loop"
rmdir "$qdir/mount" "$qdir"
exit
```

**Expected result:** The named quota lab is removed and you are back in the instructor's original shell. The learner account remains available.

## E. Optional inode exhaustion extension

### Step E1 — Prepare a separate small image

**Where and who:** Instructor root shell; no other inode lab may exist.

```bash
sudo -i
idir=/var/lib/support-inode-lab
[ ! -e "$idir" ] || exit 1
install -d -m 700 "$idir"
truncate -s 32M "$idir/inodes.img"
iloop=$(losetup --find --show "$idir/inodes.img")
printf '%s\n' "$iloop" > "$idir/loop"
mkfs.ext4 -q -N 256 "$iloop"
mkdir "$idir/mount"
mount "$iloop" "$idir/mount"
```

**Expected result:** A separate disposable ext4 filesystem has a small inode pool.

**If it differs:** Verify the loop backing file before any formatting or mounting; stop if setup fails.

### Step E2 — Create at most 400 empty files and compare resources

```bash
for number in $(seq 1 400); do
    touch "$idir/mount/item-$number" || break
done
df -i "$idir/mount"
df -h "$idir/mount"
```

**Expected result:** Inodes exhaust before data capacity; the loop stops at the first failed creation.

**If it differs:** Record the filesystem's actual inode count. Do not escalate to millions of files on root storage.

### Step E3 — Clean up the inode demonstration

```bash
find "$idir/mount" -maxdepth 1 -type f -name 'item-*' -delete
umount "$idir/mount"
losetup -d "$iloop"
```

After both unmount and detach succeed:

```bash
rm "$idir/inodes.img" "$idir/loop"
rmdir "$idir/mount" "$idir"
exit
```

**Expected result:** The named lab is removed; no mounted image is deleted.

**If it differs:** Stop on a busy unmount and identify its users before continuing.

## F. EBS decision walkthrough — no live resize in class

1. Map the actual AWS volume to the Linux device and mount; record filesystem type and whether partitions/LVM are present.
2. Explain the snapshot/recovery preparation and EBS capacity modification. Confirm the cloud modification state before guest expansion.
3. For a partitioned non-LVM device, explain `growpart DEVICE PARTITION_NUMBER` using labels on a diagram, not a copied root-device command.
4. Match filesystem growth to the filesystem: `resize2fs PARTITION` for ext4; `xfs_growfs MOUNTPOINT` for XFS. LVM adds PV/LV stages that require a different procedure.
5. Verify device, partition and filesystem capacities separately; then retry the affected user's write and inspect quota/permission evidence if it still fails.

**Expected result:** Learners can choose a procedure from evidence instead of assuming every space issue needs repartitioning.

## Evidence and completion checklist

- [ ] Learners recorded before/after capacities, inode/quota evidence and expected write failures.
- [ ] The quota experiment used the learner identity, not root, for test writes.
- [ ] All temporary workers ended; every lab mount was unmounted before its backing image was removed.
- [ ] Root storage was not resized or filled, and learner accounts remain available.
- [ ] Any unexecuted/failed demonstration is labeled honestly in the class record.

References: [AWS filesystem extension](https://docs.aws.amazon.com/ebs/latest/userguide/recognize-expanded-volume-linux.html), [Red Hat ext4 quotas](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/10/html/managing_file_systems/limiting-storage-space-usage-on-ext4-with-quotas).
