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

mkdir -p "$WORK_DIR/nocloud"
sed "s|__RTYLR_INSTALL_PASSWORD_HASH__|${INSTALL_PASSWORD_HASH}|g" \
  "$ROOT_DIR/config/autoinstall.yaml" > "$WORK_DIR/nocloud/user-data"
: > "$WORK_DIR/nocloud/meta-data"
if grep -q '__RTYLR_INSTALL_PASSWORD_HASH__' "$WORK_DIR/nocloud/user-data"; then
  printf 'Password placeholder remained in generated autoinstall data.\n' >&2
  exit 1
fi

if [[ -f "$WORK_DIR/boot/grub/grub.cfg" ]]; then
  perl -0pi -e 's/(\s+linux\s+[^\n]*?)(\s+---|\s+quiet)/$1 autoinstall ds=nocloud\\;s=\/cdrom\/nocloud\/ $2/g' "$WORK_DIR/boot/grub/grub.cfg"
else
  printf 'Ubuntu ISO does not contain boot/grub/grub.cfg\n' >&2
  exit 1
fi

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
