#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BASE_VERSION="26.04"
BASE_NAME="ubuntu-${BASE_VERSION}-live-server-amd64.iso"
BASE_URL="https://releases.ubuntu.com/${BASE_VERSION}/${BASE_NAME}"
CACHE_DIR="${ROOT_DIR}/cache"
TARGET="${CACHE_DIR}/${BASE_NAME}"

mkdir -p "$CACHE_DIR"
if [[ -f "$TARGET" ]]; then
  printf 'Base ISO already present: %s\n' "$TARGET"
  exit 0
fi

printf 'Downloading %s\n' "$BASE_URL"
curl --fail --location --progress-bar --output "$TARGET.part" "$BASE_URL"
mv "$TARGET.part" "$TARGET"
printf 'Downloaded %s\n' "$TARGET"
