#!/usr/bin/env bash
# shellcheck disable=SC2016
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="$(tr -d '[:space:]' < "$ROOT_DIR/VERSION")"
BASE="${ROOT_DIR}/cache/ubuntu-26.04-live-server-amd64.iso"
WORK_DIR="${ROOT_DIR}/work/iso"
DIST_DIR="${ROOT_DIR}/dist"
OUTPUT="${DIST_DIR}/rtylr-os-${VERSION}-amd64.iso"

die() { printf '%s\n' "$*" >&2; exit 1; }

[[ -f "$BASE" ]] || die 'Verified base ISO is required before building.'
[[ -n "${RTYLR_INSTALL_PASSWORD_HASH:-}" ]] ||
  die 'RTYLR_INSTALL_PASSWORD_HASH is required; do not embed a reusable password in the image.'
[[ "$RTYLR_INSTALL_PASSWORD_HASH" =~ ^\$[0-9a-z]+\$[^[:space:]\"]+$ ]] ||
  die 'RTYLR_INSTALL_PASSWORD_HASH does not look like a crypt(3) hash (e.g. $6$salt$hash).'

rm -rf "$WORK_DIR"
mkdir -p "$WORK_DIR/nocloud" "$WORK_DIR/boot/grub" "$DIST_DIR"

# Extract only the two files we modify instead of unpacking the whole ISO.
printf 'Extracting boot config from Ubuntu base ISO...\n'
xorriso -osirrox on -indev "$BASE" \
  -extract /boot/grub/grub.cfg "$WORK_DIR/boot/grub/grub.cfg" \
  -extract /md5sum.txt "$WORK_DIR/md5sum.txt" >/dev/null
chmod u+w "$WORK_DIR/boot/grub/grub.cfg" "$WORK_DIR/md5sum.txt"

# Render the autoinstall user-data.
RTYLR_PACKAGES="[$(grep -vE '^[[:space:]]*(#|$)' "$ROOT_DIR/config/packages.list" | paste -sd, - | sed 's/,/, /g')]"
RTYLR_SHUTDOWN=reboot
RTYLR_EXTRA_LATE=''
if [[ "${RTYLR_TEST_BUILD:-}" == "1" ]]; then
  # Test images power off after install and log to the serial console so
  # scripts/test-vm.sh can drive them headlessly. Never ship these.
  RTYLR_SHUTDOWN=poweroff
  # shellcheck disable=SC2089
  RTYLR_EXTRA_LATE=$'    - sed -i \'s/^GRUB_CMDLINE_LINUX=.*/GRUB_CMDLINE_LINUX="console=ttyS0,115200n8"/\' /target/etc/default/grub\n    - curtin in-target -- update-grub\n'
  printf 'WARNING: building a TEST image (serial console, poweroff after install).\n' >&2
fi
# shellcheck disable=SC2090
export RTYLR_PACKAGES RTYLR_SHUTDOWN RTYLR_EXTRA_LATE RTYLR_INSTALL_PASSWORD_HASH
perl -pe '
  s/__RTYLR_INSTALL_PASSWORD_HASH__/$ENV{RTYLR_INSTALL_PASSWORD_HASH}/g;
  s/__RTYLR_PACKAGES__/$ENV{RTYLR_PACKAGES}/g;
  s/__RTYLR_SHUTDOWN__/$ENV{RTYLR_SHUTDOWN}/g;
  s/^[ \t]*# __RTYLR_EXTRA_LATE_COMMANDS__\n/$ENV{RTYLR_EXTRA_LATE}/;
' "$ROOT_DIR/config/autoinstall.yaml" > "$WORK_DIR/nocloud/user-data"
: > "$WORK_DIR/nocloud/meta-data"
grep -q '__RTYLR_' "$WORK_DIR/nocloud/user-data" && die 'Unrendered placeholder left in user-data.'

# Add the autoinstall datasource to every kernel line that has a "---" marker.
perl -pi -e 's{^(\s*linux\s+\S+.*?)\s+---}{$1 autoinstall ds=nocloud\\;s=/cdrom/nocloud/ ---}' \
  "$WORK_DIR/boot/grub/grub.cfg"
grep -q 'ds=nocloud' "$WORK_DIR/boot/grub/grub.cfg" ||
  die 'Failed to patch grub.cfg: no kernel line matched; the Ubuntu ISO layout may have changed.'

# Keep the installer media integrity list consistent with the patched file.
new_md5="$(md5sum "$WORK_DIR/boot/grub/grub.cfg" | cut -d' ' -f1)"
MD5="$new_md5" perl -pi -e 's{^\S+(\s+\./boot/grub/grub\.cfg)$}{$ENV{MD5}$1}' "$WORK_DIR/md5sum.txt"

printf 'Creating customized ISO...\n'
xorriso \
  -indev "$BASE" \
  -outdev "$OUTPUT" \
  -boot_image any replay \
  -map "$WORK_DIR/boot/grub/grub.cfg" /boot/grub/grub.cfg \
  -map "$WORK_DIR/md5sum.txt" /md5sum.txt \
  -map "$WORK_DIR/nocloud" /nocloud \
  -map "$ROOT_DIR/config" /rtylr-config \
  -map "$ROOT_DIR/scripts/first-boot.sh" /scripts/first-boot.sh \
  -volid RTYLR_OS \
  -commit \
  -end

printf 'Built %s\n' "$OUTPUT"
