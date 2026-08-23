#!/usr/bin/env bash
set -euo pipefail

STATE_DIR=/var/lib/rtylr
LOG_DIR=/var/log/rtylr
DEFAULT_CONFIG=/opt/rtylr/config/shell.json
RUNTIME_CONFIG=${STATE_DIR}/shell.json

install -d -m 0750 -o rtylr -g rtylr "$STATE_DIR" "$LOG_DIR"
install -d -m 0755 /opt/rtylr/apps /opt/rtylr/agent

if [[ ! -f "$RUNTIME_CONFIG" && -f "$DEFAULT_CONFIG" ]]; then
  install -m 0640 -o rtylr -g rtylr "$DEFAULT_CONFIG" "$RUNTIME_CONFIG"
fi

if [[ ! -f "$STATE_DIR/device-id" ]]; then
  sha256sum /etc/machine-id | cut -c1-16 > "$STATE_DIR/device-id"
fi

chown -R rtylr:rtylr "$STATE_DIR" "$LOG_DIR"
chmod 0750 "$STATE_DIR" "$LOG_DIR"
touch "$STATE_DIR/.firstboot-complete"
chown rtylr:rtylr "$STATE_DIR/.firstboot-complete"
