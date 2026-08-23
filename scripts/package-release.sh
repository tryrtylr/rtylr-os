#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="$(tr -d '[:space:]' < "${ROOT_DIR}/VERSION")"
ISO_NAME="rtylr-os-${VERSION}-amd64.iso"
ISO="${1:-${ROOT_DIR}/dist/${ISO_NAME}}"
RELEASE_DIR="${RTYLR_RELEASE_DIR:-${ROOT_DIR}/dist/release}"
PART_SIZE="${RTYLR_RELEASE_PART_SIZE:-1900M}"
ASSET_LIMIT="${RTYLR_RELEASE_ASSET_LIMIT:-$((2 * 1024 * 1024 * 1024))}"

[[ -f "$ISO" ]] || { printf 'ISO not found: %s\n' "$ISO" >&2; exit 1; }
[[ -f "${ISO}.sha256" ]] || { printf 'ISO checksum not found: %s.sha256\n' "$ISO" >&2; exit 1; }
(cd "$(dirname "$ISO")" && sha256sum --check "$(basename "$ISO").sha256")

mkdir -p "$RELEASE_DIR"
find "$RELEASE_DIR" -mindepth 1 -maxdepth 1 -type f -delete

split \
  --bytes="$PART_SIZE" \
  --numeric-suffixes=1 \
  --suffix-length=2 \
  "$ISO" \
  "${RELEASE_DIR}/${ISO_NAME}.part-"

part_count=0
for part in "${RELEASE_DIR}/${ISO_NAME}.part-"*; do
  [[ -f "$part" ]] || { printf 'No release parts were created.\n' >&2; exit 1; }
  size="$(stat --format='%s' "$part")"
  ((size < ASSET_LIMIT)) || {
    printf 'Release part exceeds GitHub limit: %s (%s bytes)\n' "$part" "$size" >&2
    exit 1
  }
  ((part_count += 1))
done
((part_count >= 2)) || {
  printf 'Expected the ISO to require at least two release assets.\n' >&2
  exit 1
}

cp "${ISO}.sha256" "$RELEASE_DIR/"
(
  cd "$RELEASE_DIR"
  sha256sum "${ISO_NAME}.part-"* > "${ISO_NAME}.parts.sha256"
)

cat > "${RELEASE_DIR}/REASSEMBLE.txt" <<EOF
Rtylr OS ${VERSION}

Download every ${ISO_NAME}.part-* file and ${ISO_NAME}.sha256 into one folder.

Linux:
  cat ${ISO_NAME}.part-* > ${ISO_NAME}
  sha256sum --check ${ISO_NAME}.sha256

macOS:
  cat ${ISO_NAME}.part-* > ${ISO_NAME}
  expected=\$(awk '{print \$1}' ${ISO_NAME}.sha256)
  test "\$(shasum -a 256 ${ISO_NAME} | awk '{print \$1}')" = "\$expected"

The checksum must pass before writing the ISO to installation media.
EOF

cat > "${RELEASE_DIR}/REASSEMBLE.ps1" <<EOF
\$ErrorActionPreference = "Stop"
\$IsoName = "${ISO_NAME}"
\$Parts = Get-ChildItem -File "\${IsoName}.part-*" | Sort-Object Name
if (\$Parts.Count -lt 2) { throw "Download every \${IsoName}.part-* asset first." }

\$Destination = [System.IO.File]::Open(\$IsoName, [System.IO.FileMode]::Create)
try {
    foreach (\$Part in \$Parts) {
        \$Source = [System.IO.File]::OpenRead(\$Part.FullName)
        try { \$Source.CopyTo(\$Destination) } finally { \$Source.Dispose() }
    }
} finally {
    \$Destination.Dispose()
}

\$Expected = ((Get-Content "\${IsoName}.sha256" -Raw) -split '\\s+')[0].ToLowerInvariant()
\$Actual = (Get-FileHash -Algorithm SHA256 \$IsoName).Hash.ToLowerInvariant()
if (\$Actual -ne \$Expected) { throw "ISO checksum failed." }
Write-Host "ISO checksum passed: \$IsoName"
EOF

full_sha="$(awk '{print $1}' "${ISO}.sha256")"
cat > "${RELEASE_DIR}/RELEASE_NOTES.md" <<EOF
Rtylr OS ${VERSION} is a focused operating system for the application your business runs on.

The complete AMD64 ISO is published in ${part_count} lossless parts because GitHub limits each release asset to less than 2 GiB. Download every \`${ISO_NAME}.part-*\` asset, \`${ISO_NAME}.sha256\`, and the reconstruction instructions. Windows users can run \`REASSEMBLE.ps1\`.

\`\`\`bash
cat ${ISO_NAME}.part-* > ${ISO_NAME}
sha256sum --check ${ISO_NAME}.sha256
\`\`\`

Full ISO SHA-256: \`${full_sha}\`
EOF

printf 'Prepared %s release parts in %s\n' "$part_count" "$RELEASE_DIR"
