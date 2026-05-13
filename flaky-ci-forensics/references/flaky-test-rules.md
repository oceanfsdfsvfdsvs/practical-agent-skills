# Flaky Test Rules

## Evidence Levels

| Level | Meaning | Required signal |
|---|---|---|
| High flake confidence | Same code eventually passes without a code change and the failure pattern is known to be nondeterministic. | Retry-pass history, repeated intermittent failures, and a matching bucket. |
| Medium flake confidence | Failure looks environment or timing related, but history is incomplete. | Timeout/network/runner clues plus at least one prior occurrence. |
| Low flake confidence | One failure with little context. | Single log or screenshot; needs instrumentation. |
| Regression likely | Deterministic assertion mismatch, compile error, snapshot drift, or failure after related code change. | Repeatable failure or product behavior change. |

## Failure Buckets

| Bucket | Common signals | First fixes to try |
|---|---|---|
| `timeout_or_wait` | Timeout waiting for async work, polling, event loop, animations, jobs. | Replace sleeps with readiness checks, add trace timestamps, reduce hidden async dependency. |
| `network_or_external_service` | ECONNRESET, DNS, 429, 500, sandbox outage, webhook delay. | Stub dependency, record contract fixture, add retry only around external boundary. |
| `order_or_state_leak` | Passes alone, fails in suite, dirty database, global mocks. | Isolate fixtures, reset state, randomize order locally, record seed. |
| `parallelism_or_race` | Fails with multiple workers, port conflict, shared temp file, duplicate key. | Allocate per-worker resources, lock shared setup, avoid shared mutable globals. |
| `clock_locale_or_randomness` | Timezone, DST, locale, date boundary, random seed. | Freeze time, set locale, persist seed in logs, test boundary cases deterministically. |
| `resource_or_runner` | Browser crash, OOM, disk full, runner image change, CPU starvation. | Capture runner metadata, pin image, split heavy tests, collect memory/CPU metrics. |
| `selector_or_ui_sync` | Detached element, missing selector, hydration, stale handle, click intercepted. | Prefer stable roles/test IDs, wait for application readiness, use trace/screenshot. |
| `assertion_or_product_regression` | Expected/actual mismatch, compile error, deterministic failure. | Debug as product or test logic regression; do not quarantine by default. |
| `unknown_needs_instrumentation` | Generic failure without enough text. | Add logs, screenshots, seed, retry metadata, and artifact capture. |

## Quarantine Guardrails

- Quarantine must have an owner and expiry date.
- Do not quarantine tests covering auth, billing, migration, permissions, security, data deletion, or compliance without explicit approval.
- Keep a tracking issue with failure evidence and the condition for re-enabling the test.
- Prefer marking a test unstable over removing assertions.
- If a quarantined test finds a real regression later, escalate the owner policy rather than extending the quarantine silently.

## Prompt Baseline Failure Modes

A plain prompt usually fails by:

- Over-weighting the most recent stack trace and ignoring history.
- Recommending blanket retries without estimating cost.
- Mislabeling deterministic assertion failures as flaky.
- Producing generic advice such as "increase timeout" without preserving runner metadata.
- Forgetting owner, expiry, and release-risk guardrails.

