# Flaky CI Forensics

`flaky-ci-forensics` helps an agent turn intermittent CI/test failures into a concrete triage decision. It combines a domain workflow, failure taxonomy, local parser, and report template so the result is more stable than asking a model to "debug this flaky test" from raw logs.

## What It Solves

Teams often waste CI minutes and developer attention rerunning failures that later pass, while real regressions can also be mislabeled as flakes. This skill forces the agent to preserve evidence, classify the failure mode, estimate cost, and recommend a bounded next action.

## Included Assets

- `SKILL.md`: trigger conditions, workflow, output format, and safety guardrails.
- `agents/openai.yaml`: Codex/OpenAI-style metadata.
- `references/flaky-test-rules.md`: failure taxonomy, decision rules, and anti-patterns.
- `templates/triage-report.md`: report skeleton.
- `scripts/flaky_ci_forensics.py`: local JUnit/log/history analyzer.
- `scripts/fixtures/`: smoke-test JUnit, CI log, and history CSV.
- `.claude/skills/flaky-ci-forensics/SKILL.md`: Claude Code mirror.
- `openclaw/README.md` and `hermes/README.md`: runtime installation notes.

## Quick Start

```bash
python3 flaky-ci-forensics/scripts/flaky_ci_forensics.py \
  --junit flaky-ci-forensics/scripts/fixtures/junit.xml \
  --log flaky-ci-forensics/scripts/fixtures/ci.log \
  --history flaky-ci-forensics/scripts/fixtures/history.csv \
  --avg-job-minutes 14 \
  --runs-per-day 60
```

## Inputs

- JUnit XML from CI or local test runs.
- CI logs with failure excerpts, retry information, runner metadata, or browser logs.
- Optional history CSV with test-level run/failure/rerun-pass counts.
- Optional cost values for average job minutes and runs per day.

## Output

The script prints a Markdown report with:

- CI decision.
- Failure clusters.
- Cost and frequency estimate.
- Root-cause hypotheses.
- Minimal fix plan.
- Instrumentation and guardrails.

## Runtime Status

| Runtime | Status |
|---|---|
| Codex/OpenAI-style | Supported with `SKILL.md` and `agents/openai.yaml`. |
| Claude Code | Supported through `.claude/skills/flaky-ci-forensics/SKILL.md` mirror or by copying this directory. |
| OpenClaw | CLI present, but this local skill is not installed or published to ClawHub, so runtime visibility is not verified. |
| Hermes | CLI present, but `hermes skills inspect` does not accept this local directory; install requires a supported registry identifier or direct URL. |
