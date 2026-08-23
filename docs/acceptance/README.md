# Business-continuity acceptance catalog

Rtylr OS is meant to keep a business operational when its primary application,
network, peripherals, or local device state misbehaves. This catalog turns that
promise into reviewable acceptance scenarios.

Each file under `scenarios/` describes one observable condition and records:

- the signal an operator or the shell can observe
- the status Rtylr should present without hiding the failure
- the safe first action available to an operator
- any protected action that requires the admin PIN
- the condition that proves service has recovered
- whether work can continue without network connectivity

The scenarios are product contracts, not automated shell commands. They never
authorize arbitrary command execution and they do not replace hardware-specific
certification. Their immediate purpose is to keep UI, diagnostics, recovery, and
support behavior consistent as the OS grows.

## Validation

Run the complete source gate:

```bash
make check
```

Or validate only this catalog:

```bash
./scripts/check-scenarios.py
```

The Python loader enforces the same required fields and invariants as
`schema.json`, including unique IDs, lowercase slugs, supported severities,
non-empty response steps, and protected admin actions.

## Naming

Scenario IDs are `<domain>-<condition>`. File names must match the ID with a
`.json` suffix. Domains describe a business-device subsystem rather than an
industry; point of sale may consume these capabilities, but it does not define
the catalog.
