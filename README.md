# Rtylr OS

**The operating system for your business.**

Rtylr OS turns a standard AMD64 computer into a focused, branded workspace for
the application a business runs on. That application can be retail software,
scheduling, inventory, field-service tooling, an operations dashboard, or
something purpose-built. Point of sale is a supported workload, not the identity
of the operating system.

Rtylr layers a touch-first shell, first setup, diagnostics, recovery, kiosk
session, and provisioning on Ubuntu Server 26.04 LTS. The primary business app
runs without exposing a general-purpose Linux desktop to day-to-day users.

## Business experience

- the primary business app can open automatically after login
- a small always-available Rtylr control opens protected recovery
- touch targets are at least 52 px and every action is keyboard accessible
- an admin PIN protects configuration, restart, reboot, and shutdown actions
- device health covers network, storage, printing, and USB peripherals
- bounded crash recovery avoids infinite restart loops
- a missing or repeatedly failing app returns to a branded recovery view
- branding and the primary app can be provisioned without rebuilding the shell

`Ctrl+Alt+R` opens recovery and `Ctrl+Alt+A` requests a protected application
restart. Both require the admin PIN. The top-right Rtylr control provides the
same recovery path without a keyboard.

## Repository layout

- `src/rtylr-shell/` contains the Python/GTK business shell
- `config/shell.json` defines the default application and brand configuration
- `config/kiosk/` contains LightDM, Openbox, and session integration
- `config/polkit/` grants narrowly scoped power and NetworkManager actions
- `config/logrotate/` bounds appliance log retention
- `config/systemd/` contains first-boot and optional agent services
- `tests/` covers configuration, PIN handling, diagnostics, and supervision

Runtime state is stored in `/var/lib/rtylr`; logs are stored in
`/var/log/rtylr`. No password, admin PIN, token, or deployment secret is
committed to this repository.

## Development checks

```bash
make check
make test
```

These checks require Python 3 and Bash but do not require a graphical display.

## Reliability acceptance

Rtylr's business-continuity contract is maintained as 280 machine-validated
scenarios across 28 device domains and 10 failure or healthy conditions.

- [Catalog overview](docs/acceptance/README.md)
- [Generated scenario index](docs/acceptance/index.md)
- [Authoring guide](docs/acceptance/authoring.md)
- [Operator response taxonomy](docs/acceptance/operator-actions.md)

Validate the catalog and its coverage matrix directly with:

```bash
./scripts/check-scenarios.py
./scripts/check-scenario-coverage.py
```

## ISO build

On Ubuntu 24.04 or newer:

```bash
sudo apt-get update
sudo apt-get install -y curl gpg libarchive-tools perl python3-yaml rsync xorriso

make check
make check-build
make iso
make validate-iso
```

The build downloads and verifies the official Ubuntu Server 26.04 AMD64 image.
Its output name is derived from `VERSION`, currently
`dist/rtylr-os-0.3.0-amd64.iso`.

Public release images lock password authentication for the local `rtylr`
account while retaining the dedicated graphical autologin session. A deployment
that needs console password access can inject a SHA-512 crypt hash without
committing it:

```bash
RTYLR_INSTALL_PASSWORD_HASH='$6$...' make iso
```

The target device needs network access during installation so Subiquity can
install the graphical shell and common business-peripheral packages.

### Installer smoke test

`make lint` runs `shellcheck` and `yamllint`. `make test-vm` builds a test image
(`RTYLR_TEST_BUILD=1`: serial console, powers off after install), runs the
unattended install in QEMU/OVMF, boots the result, and checks that first-boot
provisioning ran and the graphical target was reached. It needs
`qemu-system-x86`, `qemu-utils`, and `ovmf`. Never ship a test image.

Base-image verification checks the GPG signature on Ubuntu's `SHA256SUMS`
against pinned signing keys before trusting any checksum. Override the pinned
fingerprints with `RTYLR_UBUNTU_SIGNING_FPRS` if Ubuntu rotates the key. The
autoinstall package list is generated from `config/packages.list`.

## Automated ISO releases

GitHub Actions builds and validates the complete ISO for pull requests and every
push to `main`. When `VERSION` has not previously been released, a successful
`main` build creates the matching `v<version>` tag and GitHub Release.

GitHub requires each release asset to be smaller than 2 GiB, while the complete
ISO is currently about 2.9 GB. The workflow therefore publishes lossless
`part-01`, `part-02`, and checksum assets. Reconstruct and verify the original
ISO after downloading all parts:

```bash
cat rtylr-os-0.3.0-amd64.iso.part-* > rtylr-os-0.3.0-amd64.iso
sha256sum --check rtylr-os-0.3.0-amd64.iso.sha256
```

Windows releases also include `REASSEMBLE.ps1`, which joins the parts and fails
if the reconstructed ISO does not match its SHA-256 checksum.

To publish the next release, update `VERSION` in the same change. Re-running a
workflow for an existing version is safe: assets are replaced only when the tag
points to the same commit, and a reused version pointing elsewhere fails closed.

## Primary application configuration

The new-install default is `/opt/rtylr/apps/business-app`. Choose another
executable during first setup, edit it later in protected Rtylr settings, or
provision `/var/lib/rtylr/shell.json` directly:

```json
{
  "application": {
    "name": "Business workspace",
    "command": ["/opt/my-business/app", "--kiosk"]
  }
}
```

The command is always executed as an argument array and is never passed through
a shell. Rtylr OS 0.3 automatically migrates the legacy 0.2 `pos` configuration
key when loading an existing installation.
