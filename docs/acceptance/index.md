# Acceptance scenario index

This generated index covers 280 validated scenarios across 28 business-device domains.

Legend: **admin** requires the protected admin PIN; **offline-safe** means the scenario permits an explicitly verified local workflow.

## Admin Pin

- [Admin access is degraded](scenarios/admin-pin-degraded.json) — warning, status:warning, offline-safe
- [Admin access has a failed dependency](scenarios/admin-pin-dependency-failed.json) — error, status:error, admin
- [Admin access meets its healthy baseline](scenarios/admin-pin-healthy-baseline.json) — info, status:ok, offline-safe
- [Admin access is intermittent](scenarios/admin-pin-intermittent.json) — warning, status:warning, offline-safe
- [Admin access is misconfigured](scenarios/admin-pin-misconfigured.json) — error, status:error, admin
- [Admin access did not recover](scenarios/admin-pin-recovery-failed.json) — critical, status:error, admin
- [Admin access has exhausted a resource](scenarios/admin-pin-resource-exhausted.json) — critical, status:error, admin
- [Admin access times out](scenarios/admin-pin-timeout.json) — warning, status:warning, offline-safe
- [Admin access is unavailable](scenarios/admin-pin-unavailable.json) — critical, status:error, admin
- [Admin access is in an unsafe state](scenarios/admin-pin-unsafe-state.json) — critical, status:error, admin

## Agent

- [Management agent is degraded](scenarios/agent-degraded.json) — warning, status:warning
- [Management agent has a failed dependency](scenarios/agent-dependency-failed.json) — error, status:error, admin
- [Management agent meets its healthy baseline](scenarios/agent-healthy-baseline.json) — info, status:ok
- [Management agent is intermittent](scenarios/agent-intermittent.json) — warning, status:warning
- [Management agent is misconfigured](scenarios/agent-misconfigured.json) — error, status:error, admin
- [Management agent did not recover](scenarios/agent-recovery-failed.json) — critical, status:error, admin
- [Management agent has exhausted a resource](scenarios/agent-resource-exhausted.json) — critical, status:error, admin
- [Management agent times out](scenarios/agent-timeout.json) — warning, status:warning
- [Management agent is unavailable](scenarios/agent-unavailable.json) — critical, status:error, admin
- [Management agent is in an unsafe state](scenarios/agent-unsafe-state.json) — critical, status:error, admin

## Application

- [Primary business app is degraded](scenarios/application-degraded.json) — warning, status:warning
- [Primary business app has a failed dependency](scenarios/application-dependency-failed.json) — error, status:error, admin
- [Primary business app meets its healthy baseline](scenarios/application-healthy-baseline.json) — info, status:ok
- [Primary business app is intermittent](scenarios/application-intermittent.json) — warning, status:warning
- [Primary business app is misconfigured](scenarios/application-misconfigured.json) — error, status:error, admin
- [Primary business app did not recover](scenarios/application-recovery-failed.json) — critical, status:error, admin
- [Primary business app has exhausted a resource](scenarios/application-resource-exhausted.json) — critical, status:error, admin
- [Primary business app times out](scenarios/application-timeout.json) — warning, status:warning
- [Primary business app is unavailable](scenarios/application-unavailable.json) — critical, status:error, admin
- [Primary business app is in an unsafe state](scenarios/application-unsafe-state.json) — critical, status:error, admin

## Audio

- [Audio output is degraded](scenarios/audio-degraded.json) — warning, status:warning, offline-safe
- [Audio output has a failed dependency](scenarios/audio-dependency-failed.json) — error, status:error, admin
- [Audio output meets its healthy baseline](scenarios/audio-healthy-baseline.json) — info, status:ok, offline-safe
- [Audio output is intermittent](scenarios/audio-intermittent.json) — warning, status:warning, offline-safe
- [Audio output is misconfigured](scenarios/audio-misconfigured.json) — error, status:error, admin
- [Audio output did not recover](scenarios/audio-recovery-failed.json) — critical, status:error, admin
- [Audio output has exhausted a resource](scenarios/audio-resource-exhausted.json) — critical, status:error, admin
- [Audio output times out](scenarios/audio-timeout.json) — warning, status:warning, offline-safe
- [Audio output is unavailable](scenarios/audio-unavailable.json) — critical, status:error, admin
- [Audio output is in an unsafe state](scenarios/audio-unsafe-state.json) — critical, status:error, admin

