# Operator response taxonomy

Acceptance scenarios use a small response vocabulary so a team member can act
quickly without needing Linux knowledge.

## Observe

Confirm the status card, affected capability, and support code. Observation must
not change system state and must never require the admin PIN.

## Retry

Repeat an ordinary application action when duplicate work is impossible or
clearly prevented by the application. Rtylr must not instruct a user to retry a
payment, write, or submission when the prior result is unknown.

## Recover

Use a narrowly scoped Rtylr action such as reopening the primary business app,
reconnecting networking, or refreshing health checks. Any action that can stop
work, change configuration, or affect the whole device requires the admin PIN.

## Continue offline

Continue only when the scenario explicitly marks `offline_safe` true and the
business application owns a verified offline workflow. Rtylr does not infer that
queued writes or transactions are safe.

## Escalate

Capture the support code, exact status, time, and last known successful action.
Escalation is the default when recovery would risk duplicate records, lost work,
unsafe hardware behavior, or an unknown system state.

## Language rules

- describe what is known rather than guessing at a root cause
- identify whether an action can interrupt work
- use “device” and “business app,” not industry-specific operator labels
- never expose credentials, admin PINs, tokens, or full logs in an instruction
- state a measurable success condition after every recovery action
