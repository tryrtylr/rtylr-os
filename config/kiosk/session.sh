#!/usr/bin/env bash
set -euo pipefail

export XDG_CURRENT_DESKTOP=Rtylr
export XDG_SESSION_TYPE=x11

xset s off -dpms s noblank >/dev/null 2>&1 || true
openbox-session &
exec /usr/local/bin/rtylr-shell