## Bluetooth

- [Bluetooth peripherals is degraded](scenarios/bluetooth-degraded.json) — warning, status:warning, offline-safe
- [Bluetooth peripherals has a failed dependency](scenarios/bluetooth-dependency-failed.json) — error, status:error, admin
- [Bluetooth peripherals meets its healthy baseline](scenarios/bluetooth-healthy-baseline.json) — info, status:ok, offline-safe
- [Bluetooth peripherals is intermittent](scenarios/bluetooth-intermittent.json) — warning, status:warning, offline-safe
- [Bluetooth peripherals is misconfigured](scenarios/bluetooth-misconfigured.json) — error, status:error, admin
- [Bluetooth peripherals did not recover](scenarios/bluetooth-recovery-failed.json) — critical, status:error, admin
- [Bluetooth peripherals has exhausted a resource](scenarios/bluetooth-resource-exhausted.json) — critical, status:error, admin
- [Bluetooth peripherals times out](scenarios/bluetooth-timeout.json) — warning, status:warning, offline-safe
- [Bluetooth peripherals is unavailable](scenarios/bluetooth-unavailable.json) — critical, status:error, admin
- [Bluetooth peripherals is in an unsafe state](scenarios/bluetooth-unsafe-state.json) — critical, status:error, admin

## Boot

- [Boot process is degraded](scenarios/boot-degraded.json) — warning, status:warning, offline-safe
- [Boot process has a failed dependency](scenarios/boot-dependency-failed.json) — error, status:error, admin
- [Boot process meets its healthy baseline](scenarios/boot-healthy-baseline.json) — info, status:ok, offline-safe
- [Boot process is intermittent](scenarios/boot-intermittent.json) — warning, status:warning, offline-safe
- [Boot process is misconfigured](scenarios/boot-misconfigured.json) — error, status:error, admin
- [Boot process did not recover](scenarios/boot-recovery-failed.json) — critical, status:error, admin
- [Boot process has exhausted a resource](scenarios/boot-resource-exhausted.json) — critical, status:error, admin
- [Boot process times out](scenarios/boot-timeout.json) — warning, status:warning, offline-safe
- [Boot process is unavailable](scenarios/boot-unavailable.json) — critical, status:error, admin
- [Boot process is in an unsafe state](scenarios/boot-unsafe-state.json) — critical, status:error, admin

## Clock

- [System time is degraded](scenarios/clock-degraded.json) — warning, status:warning, offline-safe
- [System time has a failed dependency](scenarios/clock-dependency-failed.json) — error, status:error, admin
- [System time meets its healthy baseline](scenarios/clock-healthy-baseline.json) — info, status:ok, offline-safe
- [System time is intermittent](scenarios/clock-intermittent.json) — warning, status:warning, offline-safe
- [System time is misconfigured](scenarios/clock-misconfigured.json) — error, status:error, admin
- [System time did not recover](scenarios/clock-recovery-failed.json) — critical, status:error, admin
- [System time has exhausted a resource](scenarios/clock-resource-exhausted.json) — critical, status:error, admin
- [System time times out](scenarios/clock-timeout.json) — warning, status:warning, offline-safe
- [System time is unavailable](scenarios/clock-unavailable.json) — critical, status:error, admin
- [System time is in an unsafe state](scenarios/clock-unsafe-state.json) — critical, status:error, admin

## Configuration

- [Rtylr configuration is degraded](scenarios/configuration-degraded.json) — warning, status:warning, offline-safe
- [Rtylr configuration has a failed dependency](scenarios/configuration-dependency-failed.json) — error, status:error, admin
- [Rtylr configuration meets its healthy baseline](scenarios/configuration-healthy-baseline.json) — info, status:ok, offline-safe
- [Rtylr configuration is intermittent](scenarios/configuration-intermittent.json) — warning, status:warning, offline-safe
- [Rtylr configuration is misconfigured](scenarios/configuration-misconfigured.json) — error, status:error, admin
- [Rtylr configuration did not recover](scenarios/configuration-recovery-failed.json) — critical, status:error, admin
- [Rtylr configuration has exhausted a resource](scenarios/configuration-resource-exhausted.json) — critical, status:error, admin
- [Rtylr configuration times out](scenarios/configuration-timeout.json) — warning, status:warning, offline-safe
- [Rtylr configuration is unavailable](scenarios/configuration-unavailable.json) — critical, status:error, admin
- [Rtylr configuration is in an unsafe state](scenarios/configuration-unsafe-state.json) — critical, status:error, admin

