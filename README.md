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
  grub-pc-bin \
  grub-efi-amd64-bin \
  mtools \
  squashfs-tools \
  rsync \
  curl \
  gpg

make check
RTYLR_INSTALL_PASSWORD_HASH='...' make iso
```

`make iso` downloads the official Ubuntu Server 26.04 AMD64 base image into
`cache/`, verifies its SHA256 checksum, and produces a customized installer
image in `dist/`.

The password hash must be supplied at build time; generate a deployment-
specific SHA-512 crypt hash and never commit it to this repository.

## Current scope

The initial build establishes:

- verified Ubuntu 26.04 AMD64 base-image handling
- declarative autoinstall configuration
- minimal POS package and graphics dependency declarations
- systemd service boundaries for POS, agent, and first boot
- restricted kiosk session scaffolding
- explicit build-host dependency checks

The first image does not yet contain a production POS binary or secrets.
Production provisioning, signed Rtylr packages, remote support, update
rollback, and final installer branding remain subsequent milestones.
