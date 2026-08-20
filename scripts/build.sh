#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BASE="${ROOT_DIR}/cache/ubuntu-26.04-live-server-amd64.iso"
WORK_DIR="${ROOT_DIR}/work/iso"
DIST_DIR="${ROOT_DIR}/dist"
OUTPUT="${DIST_DIR}/rtylr-os-0.1.0-amd64.iso"

[[ -f "$BASE" ]] || { printf 'Verified base ISO is required before building.\n' >&2; exit 1; }
[[ -n "${RTYLR_INSTALL_PASSWORD_HASH:-}" ]] || {
  printf 'RTYLR_INSTALL_PASSWORD_HASH is required; do not embed a reusable password in the image.\n' >&2
  exit 1
}
rm -rf "$WORK_DIR"
mkdir -p "$WORK_DIR" "$DIST_DIR"

printf 'Extracting Ubuntu base ISO...\n'
bsdtar -xf "$BASE" -C "$WORK_DIR"

mkdir -p "$WORK_DIR/nocloud"
sed "s|__RTYLR_INSTALL_PASSWORD_HASH__|${RTYLR_INSTALL_PASSWORD_HASH}|g" \
  "$ROOT_DIR/config/autoinstall.yaml" > "$WORK_DIR/nocloud/user-data"
: > "$WORK_DIR/nocloud/meta-data"

if [[ -f "$WORK_DIR/boot/grub/grub.cfg" ]]; then
  perl -0pi -e 's/(\s+linux\s+[^\n]*?)(\s+---|\s+quiet)/$1 autoinstall ds=nocloud\\;s=\/cdrom\/nocloud\/ $2/g' "$WORK_DIR/boot/grub/grub.cfg"
else
  printf 'Ubuntu ISO does not contain boot/grub/grub.cfg\n' >&2
  exit 1
fi

printf 'Creating customized ISO...\n'
xorriso \
  -indev "$BASE" \
  -outdev "$OUTPUT" \
  -boot_image any replay \
  -map "$WORK_DIR/boot/grub/grub.cfg" /boot/grub/grub.cfg \
  -map "$WORK_DIR/nocloud" /nocloud \
  -map "$ROOT_DIR/config" /rtylr-config \
  -map "$ROOT_DIR/scripts/first-boot.sh" /scripts/first-boot.sh \
  -volid RTYLR_OS \
  -commit \
  -end

printf 'Built %s\n' "$OUTPUT"