## Display

- [Display output is degraded](scenarios/display-degraded.json) — warning, status:warning, offline-safe
- [Display output has a failed dependency](scenarios/display-dependency-failed.json) — error, status:error, admin
- [Display output meets its healthy baseline](scenarios/display-healthy-baseline.json) — info, status:ok, offline-safe
- [Display output is intermittent](scenarios/display-intermittent.json) — warning, status:warning, offline-safe
- [Display output is misconfigured](scenarios/display-misconfigured.json) — error, status:error, admin
- [Display output did not recover](scenarios/display-recovery-failed.json) — critical, status:error, admin
- [Display output has exhausted a resource](scenarios/display-resource-exhausted.json) — critical, status:error, admin
- [Display output times out](scenarios/display-timeout.json) — warning, status:warning, offline-safe
- [Display output is unavailable](scenarios/display-unavailable.json) — critical, status:error, admin
- [Display output is in an unsafe state](scenarios/display-unsafe-state.json) — critical, status:error, admin

## Dns

- [Name resolution is degraded](scenarios/dns-degraded.json) — warning, status:warning
- [Name resolution has a failed dependency](scenarios/dns-dependency-failed.json) — error, status:error, admin
- [Name resolution meets its healthy baseline](scenarios/dns-healthy-baseline.json) — info, status:ok
- [Name resolution is intermittent](scenarios/dns-intermittent.json) — warning, status:warning
- [Name resolution is misconfigured](scenarios/dns-misconfigured.json) — error, status:error, admin
- [Name resolution did not recover](scenarios/dns-recovery-failed.json) — critical, status:error, admin
- [Name resolution has exhausted a resource](scenarios/dns-resource-exhausted.json) — critical, status:error, admin
- [Name resolution times out](scenarios/dns-timeout.json) — warning, status:warning
- [Name resolution is unavailable](scenarios/dns-unavailable.json) — critical, status:error, admin
- [Name resolution is in an unsafe state](scenarios/dns-unsafe-state.json) — critical, status:error, admin

## Ethernet

- [Wired network is degraded](scenarios/ethernet-degraded.json) — warning, status:warning
- [Wired network has a failed dependency](scenarios/ethernet-dependency-failed.json) — error, status:error, admin
- [Wired network meets its healthy baseline](scenarios/ethernet-healthy-baseline.json) — info, status:ok
- [Wired network is intermittent](scenarios/ethernet-intermittent.json) — warning, status:warning
- [Wired network is misconfigured](scenarios/ethernet-misconfigured.json) — error, status:error, admin
- [Wired network did not recover](scenarios/ethernet-recovery-failed.json) — critical, status:error, admin
- [Wired network has exhausted a resource](scenarios/ethernet-resource-exhausted.json) — critical, status:error, admin
- [Wired network times out](scenarios/ethernet-timeout.json) — warning, status:warning
- [Wired network is unavailable](scenarios/ethernet-unavailable.json) — critical, status:error, admin
- [Wired network is in an unsafe state](scenarios/ethernet-unsafe-state.json) — critical, status:error, admin

## Filesystem

- [System filesystem is degraded](scenarios/filesystem-degraded.json) — warning, status:warning, offline-safe
- [System filesystem has a failed dependency](scenarios/filesystem-dependency-failed.json) — error, status:error, admin
- [System filesystem meets its healthy baseline](scenarios/filesystem-healthy-baseline.json) — info, status:ok, offline-safe
- [System filesystem is intermittent](scenarios/filesystem-intermittent.json) — warning, status:warning, offline-safe
- [System filesystem is misconfigured](scenarios/filesystem-misconfigured.json) — error, status:error, admin
- [System filesystem did not recover](scenarios/filesystem-recovery-failed.json) — critical, status:error, admin
- [System filesystem has exhausted a resource](scenarios/filesystem-resource-exhausted.json) — critical, status:error, admin
- [System filesystem times out](scenarios/filesystem-timeout.json) — warning, status:warning, offline-safe
- [System filesystem is unavailable](scenarios/filesystem-unavailable.json) — critical, status:error, admin
- [System filesystem is in an unsafe state](scenarios/filesystem-unsafe-state.json) — critical, status:error, admin

