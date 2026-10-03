#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BASE_NAME="ubuntu-26.04-live-server-amd64.iso"
BASE="${ROOT_DIR}/cache/${BASE_NAME}"
SUMS_URL="https://releases.ubuntu.com/26.04/SHA256SUMS"
SUMS="${ROOT_DIR}/cache/SHA256SUMS"
KEYSERVER="${RTYLR_KEYSERVER:-hkps://keyserver.ubuntu.com}"
# Ubuntu CD Image Automatic Signing Keys. Override (space separated) if
# Ubuntu rotates the key used to sign the 26.04 checksums.
SIGNING_FPRS="${RTYLR_UBUNTU_SIGNING_FPRS:-843938DF228D22F7B3742BC0D94AA3F0EFE21092 C5986B4F1257FFA86632CBA746181433FBB75451}"

die() { printf '%s\n' "$*" >&2; exit 1; }

[[ -f "$BASE" ]] || die 'Base ISO missing; run make download first.'

GNUPGHOME="$(mktemp -d)"
export GNUPGHOME
trap 'rm -rf "$GNUPGHOME"' EXIT

curl --fail --location --silent --show-error --output "${SUMS}.part" "$SUMS_URL"
curl --fail --location --silent --show-error --output "${SUMS}.gpg.part" "${SUMS_URL}.gpg"

# shellcheck disable=SC2086
gpg --batch --quiet --keyserver "$KEYSERVER" --recv-keys $SIGNING_FPRS ||
  die 'Could not fetch Ubuntu signing keys.'

status="$(gpg --batch --status-fd 1 --verify "${SUMS}.gpg.part" "${SUMS}.part" 2>/dev/null)" ||
  die 'GPG signature verification of SHA256SUMS FAILED.'
grep -q '^\[GNUPG:\] GOODSIG ' <<<"$status" || die 'SHA256SUMS has no good signature.'
primary="$(awk '$2 == "VALIDSIG" { print $NF }' <<<"$status")"
[[ -n "$primary" && " $SIGNING_FPRS " == *" $primary "* ]] ||
  die "SHA256SUMS signed by unexpected key: ${primary:-none}"

mv "${SUMS}.part" "$SUMS"
mv "${SUMS}.gpg.part" "${SUMS}.gpg"

(cd "$(dirname "$BASE")" && grep -E "^[[:xdigit:]]{64}[[:space:]]+\\*?${BASE_NAME}$" "$SUMS" | sha256sum --check --strict -)
printf 'Verified %s (checksums signed by %s)\n' "$BASE" "$primary"
