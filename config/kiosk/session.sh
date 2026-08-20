#!/usr/bin/env bash
set -euo pipefail

export XDG_CURRENT_DESKTOP=Rtylr
export XDG_SESSION_TYPE=x11

openbox-session &
exec /opt/rtylr/pos/rtylr-pos