## Gateway

- [Default gateway is degraded](scenarios/gateway-degraded.json) — warning, status:warning
- [Default gateway has a failed dependency](scenarios/gateway-dependency-failed.json) — error, status:error, admin
- [Default gateway meets its healthy baseline](scenarios/gateway-healthy-baseline.json) — info, status:ok
- [Default gateway is intermittent](scenarios/gateway-intermittent.json) — warning, status:warning
- [Default gateway is misconfigured](scenarios/gateway-misconfigured.json) — error, status:error, admin
- [Default gateway did not recover](scenarios/gateway-recovery-failed.json) — critical, status:error, admin
- [Default gateway has exhausted a resource](scenarios/gateway-resource-exhausted.json) — critical, status:error, admin
- [Default gateway times out](scenarios/gateway-timeout.json) — warning, status:warning
- [Default gateway is unavailable](scenarios/gateway-unavailable.json) — critical, status:error, admin
- [Default gateway is in an unsafe state](scenarios/gateway-unsafe-state.json) — critical, status:error, admin

## Installer

- [Installer is degraded](scenarios/installer-degraded.json) — warning, status:warning
- [Installer has a failed dependency](scenarios/installer-dependency-failed.json) — error, status:error, admin
- [Installer meets its healthy baseline](scenarios/installer-healthy-baseline.json) — info, status:ok
- [Installer is intermittent](scenarios/installer-intermittent.json) — warning, status:warning
- [Installer is misconfigured](scenarios/installer-misconfigured.json) — error, status:error, admin
- [Installer did not recover](scenarios/installer-recovery-failed.json) — critical, status:error, admin
- [Installer has exhausted a resource](scenarios/installer-resource-exhausted.json) — critical, status:error, admin
- [Installer times out](scenarios/installer-timeout.json) — warning, status:warning
- [Installer is unavailable](scenarios/installer-unavailable.json) — critical, status:error, admin
- [Installer is in an unsafe state](scenarios/installer-unsafe-state.json) — critical, status:error, admin

## Keyboard

- [Keyboard input is degraded](scenarios/keyboard-degraded.json) — warning, status:warning, offline-safe
- [Keyboard input has a failed dependency](scenarios/keyboard-dependency-failed.json) — error, status:error, admin
- [Keyboard input meets its healthy baseline](scenarios/keyboard-healthy-baseline.json) — info, status:ok, offline-safe
- [Keyboard input is intermittent](scenarios/keyboard-intermittent.json) — warning, status:warning, offline-safe
- [Keyboard input is misconfigured](scenarios/keyboard-misconfigured.json) — error, status:error, admin
- [Keyboard input did not recover](scenarios/keyboard-recovery-failed.json) — critical, status:error, admin
- [Keyboard input has exhausted a resource](scenarios/keyboard-resource-exhausted.json) — critical, status:error, admin
- [Keyboard input times out](scenarios/keyboard-timeout.json) — warning, status:warning, offline-safe
- [Keyboard input is unavailable](scenarios/keyboard-unavailable.json) — critical, status:error, admin
- [Keyboard input is in an unsafe state](scenarios/keyboard-unsafe-state.json) — critical, status:error, admin

## Logs

- [Operational logs is degraded](scenarios/logs-degraded.json) — warning, status:warning, offline-safe
- [Operational logs has a failed dependency](scenarios/logs-dependency-failed.json) — error, status:error, admin
- [Operational logs meets its healthy baseline](scenarios/logs-healthy-baseline.json) — info, status:ok, offline-safe
- [Operational logs is intermittent](scenarios/logs-intermittent.json) — warning, status:warning, offline-safe
- [Operational logs is misconfigured](scenarios/logs-misconfigured.json) — error, status:error, admin
- [Operational logs did not recover](scenarios/logs-recovery-failed.json) — critical, status:error, admin
- [Operational logs has exhausted a resource](scenarios/logs-resource-exhausted.json) — critical, status:error, admin
- [Operational logs times out](scenarios/logs-timeout.json) — warning, status:warning, offline-safe
- [Operational logs is unavailable](scenarios/logs-unavailable.json) — critical, status:error, admin
- [Operational logs is in an unsafe state](scenarios/logs-unsafe-state.json) — critical, status:error, admin

