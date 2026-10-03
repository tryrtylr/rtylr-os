#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BASE="${ROOT_DIR}/cache/ubuntu-26.04-live-server-amd64.iso"
WORK_DIR="${ROOT_DIR}/work/iso"
DIST_DIR="${ROOT_DIR}/dist"
VERSION="$(tr -d '[:space:]' < "${ROOT_DIR}/VERSION")"
OUTPUT="${DIST_DIR}/rtylr-os-${VERSION}-amd64.iso"
SHELL_STAGE="${WORK_DIR}/rtylr-shell"
INSTALL_PASSWORD_HASH="${RTYLR_INSTALL_PASSWORD_HASH:-!}"

[[ -f "$BASE" ]] || { printf 'Verified base ISO is required before building.\n' >&2; exit 1; }
[[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+([.-][0-9A-Za-z.-]+)?$ ]] || {
  printf 'VERSION is not a valid release version: %s\n' "$VERSION" >&2
  exit 1
}
if [[ "$INSTALL_PASSWORD_HASH" != "!" && ! "$INSTALL_PASSWORD_HASH" =~ ^\$(5|6|y)\$ ]]; then
  printf 'RTYLR_INSTALL_PASSWORD_HASH must be a SHA-256, SHA-512, yescrypt hash, or !.\n' >&2
  exit 1
fi
rm -rf "$WORK_DIR"
mkdir -p "$WORK_DIR" "$DIST_DIR"
rm -f "$OUTPUT" "${OUTPUT}.sha256"

printf 'Extracting the Ubuntu boot configuration...\n'
mkdir -p "$WORK_DIR/boot/grub"
xorriso -osirrox on -indev "$BASE" \
  -extract /boot/grub/grub.cfg "$WORK_DIR/boot/grub/grub.cfg" \
  >/dev/null 2>&1

chmod u+w "$WORK_DIR/boot/grub/grub.cfg"

# Render the autoinstall user-data from config/autoinstall.yaml.
RTYLR_PACKAGES="[$(grep -vE '^[[:space:]]*(#|$)' "$ROOT_DIR/config/packages.list" | paste -sd, - | sed 's/,/, /g')]"
RTYLR_SHUTDOWN=reboot
RTYLR_EXTRA_LATE=''
if [[ "${RTYLR_TEST_BUILD:-}" == "1" ]]; then
  # Test images power off after install and log to the serial console so
  # scripts/test-vm.sh can drive them headlessly. Never ship these.
  RTYLR_SHUTDOWN=poweroff
  # shellcheck disable=SC2016,SC2089
  RTYLR_EXTRA_LATE=$'    - sed -i \'s/^GRUB_CMDLINE_LINUX=.*/GRUB_CMDLINE_LINUX="console=ttyS0,115200n8"/\' /target/etc/default/grub\n    - curtin in-target -- update-grub\n'
  printf 'WARNING: building a TEST image (serial console, poweroff after install).\n' >&2
fi
RTYLR_INSTALL_PASSWORD_HASH="$INSTALL_PASSWORD_HASH"
# shellcheck disable=SC2090
export RTYLR_PACKAGES RTYLR_SHUTDOWN RTYLR_EXTRA_LATE RTYLR_INSTALL_PASSWORD_HASH
mkdir -p "$WORK_DIR/nocloud"
perl -pe '
  s/__RTYLR_INSTALL_PASSWORD_HASH__/$ENV{RTYLR_INSTALL_PASSWORD_HASH}/g;
  s/__RTYLR_PACKAGES__/$ENV{RTYLR_PACKAGES}/g;
  s/__RTYLR_SHUTDOWN__/$ENV{RTYLR_SHUTDOWN}/g;
  s/^[ \t]*# __RTYLR_EXTRA_LATE_COMMANDS__\n/$ENV{RTYLR_EXTRA_LATE}/;
' "$ROOT_DIR/config/autoinstall.yaml" > "$WORK_DIR/nocloud/user-data"
: > "$WORK_DIR/nocloud/meta-data"
if grep -q '__RTYLR_' "$WORK_DIR/nocloud/user-data"; then
  printf 'Unrendered placeholder remained in generated autoinstall data.\n' >&2
  exit 1
fi

perl -pi -e 's{^(\s*linux\s+\S+.*?)\s+---}{$1 autoinstall ds=nocloud\\;s=/cdrom/nocloud/ ---}' "$WORK_DIR/boot/grub/grub.cfg"
grep -Fq 'autoinstall ds=nocloud' "$WORK_DIR/boot/grub/grub.cfg" || {
  printf 'Failed to patch grub.cfg: no kernel line matched; the Ubuntu ISO layout may have changed.\n' >&2
  exit 1
}

# Keep the installer media integrity list consistent with the patched file.
xorriso -osirrox on -indev "$BASE" -extract /md5sum.txt "$WORK_DIR/md5sum.txt" >/dev/null 2>&1
chmod u+w "$WORK_DIR/md5sum.txt"
MD5="$(md5sum "$WORK_DIR/boot/grub/grub.cfg" | cut -d' ' -f1)" \
  perl -pi -e 's{^\S+(\s+\./boot/grub/grub\.cfg)$}{$ENV{MD5}$1}' "$WORK_DIR/md5sum.txt"

# Stage only source assets needed by the appliance. Development bytecode can be
# incompatible with the target Python version and does not belong in the ISO.
mkdir -p "$SHELL_STAGE"
rsync -a \
  --exclude '__pycache__/' \
  --exclude '*.pyc' \
  --exclude '*.pyo' \
  "$ROOT_DIR/src/rtylr-shell/" "$SHELL_STAGE/"

printf 'Creating customized ISO...\n'
xorriso \
  -indev "$BASE" \
  -outdev "$OUTPUT" \
  -boot_image any replay \
  -map "$WORK_DIR/boot/grub/grub.cfg" /boot/grub/grub.cfg \
  -map "$WORK_DIR/md5sum.txt" /md5sum.txt \
  -map "$WORK_DIR/nocloud" /nocloud \
  -map "$ROOT_DIR/config" /rtylr-config \
  -map "$SHELL_STAGE" /rtylr-shell \
  -map "$ROOT_DIR/scripts/first-boot.sh" /scripts/first-boot.sh \
  -map "$ROOT_DIR/VERSION" /rtylr-version \
  -volid RTYLROS \
  -commit \
  -end

(cd "$DIST_DIR" && sha256sum "$(basename "$OUTPUT")" > "$(basename "$OUTPUT").sha256")
printf 'Built %s\n' "$OUTPUT"
