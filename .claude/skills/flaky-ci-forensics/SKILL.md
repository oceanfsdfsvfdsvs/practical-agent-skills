---
name: flaky-ci-forensics
description: Analyze flaky CI/test failures from JUnit XML, test history, and CI logs. Use when a team needs to distinguish true regressions from flakes, estimate rerun cost, choose quarantine versus fix-now actions, or produce a prioritized triage plan.
---

# Flaky CI Forensics

This is a Claude Code install mirror for `flaky-ci-forensics`. Keep the canonical implementation in `flaky-ci-forensics/`.

## Trigger

Use when the user provides CI logs, JUnit XML, test history, or asks whether failing tests are flaky, should be rerun, should be quarantined, or need a fix-now plan.

## Workflow

1. Preserve the exact evidence: test names, failure messages, commit, retry count, runner metadata, and whether the same commit passed on retry.
2. If file artifacts exist, run the canonical analyzer from the repository root:

```bash
python3 flaky-ci-forensics/scripts/flaky_ci_forensics.py \
  --junit flaky-ci-forensics/scripts/fixtures/junit.xml \
  --log flaky-ci-forensics/scripts/fixtures/ci.log \
  --history flaky-ci-forensics/scripts/fixtures/history.csv
```

3. Classify failures into the canonical buckets from `flaky-ci-forensics/references/flaky-test-rules.md`.
4. Return the standard report: CI decision, failure cluster, cost and frequency, likely root cause, minimal fix plan, instrumentation, and guardrails.

## Guardrails

- Do not label deterministic assertion mismatches as flaky without retry-pass or environment evidence.
- Do not quarantine auth, billing, payment, migration, security, deletion, or compliance coverage without explicit approval.
- Quarantine recommendations need owner, expiry, and tracking issue.