## Mouse

- [Pointer input is degraded](scenarios/mouse-degraded.json) — warning, status:warning, offline-safe
- [Pointer input has a failed dependency](scenarios/mouse-dependency-failed.json) — error, status:error, admin
- [Pointer input meets its healthy baseline](scenarios/mouse-healthy-baseline.json) — info, status:ok, offline-safe
- [Pointer input is intermittent](scenarios/mouse-intermittent.json) — warning, status:warning, offline-safe
- [Pointer input is misconfigured](scenarios/mouse-misconfigured.json) — error, status:error, admin
- [Pointer input did not recover](scenarios/mouse-recovery-failed.json) — critical, status:error, admin
- [Pointer input has exhausted a resource](scenarios/mouse-resource-exhausted.json) — critical, status:error, admin
- [Pointer input times out](scenarios/mouse-timeout.json) — warning, status:warning, offline-safe
- [Pointer input is unavailable](scenarios/mouse-unavailable.json) — critical, status:error, admin
- [Pointer input is in an unsafe state](scenarios/mouse-unsafe-state.json) — critical, status:error, admin

## Network

- [Network connectivity is degraded](scenarios/network-degraded.json) — warning, status:warning
- [Network connectivity has a failed dependency](scenarios/network-dependency-failed.json) — error, status:error, admin
- [Network connectivity meets its healthy baseline](scenarios/network-healthy-baseline.json) — info, status:ok
- [Network connectivity is intermittent](scenarios/network-intermittent.json) — warning, status:warning
- [Network connectivity is misconfigured](scenarios/network-misconfigured.json) — error, status:error, admin
- [Network connectivity did not recover](scenarios/network-recovery-failed.json) — critical, status:error, admin
- [Network connectivity has exhausted a resource](scenarios/network-resource-exhausted.json) — critical, status:error, admin
- [Network connectivity times out](scenarios/network-timeout.json) — warning, status:warning
- [Network connectivity is unavailable](scenarios/network-unavailable.json) — critical, status:error, admin
- [Network connectivity is in an unsafe state](scenarios/network-unsafe-state.json) — critical, status:error, admin

## Power

- [Power controls is degraded](scenarios/power-degraded.json) — warning, status:warning, offline-safe
- [Power controls has a failed dependency](scenarios/power-dependency-failed.json) — error, status:error, admin
- [Power controls meets its healthy baseline](scenarios/power-healthy-baseline.json) — info, status:ok, offline-safe
- [Power controls is intermittent](scenarios/power-intermittent.json) — warning, status:warning, offline-safe
- [Power controls is misconfigured](scenarios/power-misconfigured.json) — error, status:error, admin
- [Power controls did not recover](scenarios/power-recovery-failed.json) — critical, status:error, admin
- [Power controls has exhausted a resource](scenarios/power-resource-exhausted.json) — critical, status:error, admin
- [Power controls times out](scenarios/power-timeout.json) — warning, status:warning, offline-safe
- [Power controls is unavailable](scenarios/power-unavailable.json) — critical, status:error, admin
- [Power controls is in an unsafe state](scenarios/power-unsafe-state.json) — critical, status:error, admin

## Printing

- [Printing is degraded](scenarios/printing-degraded.json) — warning, status:warning, offline-safe
- [Printing has a failed dependency](scenarios/printing-dependency-failed.json) — error, status:error, admin
- [Printing meets its healthy baseline](scenarios/printing-healthy-baseline.json) — info, status:ok, offline-safe
- [Printing is intermittent](scenarios/printing-intermittent.json) — warning, status:warning, offline-safe
- [Printing is misconfigured](scenarios/printing-misconfigured.json) — error, status:error, admin
- [Printing did not recover](scenarios/printing-recovery-failed.json) — critical, status:error, admin
- [Printing has exhausted a resource](scenarios/printing-resource-exhausted.json) — critical, status:error, admin
- [Printing times out](scenarios/printing-timeout.json) — warning, status:warning, offline-safe
- [Printing is unavailable](scenarios/printing-unavailable.json) — critical, status:error, admin
- [Printing is in an unsafe state](scenarios/printing-unsafe-state.json) — critical, status:error, admin

