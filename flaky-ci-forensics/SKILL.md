---
name: flaky-ci-forensics
description: Analyze flaky CI/test failures from JUnit XML, test history, and CI logs. Use when a team needs to distinguish true regressions from flakes, estimate rerun cost, choose quarantine versus fix-now actions, or produce a prioritized triage plan for GitHub Actions, CircleCI, Buildkite, Jenkins, Playwright, pytest, Jest, RSpec, Go test, or similar pipelines.
---

# Flaky CI Forensics

## Overview

Use this skill to convert noisy CI failures into a defensible flaky-test triage report. The goal is not to make tests pass by repeatedly rerunning them; the goal is to identify the failure pattern, decide whether the team is looking at a real product regression or a flake, and preserve enough evidence for a targeted fix.

## Use And Do Not Use

Use for:

- CI jobs where tests fail intermittently and pass on retry.
- JUnit XML, pytest/Jest/RSpec/Go test reports, Playwright traces, browser logs, or copied CI logs.
- Estimating wasted CI minutes and developer time from reruns.
- Deciding whether to quarantine, mark unstable, fix immediately, add instrumentation, or reject a flaky-test excuse.
- Building a concise issue comment, incident note, or test-owner handoff.

Do not use for:

- Hiding real product regressions behind "probably flaky" language.
- Deleting or disabling tests without owner approval and replacement coverage.
- Debugging a live production incident where CI logs are only a side signal.
- Sending logs to external services without explicit user approval.

## Required Inputs

Ask only for missing inputs that materially affect the decision:

- Test report path, pasted failure text, or CI log path.
- Framework and CI system when known.
- Whether the same commit passed on retry or failed on multiple branches.
- Recent failure history, such as run counts, failure counts, rerun-pass counts, or links to prior CI runs.
- Cost context if available: average job minutes, runs per day, and approximate staff cost.
- Ownership constraints: test owner, code area, release blocker status, and whether quarantine is allowed.

If the user only has a single failure log, produce a sample-limited report and label flake confidence as provisional.

## Workflow

### 1. Preserve Evidence Before Recommending A Fix

Capture:

- Commit SHA, branch, CI job, runner image, timestamp, and retry count.
- Exact test names and failure messages.
- Whether the same test passed on rerun without code changes.
- Environmental clues: browser version, timezone, locale, network service, seed, parallel worker, CPU/memory pressure, container image, and external dependency.

Read `references/flaky-test-rules.md` when the failure involves timing, async UI, network, parallelism, fixture leakage, external services, or suspicious rerun behavior.

### 2. Run Local Forensics When Files Exist

Use the bundled script for JUnit XML, CI logs, and optional history CSV:

```bash
python3 flaky-ci-forensics/scripts/flaky_ci_forensics.py \
  --junit /absolute/path/junit.xml \
  --log /absolute/path/ci.log \
  --history /absolute/path/history.csv \
  --avg-job-minutes 12 \
  --runs-per-day 80
```

History CSV columns are optional but should use these names when available:

```csv
test,runs,failures,rerun_passes,first_seen,last_seen,owner
```

For pasted logs, apply the same taxonomy manually and state that XML/history metrics are unavailable.

### 3. Classify The Failure

Classify each failing test into one primary bucket:

- `timeout_or_wait`: timeouts, missing waits, event-loop starvation, animation or async readiness.
- `network_or_external_service`: connection resets, DNS, third-party sandbox, rate limits, HTTP 5xx.
- `order_or_state_leak`: test pollution, shared database state, global mocks, random ordering.
- `parallelism_or_race`: thread/process race, port collision, shared temp paths, non-atomic setup.
- `clock_locale_or_randomness`: timezone, daylight saving, locale, seeded randomness, date boundaries.
- `resource_or_runner`: CPU/memory pressure, disk space, browser crash, CI image drift.
- `selector_or_ui_sync`: brittle selectors, detached elements, React hydration, stale DOM handles.
- `assertion_or_product_regression`: deterministic assertion mismatch or likely product behavior change.
- `unknown_needs_instrumentation`: not enough evidence to classify.

Never call a deterministic assertion mismatch a flake just because the team wants the build green.

### 4. Decide Action

Use this action ladder:

- `Fix now`: high confidence product regression, high-frequency flake blocking release, or unsafe false-pass risk.
- `Instrument then rerun`: unknown cause, low evidence, or missing logs that can be captured cheaply.
- `Quarantine with owner and expiry`: high-confidence flake, repeated retry-pass evidence, and an allowed quarantine policy.
- `Rerun once only`: CI infrastructure blip with weak recurrence evidence and low release risk.
- `Do not quarantine`: security, billing, data-loss, migration, auth, or compliance coverage where disabling the test creates unacceptable risk.

### 5. Produce The Triage Report

Return:

```markdown
## CI Decision
[Fix now / Instrument then rerun / Quarantine with owner and expiry / Rerun once only / Do not quarantine]

## Failure Cluster
| Test | Bucket | Flake confidence | Evidence | Owner | Action |
|---|---|---|---|---|---|

## Cost And Frequency
[CI minutes, developer interruption estimate, failure rate, retry-pass signal]

## Likely Root Cause
[Concrete hypothesis tied to evidence]

## Minimal Fix Plan
[Smallest code/test/infrastructure change to test first]

## Instrumentation To Add
[Logs, screenshots, traces, seeds, timestamps, runner metadata]

## Guardrails
[What not to disable, what requires owner approval, when to expire quarantine]
```

## Examples And Acceptance Checks

Positive example: "Use $flaky-ci-forensics on this GitHub Actions JUnit report. The Playwright checkout test fails with a selector timeout but passes on rerun." The skill should classify `selector_or_ui_sync` or `timeout_or_wait`, estimate rerun cost if history exists, and recommend instrumentation or a targeted wait/selector fix before quarantine.

Positive backend example: "Our pytest suite fails randomly with duplicate key errors under `-n auto`." The skill should classify order/state leak or parallelism, ask for seed/worker/db isolation evidence, and avoid generic "rerun CI" advice.

Negative example: "A unit test always fails after I changed the parser." Do not label it flaky without retry-pass or environment evidence; treat it as a regression-debugging task.

Boundary example: "I only have a screenshot that says CI failed." Produce a missing-evidence checklist and do not assign high flake confidence.

## Validation

Smoke-test the bundled fixture:

```bash
python3 flaky-ci-forensics/scripts/flaky_ci_forensics.py \
  --junit flaky-ci-forensics/scripts/fixtures/junit.xml \
  --log flaky-ci-forensics/scripts/fixtures/ci.log \
  --history flaky-ci-forensics/scripts/fixtures/history.csv \
  --avg-job-minutes 14 \
  --runs-per-day 60
```

Expected result: a Markdown report with `CI Decision`, buckets including `timeout_or_wait` and `network_or_external_service`, a retry-pass signal, and a cost estimate.

