#!/usr/bin/env bash
set -euo pipefail

STATE_DIR=/var/lib/rtylr
mkdir -p "$STATE_DIR"

# Provisioning is deliberately a separate milestone. This marker prevents a
# partially implemented first boot from repeatedly mutating a terminal.
touch "$STATE_DIR/.firstboot-complete"