## Session

- [Business session is degraded](scenarios/session-degraded.json) — warning, status:warning, offline-safe
- [Business session has a failed dependency](scenarios/session-dependency-failed.json) — error, status:error, admin
- [Business session meets its healthy baseline](scenarios/session-healthy-baseline.json) — info, status:ok, offline-safe
- [Business session is intermittent](scenarios/session-intermittent.json) — warning, status:warning, offline-safe
- [Business session is misconfigured](scenarios/session-misconfigured.json) — error, status:error, admin
- [Business session did not recover](scenarios/session-recovery-failed.json) — critical, status:error, admin
- [Business session has exhausted a resource](scenarios/session-resource-exhausted.json) — critical, status:error, admin
- [Business session times out](scenarios/session-timeout.json) — warning, status:warning, offline-safe
- [Business session is unavailable](scenarios/session-unavailable.json) — critical, status:error, admin
- [Business session is in an unsafe state](scenarios/session-unsafe-state.json) — critical, status:error, admin

## Storage

- [Local storage is degraded](scenarios/storage-degraded.json) — warning, status:warning, offline-safe
- [Local storage has a failed dependency](scenarios/storage-dependency-failed.json) — error, status:error, admin
- [Local storage meets its healthy baseline](scenarios/storage-healthy-baseline.json) — info, status:ok, offline-safe
- [Local storage is intermittent](scenarios/storage-intermittent.json) — warning, status:warning, offline-safe
- [Local storage is misconfigured](scenarios/storage-misconfigured.json) — error, status:error, admin
- [Local storage did not recover](scenarios/storage-recovery-failed.json) — critical, status:error, admin
- [Local storage has exhausted a resource](scenarios/storage-resource-exhausted.json) — critical, status:error, admin
- [Local storage times out](scenarios/storage-timeout.json) — warning, status:warning, offline-safe
- [Local storage is unavailable](scenarios/storage-unavailable.json) — critical, status:error, admin
- [Local storage is in an unsafe state](scenarios/storage-unsafe-state.json) — critical, status:error, admin

## Support

- [Support workflow is degraded](scenarios/support-degraded.json) — warning, status:warning
- [Support workflow has a failed dependency](scenarios/support-dependency-failed.json) — error, status:error, admin
- [Support workflow meets its healthy baseline](scenarios/support-healthy-baseline.json) — info, status:ok
- [Support workflow is intermittent](scenarios/support-intermittent.json) — warning, status:warning
- [Support workflow is misconfigured](scenarios/support-misconfigured.json) — error, status:error, admin
- [Support workflow did not recover](scenarios/support-recovery-failed.json) — critical, status:error, admin
- [Support workflow has exhausted a resource](scenarios/support-resource-exhausted.json) — critical, status:error, admin
- [Support workflow times out](scenarios/support-timeout.json) — warning, status:warning
- [Support workflow is unavailable](scenarios/support-unavailable.json) — critical, status:error, admin
- [Support workflow is in an unsafe state](scenarios/support-unsafe-state.json) — critical, status:error, admin

## Thermal

- [Thermal state is degraded](scenarios/thermal-degraded.json) — warning, status:warning, offline-safe
- [Thermal state has a failed dependency](scenarios/thermal-dependency-failed.json) — error, status:error, admin
- [Thermal state meets its healthy baseline](scenarios/thermal-healthy-baseline.json) — info, status:ok, offline-safe
- [Thermal state is intermittent](scenarios/thermal-intermittent.json) — warning, status:warning, offline-safe
- [Thermal state is misconfigured](scenarios/thermal-misconfigured.json) — error, status:error, admin
- [Thermal state did not recover](scenarios/thermal-recovery-failed.json) — critical, status:error, admin
- [Thermal state has exhausted a resource](scenarios/thermal-resource-exhausted.json) — critical, status:error, admin
- [Thermal state times out](scenarios/thermal-timeout.json) — warning, status:warning, offline-safe
- [Thermal state is unavailable](scenarios/thermal-unavailable.json) — critical, status:error, admin
- [Thermal state is in an unsafe state](scenarios/thermal-unsafe-state.json) — critical, status:error, admin

## Touchscreen

