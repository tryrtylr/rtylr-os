#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPYCACHEPREFIX="$ROOT_DIR/tmp/pycache"

while IFS= read -r script; do
  bash -n "$script"
done < <(find "$ROOT_DIR/scripts" "$ROOT_DIR/config/kiosk" -type f -name '*.sh')

for executable in \
  "$ROOT_DIR/scripts/build.sh" \
  "$ROOT_DIR/scripts/first-boot.sh" \
  "$ROOT_DIR/scripts/package-release.sh" \
  "$ROOT_DIR/scripts/validate-iso.sh" \
  "$ROOT_DIR/config/kiosk/session.sh" \
  "$ROOT_DIR/src/rtylr-shell/rtylr-shell"; do
  [[ -x "$executable" ]] || { printf 'Expected executable: %s\n' "$executable" >&2; exit 1; }
done

python3 -m py_compile "$ROOT_DIR/src/rtylr-shell/rtylr-shell"
python3 -m compileall -q "$ROOT_DIR/src/rtylr-shell/rtylr_shell"
python3 -m json.tool "$ROOT_DIR/config/shell.json" >/dev/null
python3 "$ROOT_DIR/scripts/check-gtk-css.py" "$ROOT_DIR/src/rtylr-shell/rtylr_shell/style.css"
python3 - "$ROOT_DIR" <<'PY'
from configparser import ConfigParser
from pathlib import Path
import sys
from xml.etree import ElementTree

root = Path(sys.argv[1])
version = (root / "VERSION").read_text(encoding="utf-8").strip()
assert version.count(".") >= 2 and all(version.split(".")), "VERSION must be populated"
package_init = (root / "src/rtylr-shell/rtylr_shell/__init__.py").read_text(encoding="utf-8")
assert f'__version__ = "{version}"' in package_init

ElementTree.parse(root / "config/kiosk/openbox.xml")
openbox_text = (root / "config/kiosk/openbox.xml").read_text(encoding="utf-8")
assert 'class="*" type="normal"' in openbox_text
assert "--restart-app" in openbox_text

shell_config = __import__("json").loads(
    (root / "config/shell.json").read_text(encoding="utf-8")
)
assert "application" in shell_config
assert "pos" not in shell_config

desktop = ConfigParser(interpolation=None)
desktop.read(root / "config/kiosk/rtylr.desktop")
assert desktop.get("Desktop Entry", "Exec") == "/usr/local/lib/rtylr/session.sh"

lightdm = ConfigParser(interpolation=None)
lightdm.read(root / "config/kiosk/autologin.conf")
assert lightdm.get("Seat:*", "user-session") == "rtylr"

try:
    import yaml
except ImportError:
    print("PyYAML unavailable; skipping autoinstall schema parse.", file=sys.stderr)
else:
    document = yaml.safe_load((root / "config/autoinstall.yaml").read_text(encoding="utf-8"))
    autoinstall = document["autoinstall"]
    assert autoinstall["version"] == 1
    late_commands = "\n".join(autoinstall["late-commands"])
    for source in (
        "/cdrom/rtylr-shell/rtylr-shell",
        "/cdrom/rtylr-config/kiosk/session.sh",
        "/cdrom/rtylr-config/kiosk/rtylr.desktop",
        "/cdrom/rtylr-config/logrotate/rtylr",
        "/cdrom/rtylr-version",
        "/cdrom/scripts/first-boot.sh",
    ):
        assert source in late_commands, f"Installer does not copy {source}"
PY
PYTHONPATH="$ROOT_DIR/src/rtylr-shell" python3 -m unittest discover -s "$ROOT_DIR/tests" -v

grep -Fq 'run: make iso' "$ROOT_DIR/.github/workflows/check.yml"
grep -Fq 'run: make package-release' "$ROOT_DIR/.github/workflows/check.yml"
grep -Fq 'gh release create' "$ROOT_DIR/.github/workflows/check.yml"

if ! grep -q '__RTYLR_INSTALL_PASSWORD_HASH__' "$ROOT_DIR/config/autoinstall.yaml"; then
  printf 'Autoinstall password placeholder is missing.\n' >&2
  exit 1
fi

printf 'Source, configuration, and unit checks passed.\n'
