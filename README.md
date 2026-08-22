# Rtylr OS

Rtylr OS turns a standard AMD64 terminal into a focused appliance for running
one configured point-of-sale application. It layers a branded, touch-first
shell, setup, diagnostics, recovery, kiosk session, and provisioning on top of
Ubuntu Server 26.04 LTS.

The shell is POS-vendor neutral. A merchant can install any graphical POS
application and configure its executable without exposing a general-purpose
Linux desktop to cashiers.

## Operator experience

- the configured POS starts automatically after login
- a small always-available Rtylr control opens recovery without leaving the POS
- touch targets are at least 52 px and every action is keyboard accessible
- an admin PIN protects configuration, restart, reboot, and shutdown actions
- the admin PIN can be rotated from the protected System page
- actionable health cards cover network, storage, printing, USB, and the POS
- crashed POS processes use bounded restart backoff instead of a restart loop
- missing or repeatedly failing POS software returns to a branded recovery view

`Ctrl+Alt+R` opens recovery and `Ctrl+Alt+P` requests a protected POS restart.
Both require the admin PIN. The touch control in the top-right corner provides
the same recovery path without a keyboard.

## Repository layout

- `src/rtylr-shell/` contains the Python/GTK appliance shell
- `config/shell.json` defines the default POS and brand configuration
- `config/kiosk/` contains LightDM, Openbox, and session integration
- `config/polkit/` grants the active local appliance user narrowly scoped power
  and NetworkManager actions
- `config/logrotate/` bounds appliance log retention
- `config/systemd/` contains first-boot and optional agent services
- `tests/` covers configuration, PIN handling, diagnostics, and supervision

Runtime state is stored in `/var/lib/rtylr`; logs are stored in
`/var/log/rtylr`. No password, admin PIN, token, or other deployment secret is
committed to this repository.

## Development checks

The source checks require Python 3 and Bash, but do not require a graphical
display:

```bash
make check
make test
```

## ISO build

On Ubuntu 26.04 (recommended build host):

```bash
sudo apt-get update
sudo apt-get install -y \
  xorriso \
  grub-pc-bin \
  grub-efi-amd64-bin \
  mtools \
  squashfs-tools \
  libarchive-tools \
  rsync \
  curl \
  gpg

make check
make check-build
RTYLR_INSTALL_PASSWORD_HASH='...' make iso
make validate-iso
```

The target terminal needs network access during installation so Subiquity can
install the graphical shell and POS peripheral packages listed in the image.

`make iso` downloads and verifies the official Ubuntu Server 26.04 AMD64 image,
then writes `dist/rtylr-os-0.2.0-amd64.iso` and its SHA256 file. Generate a
deployment-specific SHA-512 crypt password hash; never commit a reusable hash.

## Default POS configuration

The installed default is `/opt/rtylr/pos/rtylr-pos`. Edit it in the protected
Rtylr settings screen or provision `/var/lib/rtylr/shell.json` directly:

```json
{
  "pos": {
    "name": "Store POS",
    "command": ["/opt/store-pos/store-pos", "--kiosk"]
  }
}
```

The command is always executed as an argument array; it is never passed through
a shell.
