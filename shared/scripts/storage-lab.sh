#!/usr/bin/env bash
# Disposable 320 MiB image; never accepts a device supplied by a student.
set -euo pipefail
[[ $EUID -eq 0 ]] || { echo 'sudo required'; exit 1; }
root=/var/lib/support-storage-lab
case ${1:-} in
 create)
  [[ ! -e $root ]] || { echo 'Lab exists; inspect or clean up first'; exit 1; }
  install -d -m 700 "$root"
  truncate -s 192M "$root/disk.img"
  parted -s "$root/disk.img" mklabel msdos mkpart primary ext4 1MiB 100%
  loop=$(losetup --find --show --partscan "$root/disk.img")
  printf '%s\n' "$loop" > "$root/loop"
  udevadm settle
  mkfs.ext4 -q "${loop}p1"
  mkdir "$root/mount"; mount "${loop}p1" "$root/mount"
  echo "Disposable device: $loop; mount: $root/mount";;
 grow)
  loop=$(cat "$root/loop")
  [[ $(losetup -n -O BACK-FILE "$loop") == "$root/disk.img" ]] || exit 1
  truncate -s 320M "$root/disk.img"; losetup -c "$loop"
  echo 'Device expanded. Compare lsblk and df before the next steps.'
  growpart "$loop" 1
  partprobe "$loop"; udevadm settle
  resize2fs "${loop}p1"
  df -hT "$root/mount";;
 cleanup)
  loop=$(cat "$root/loop")
  [[ $(losetup -n -O BACK-FILE "$loop") == "$root/disk.img" ]] || exit 1
  umount "$root/mount"; losetup -d "$loop"
  rm -rf -- "$root";;
 *) echo 'Usage: storage-lab.sh {create|grow|cleanup}'; exit 2;;
esac
