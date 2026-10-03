#!/usr/bin/env bash
set -euo pipefail

required=(curl sha256sum md5sum xorriso bsdtar rsync gpg perl paste split stat)
missing=()
for command_name in "${required[@]}"; do
  command -v "$command_name" >/dev/null 2>&1 || missing+=("$command_name")
done

if ((${#missing[@]})); then
  printf 'Missing build dependencies: %s\n' "${missing[*]}" >&2
  printf 'Install the Ubuntu build dependencies listed in README.md.\n' >&2
  exit 1
fi

if [[ "$(uname -m)" != "x86_64" && "${RTYLR_ALLOW_CROSS_BUILD:-}" != "1" ]]; then
  printf 'Build host is %s; target is AMD64. Set RTYLR_ALLOW_CROSS_BUILD=1 to acknowledge cross-building.\n' "$(uname -m)" >&2
  exit 1
fi

printf 'Build dependencies and AMD64 target check passed.\n'
