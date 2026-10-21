# Storage diagnosis worksheet

Use this during Module 1 exercise 03. Instructor demonstrations use disposable images; learners record observations. No learner repartitions the shared EC2 root disk.

| Layer | Evidence to record | What the evidence establishes |
|---|---|---|
| Device | `lsblk` size | Capacity presented by the volume or loop image |
| Partition | `lsblk` child size | Space assigned to the partition |
| Filesystem bytes | `df -hT` | Allocated filesystem capacity and available bytes |
| Filesystem inodes | `df -i` | Availability of file metadata entries |
| User quota | `quota -s`; instructor quota report | Per-user limits where quotas are enabled |
| Permissions | `id`; directory and file modes | Whether this identity may access the path |

1. Capture the baseline and identify the actual mounted filesystem for your home directory.
2. Predict what `df` will show if only the underlying device grows.
3. Observe disposable image, partition and ext4 growth. Record before/after sizes; filesystem metadata means raw and usable sizes differ.
4. Observe a quota allocation. Compare another user's ability to write to the same filesystem. Explain why a user limit does not imply a small disk.
5. Sketch the EBS sequence: approved volume expansion, verify device size, grow the correct partition where present, grow the filesystem using its supported tool, verify capacity and application writes. XFS, ext4 and LVM require different procedures; do not infer device names.
6. Complete cases A–C in the exercise, choosing a discriminating check before a correction.

Quota demonstration is guided. Deleted-open-file and inode exhaustion demonstrations are optional extensions. For deleted-open files, compare directory-visible usage against filesystem usage and inspect open handles with the instructor. Record unavailable evidence explicitly.

Keep earlier measurements on a repeat run. Shared demonstration cleanup belongs to the instructor, who confirms the disposable image is no longer mounted.
