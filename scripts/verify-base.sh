#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BASE_NAME="ubuntu-26.04-live-server-amd64.iso"
BASE="${ROOT_DIR}/cache/${BASE_NAME}"
SUMS_URL="https://releases.ubuntu.com/26.04/SHA256SUMS"
SUMS="${ROOT_DIR}/cache/SHA256SUMS"

[[ -f "$BASE" ]] || { printf 'Base ISO missing; run make download first.\n' >&2; exit 1; }
curl --fail --location --silent --show-error --output "${SUMS}.part" "$SUMS_URL"
mv "${SUMS}.part" "$SUMS"
(cd "$(dirname "$BASE")" && grep -E "^[[:xdigit:]]{64}[[:space:]]+\\*?${BASE_NAME}$" "$SUMS" | sha256sum --check --strict -)
printf 'Verified %s\n' "$BASE"
