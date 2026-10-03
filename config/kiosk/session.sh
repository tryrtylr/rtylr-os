#!/usr/bin/env bash
# Kiosk session launched by LightDM (see rtylr-kiosk.desktop). This is the only
# thing that starts the POS application; it supervises it and restarts it.
set -uo pipefail

export XDG_CURRENT_DESKTOP=Rtylr
export XDG_SESSION_TYPE=x11

POS=/opt/rtylr/pos/rtylr-pos

openbox-session &

while true; do
  if [[ -x "$POS" ]]; then
    "$POS" || logger -t rtylr-session "rtylr-pos exited with status $?; restarting"
  else
    logger -t rtylr-session "$POS not installed; waiting"
  fi
  sleep 3
done
