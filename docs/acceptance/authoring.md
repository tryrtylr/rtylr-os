# Scenario authoring guide

One scenario should cover one subsystem condition. Keep it small enough that a
reviewer can decide whether the status, operator response, and success criteria
are correct without interpreting another file.

## Required qualities

1. Use an industry-neutral domain such as `application`, `network`, `storage`,
   or `touchscreen`.
2. Name the condition as an observable state, not an assumed vendor defect.
3. Choose the highest severity justified by business interruption or data risk.
4. Describe signals available locally; do not depend on a cloud control plane to
   explain an offline device.
5. Put the safest reversible action first.
6. Require admin access for configuration, process interruption, power actions,
   or anything that could affect another user.
7. Make every success criterion measurable from the shell, application, or a
   deliberate operator check.

## Severity

- `info`: expected healthy baseline or a condition with no interruption
- `warning`: degraded capability with a safe way to continue
- `error`: a capability is unavailable and operator action is required
- `critical`: business continuity, integrity, or safe device operation is at risk

## Expected status

`expected_status` describes the visual state Rtylr should expose: `ok`,
`warning`, `error`, or `neutral`. It is intentionally independent of severity so
future policy can distinguish an informational stopped state from a fault.

## Review checklist

- the file name matches `<domain>-<condition>.json`
- the ID matches the domain and condition fields
- instructions cannot duplicate unknown writes or transactions
- protected steps are separated from ordinary operator steps
- no secret or customer information appears in signals or instructions
- `make check` succeeds
