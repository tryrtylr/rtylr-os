# Rtylr OS

Rtylr OS is the reproducible build recipe for Rtylr POS terminals. It layers
the Rtylr appliance configuration, services, kiosk session, provisioning, and
branding on top of Ubuntu Server 26.04 LTS AMD64.

The repository contains source and build scripts, not generated operating
system images. ISO files are written to `dist/` and are ignored by Git.

## Build

On Ubuntu 26.04 (recommended build host):

```bash
sudo apt-get update
sudo apt-get install -y \
  xorriso \
  curl \
  gpg \
  perl

make check
RTYLR_INSTALL_PASSWORD_HASH='...' make iso
```

`make iso` downloads the official Ubuntu Server 26.04 AMD64 base image into
`cache/`, verifies the GPG signature on `SHA256SUMS` (pinned Ubuntu signing
keys) and then the image checksum, and produces a customized installer
image in `dist/`.

The password hash must be supplied at build time; generate a deployment-
specific SHA-512 crypt hash and never commit it to this repository.

## Test

`make lint` runs `shellcheck` and `yamllint`. `make test-vm` builds a test
image (`RTYLR_TEST_BUILD=1`: serial console, powers off after install), runs
the unattended install in QEMU/OVMF, boots the result and checks that
first-boot provisioning ran. It needs `qemu-system-x86`, `qemu-utils` and
`ovmf`. Never ship a test image.

The package list lives only in `config/packages.list`; the build injects it
into the autoinstall config. The version lives in `VERSION`.

## Current scope

The initial build establishes:

- verified Ubuntu 26.04 AMD64 base-image handling
- declarative autoinstall configuration
- minimal POS package and graphics dependency declarations
- systemd service boundaries for the agent (own user, sandboxed) and first boot
- kiosk session (`rtylr-kiosk`) that supervises the POS application
- explicit build-host dependency checks

The first image does not yet contain a production POS binary or secrets.
Production provisioning, signed Rtylr packages, remote support, update
rollback, and final installer branding remain subsequent milestones.
