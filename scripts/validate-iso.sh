#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="$(tr -d '[:space:]' < "${ROOT_DIR}/VERSION")"
ISO="$(realpath "${1:-${ROOT_DIR}/dist/rtylr-os-${VERSION}-amd64.iso}")"

[[ -f "$ISO" ]] || { printf 'ISO not found: %s\n' "$ISO" >&2; exit 1; }
for command_name in xorriso bsdtar sha256sum python3; do
  command -v "$command_name" >/dev/null 2>&1 || {
    printf 'Missing ISO validation dependency: %s\n' "$command_name" >&2
    exit 1
  }
done

ISO_DIR="$(dirname "$ISO")"
ISO_NAME="$(basename "$ISO")"
if [[ -f "${ISO}.sha256" ]]; then
  (cd "$ISO_DIR" && sha256sum --check "${ISO_NAME}.sha256")
fi

mapfile -t entries < <(bsdtar -tf "$ISO")
declare -A entry_set=()
for entry in "${entries[@]}"; do
  entry_set["$entry"]=1
  if [[ "$entry" =~ (^|/)__pycache__(/|$)|\.py[co]$ ]]; then
    printf 'Development bytecode was included in the ISO: %s\n' "$entry" >&2
    exit 1
  fi
done
for required in \
  boot/grub/grub.cfg \
  nocloud/user-data \
  nocloud/meta-data \
  rtylr-version \
  rtylr-shell/rtylr-shell \
  rtylr-shell/rtylr_shell/app.py \
  rtylr-config/kiosk/rtylr.desktop \
  rtylr-config/logrotate/rtylr; do
  [[ -n "${entry_set[$required]+present}" ]] || {
    printf 'ISO payload missing: %s\n' "$required" >&2
    exit 1
  }
done

TEMP_DIR="$(mktemp -d /tmp/rtylr-iso-validation.XXXXXX)"
trap 'rm -rf -- "$TEMP_DIR"' EXIT
xorriso -osirrox on -indev "$ISO" \
  -extract /boot/grub/grub.cfg "$TEMP_DIR/grub.cfg" \
  -extract /nocloud/user-data "$TEMP_DIR/user-data" \
  -extract /rtylr-version "$TEMP_DIR/rtylr-version" \
  >/dev/null 2>&1

grep -Fq 'autoinstall ds=nocloud\;s=/cdrom/nocloud/' "$TEMP_DIR/grub.cfg"
[[ "$(tr -d '[:space:]' < "$TEMP_DIR/rtylr-version")" == "$VERSION" ]]
if grep -q '__RTYLR_INSTALL_PASSWORD_HASH__' "$TEMP_DIR/user-data"; then
  printf 'Installer password placeholder remains in ISO.\n' >&2
  exit 1
fi
python3 - "$TEMP_DIR/user-data" <<'PY'
from pathlib import Path
import sys

try:
    import yaml
except ImportError:
    raise SystemExit("PyYAML is required to validate embedded autoinstall data")

document = yaml.safe_load(Path(sys.argv[1]).read_text(encoding="utf-8"))
assert document["autoinstall"]["version"] == 1
password = document["autoinstall"]["identity"]["password"]
assert isinstance(password, str)
assert password == "!" or password.startswith(("$5$", "$6$", "$y$"))
PY

boot_report="$(xorriso -indev "$ISO" -report_el_torito plain 2>&1)"
grep -Eq 'El Torito boot img.*BIOS.*y' <<<"$boot_report"
grep -Eq 'El Torito boot img.*UEFI.*y' <<<"$boot_report"
grep -Fq "Volume id    : 'RTYLROS'" <<<"$boot_report"

printf 'ISO payload, autoinstall, checksum, BIOS boot, and UEFI boot: OK\n'
