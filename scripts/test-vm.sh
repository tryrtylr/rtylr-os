#!/usr/bin/env bash
# shellcheck disable=SC2054 # commas are QEMU option separators, not array separators
# End-to-end smoke test: unattended install in QEMU/UEFI, then boot the result
# and check that first-boot provisioning ran and the graphical target was reached.
#
# Requires an ISO built with:  RTYLR_TEST_BUILD=1 RTYLR_INSTALL_PASSWORD_HASH=... make iso
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="$(tr -d '[:space:]' < "$ROOT_DIR/VERSION")"
ISO="${1:-${ROOT_DIR}/dist/rtylr-os-${VERSION}-amd64.iso}"
VM_DIR="${ROOT_DIR}/work/vm"
INSTALL_TIMEOUT="${RTYLR_INSTALL_TIMEOUT:-2400}"
BOOT_TIMEOUT="${RTYLR_BOOT_TIMEOUT:-300}"

die() { printf '%s\n' "$*" >&2; exit 1; }
first_existing() { for p in "$@"; do [[ -f "$p" ]] && { printf '%s' "$p"; return 0; }; done; return 1; }

command -v qemu-system-x86_64 >/dev/null || die 'qemu-system-x86_64 is required.'
command -v qemu-img >/dev/null || die 'qemu-img is required.'
[[ -f "$ISO" ]] || die "ISO not found: $ISO (build with RTYLR_TEST_BUILD=1 make iso)"

OVMF_CODE="$(first_existing /usr/share/OVMF/OVMF_CODE_4M.fd /usr/share/OVMF/OVMF_CODE.fd /usr/share/edk2/ovmf/OVMF_CODE.fd)" ||
  die 'OVMF firmware not found (apt install ovmf).'
OVMF_VARS_TEMPLATE="$(first_existing /usr/share/OVMF/OVMF_VARS_4M.fd /usr/share/OVMF/OVMF_VARS.fd /usr/share/edk2/ovmf/OVMF_VARS.fd)" ||
  die 'OVMF vars template not found (apt install ovmf).'

accel=(-machine q35 -cpu max)
if [[ -w /dev/kvm ]]; then accel=(-machine q35,accel=kvm -cpu host); fi

rm -rf "$VM_DIR"
mkdir -p "$VM_DIR"
qemu-img create -q -f qcow2 "$VM_DIR/disk.qcow2" 16G
cp "$OVMF_VARS_TEMPLATE" "$VM_DIR/vars.fd"

qemu_common=(
  "${accel[@]}" -smp 2 -m 4096
  -display none -serial "file:$VM_DIR/serial.log"
  -drive "if=pflash,format=raw,readonly=on,file=$OVMF_CODE"
  -drive "if=pflash,format=raw,file=$VM_DIR/vars.fd"
  -drive "file=$VM_DIR/disk.qcow2,if=virtio,format=qcow2"
  -nic user,model=virtio-net-pci
)

printf '== Phase 1: unattended install (timeout %ss)\n' "$INSTALL_TIMEOUT"
set +e
timeout "$INSTALL_TIMEOUT" qemu-system-x86_64 "${qemu_common[@]}" \
  -drive "file=$ISO,media=cdrom,readonly=on" -boot d
rc=$?
set -e
[[ $rc -ne 124 ]] || { tail -n 40 "$VM_DIR/serial.log" || true; die 'Install timed out.'; }
[[ $rc -eq 0 ]] || die "QEMU exited with status $rc during install."
mv "$VM_DIR/serial.log" "$VM_DIR/install.log"

printf '== Phase 2: boot installed system (timeout %ss)\n' "$BOOT_TIMEOUT"
qemu-system-x86_64 "${qemu_common[@]}" &
qemu_pid=$!
trap 'kill "$qemu_pid" 2>/dev/null || true' EXIT

deadline=$((SECONDS + BOOT_TIMEOUT))
want=('Finished Rtylr first-boot provisioning' 'Reached target .*Graphical Interface')
while ((SECONDS < deadline)); do
  ok=1
  for pattern in "${want[@]}"; do
    grep -qE "$pattern" "$VM_DIR/serial.log" 2>/dev/null || ok=0
  done
  if ((ok)); then printf 'PASS: installed system booted and provisioned.\n'; exit 0; fi
  kill -0 "$qemu_pid" 2>/dev/null || break
  sleep 5
done

tail -n 60 "$VM_DIR/serial.log" || true
die 'FAIL: expected boot markers not seen on serial console.'