- [Touch input is degraded](scenarios/touchscreen-degraded.json) — warning, status:warning, offline-safe
- [Touch input has a failed dependency](scenarios/touchscreen-dependency-failed.json) — error, status:error, admin
- [Touch input meets its healthy baseline](scenarios/touchscreen-healthy-baseline.json) — info, status:ok, offline-safe
- [Touch input is intermittent](scenarios/touchscreen-intermittent.json) — warning, status:warning, offline-safe
- [Touch input is misconfigured](scenarios/touchscreen-misconfigured.json) — error, status:error, admin
- [Touch input did not recover](scenarios/touchscreen-recovery-failed.json) — critical, status:error, admin
- [Touch input has exhausted a resource](scenarios/touchscreen-resource-exhausted.json) — critical, status:error, admin
- [Touch input times out](scenarios/touchscreen-timeout.json) — warning, status:warning, offline-safe
- [Touch input is unavailable](scenarios/touchscreen-unavailable.json) — critical, status:error, admin
- [Touch input is in an unsafe state](scenarios/touchscreen-unsafe-state.json) — critical, status:error, admin

## Updates

- [System updates is degraded](scenarios/updates-degraded.json) — warning, status:warning
- [System updates has a failed dependency](scenarios/updates-dependency-failed.json) — error, status:error, admin
- [System updates meets its healthy baseline](scenarios/updates-healthy-baseline.json) — info, status:ok
- [System updates is intermittent](scenarios/updates-intermittent.json) — warning, status:warning
- [System updates is misconfigured](scenarios/updates-misconfigured.json) — error, status:error, admin
- [System updates did not recover](scenarios/updates-recovery-failed.json) — critical, status:error, admin
- [System updates has exhausted a resource](scenarios/updates-resource-exhausted.json) — critical, status:error, admin
- [System updates times out](scenarios/updates-timeout.json) — warning, status:warning
- [System updates is unavailable](scenarios/updates-unavailable.json) — critical, status:error, admin
- [System updates is in an unsafe state](scenarios/updates-unsafe-state.json) — critical, status:error, admin

## Usb

- [USB peripherals is degraded](scenarios/usb-degraded.json) — warning, status:warning, offline-safe
- [USB peripherals has a failed dependency](scenarios/usb-dependency-failed.json) — error, status:error, admin
- [USB peripherals meets its healthy baseline](scenarios/usb-healthy-baseline.json) — info, status:ok, offline-safe
- [USB peripherals is intermittent](scenarios/usb-intermittent.json) — warning, status:warning, offline-safe
- [USB peripherals is misconfigured](scenarios/usb-misconfigured.json) — error, status:error, admin
- [USB peripherals did not recover](scenarios/usb-recovery-failed.json) — critical, status:error, admin
- [USB peripherals has exhausted a resource](scenarios/usb-resource-exhausted.json) — critical, status:error, admin
- [USB peripherals times out](scenarios/usb-timeout.json) — warning, status:warning, offline-safe
- [USB peripherals is unavailable](scenarios/usb-unavailable.json) — critical, status:error, admin
- [USB peripherals is in an unsafe state](scenarios/usb-unsafe-state.json) — critical, status:error, admin

## Wifi

- [Wi-Fi is degraded](scenarios/wifi-degraded.json) — warning, status:warning
- [Wi-Fi has a failed dependency](scenarios/wifi-dependency-failed.json) — error, status:error, admin
- [Wi-Fi meets its healthy baseline](scenarios/wifi-healthy-baseline.json) — info, status:ok
- [Wi-Fi is intermittent](scenarios/wifi-intermittent.json) — warning, status:warning
- [Wi-Fi is misconfigured](scenarios/wifi-misconfigured.json) — error, status:error, admin
- [Wi-Fi did not recover](scenarios/wifi-recovery-failed.json) — critical, status:error, admin
- [Wi-Fi has exhausted a resource](scenarios/wifi-resource-exhausted.json) — critical, status:error, admin
- [Wi-Fi times out](scenarios/wifi-timeout.json) — warning, status:warning
- [Wi-Fi is unavailable](scenarios/wifi-unavailable.json) — critical, status:error, admin
- [Wi-Fi is in an unsafe state](scenarios/wifi-unsafe-state.json) — critical, status:error, admin
