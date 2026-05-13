---
name: feature-flag-debt-audit
description: Audit stale feature flags, launch toggles, kill switches, and experiment gates from a flag export plus source tree. Use when a team needs to find expired or unreferenced flags, prevent risky deletes, assign owners, and produce a cleanup plan that is safer than asking an agent to guess from code snippets.
---

# Feature Flag Debt Audit

## Overview

Use this skill to turn feature-flag debt into an owner-ready cleanup plan. The goal is to remove stale release toggles and expired experiments without breaking operational kill switches, compliance controls, or partially rolled-out features.

Feature flags are useful while a change is moving through release. They become debt when nobody knows who owns them, whether they are still evaluated, or which code paths can be deleted.

## Use And Do Not Use

Use for:

- Cleaning up stale release toggles, experiment flags, gradual rollout flags, and migration flags.
- Reviewing a flag export from LaunchDarkly, Statsig, Unleash, Split, Harness, PostHog, or an internal flag system.
- Scanning a local repository for flag references before deleting code.
- Producing cleanup tickets with owner, risk, evidence, and verification steps.
- Distinguishing removable launch flags from permanent ops flags or kill switches.

Do not use for:

- Deleting production flags without owner approval.
- Inferring business rollout state from code references alone.
- Calling vendor APIs or changing remote flag state unless the user explicitly asks and supplies credentials through environment variables.
- Removing security, billing, migration, or data-loss guardrails without a rollback plan.

## Required Inputs

Ask only for missing inputs that materially affect the decision:

- Flag export as CSV or JSON. Preferred fields: `key`, `name`, `status`, `kind`, `owner`, `created_at`, `last_seen`, `expires_at`, `permanent`, `description`.
- Repository path or code directory to scan.
- Flag naming conventions and known permanent flag prefixes, such as `ops_`, `kill_`, `perm_`, or `guard_`.
- Cleanup policy, such as stale after 60, 90, or 180 days without evaluation.
- Release constraints: owner approval rules, audit requirements, or branches where flags must remain.

If the user only has pasted flag names, produce a provisional report and state that reference counts and age signals are missing.

## Workflow

### 1. Preserve The Deletion Boundary

Before recommending a delete, capture:

- Flag key and display name.
- Owner or owning team.
- Status, type, creation date, last-seen date, and expiry date.
- Code references and file paths.
- Whether the flag is a release toggle, experiment, migration, entitlement, ops kill switch, or compliance guardrail.
- Rollback path if removal causes production behavior to change.

Read `references/cleanup-rules.md` before classifying flags that touch auth, billing, data migration, compliance, incident response, or infrastructure failover.

### 2. Run The Local Audit When Files Exist

Use the bundled script with explicit paths:

```bash
python3 feature-flag-debt-audit/scripts/feature_flag_debt_audit.py \
  --flags /absolute/path/flags.csv \
  --code-dir /absolute/path/repo \
  --stale-days 90
```

For JSON exports, the script accepts either a list of flag objects or an object containing a `flags` list.

### 3. Classify Each Flag

Use one primary action:

- `delete_candidate`: expired or long-stale release/experiment flag, low reference risk, and no permanent signal.
- `owner_review`: stale or expired but owner, rollout state, or references need human confirmation.
- `instrument_first`: likely active but last-seen data is missing or untrusted.
- `keep_permanent`: kill switch, ops guard, entitlement, compliance control, or explicitly permanent flag.

Use one primary risk:

- `low`: no references or one isolated reference, owner exists, not permanent, stale by policy.
- `medium`: several references, missing owner, ambiguous rollout state, or partial stale signal.
- `high`: many references, permanent or kill-switch signal, security/billing/data path, or missing rollback evidence.

Never recommend deleting a flag purely because its name sounds old.

### 4. Produce The Cleanup Report

Return:

```markdown
## Flag Debt Decision
[Delete candidates / Owner review needed / Instrument first / No safe delete today]

## Cleanup Candidates
| Flag | Action | Risk | Evidence | Owner | Next step |
|---|---|---|---|---|---|

## Guardrails
[Flags that must not be deleted without explicit owner approval]

## Code References
[Files and counts grouped by flag]

## Cleanup Tickets
[One ticket per delete or owner-review candidate]

## Verification Plan
[Tests, rollout checks, metrics, and rollback confirmation]
```

Use `templates/cleanup-ticket.md` when the user asks for tickets.

### 5. Apply Guardrails Before Suggesting Edits

Do not suggest code deletion until the report has:

- Owner or escalation path.
- Current production state evidence, or a clear missing-evidence marker.
- Reference list with file paths.
- Test or smoke-check command to run after deletion.
- Rollback or restore instruction for the flag system.

## Examples And Acceptance Checks

Positive example: "Use $feature-flag-debt-audit on this LaunchDarkly CSV and repo. Find flags older than 90 days that are safe cleanup candidates." The skill should scan references, identify expired release toggles, and produce owner-ready cleanup tickets.

Positive internal-tool example: "We have a JSON export from our homegrown flag service and a Rails app." The skill should normalize known fields, scan code references, and label missing metadata instead of guessing.

Negative example: "Delete every flag with old in the name." Refuse the delete plan and ask for flag metadata or owner confirmation.

Boundary example: "I only have a list of five flag names." Produce a provisional checklist and do not assign low risk.

## Validation

Smoke-test the bundled fixture:

```bash
python3 feature-flag-debt-audit/scripts/feature_flag_debt_audit.py \
  --flags feature-flag-debt-audit/scripts/fixtures/flags.csv \
  --code-dir feature-flag-debt-audit/scripts/fixtures/sample_app \
  --stale-days 90 \
  --today 2026-05-12
```

Expected result: a Markdown report with `Flag Debt Decision`, at least one `delete_candidate`, at least one `keep_permanent`, reference counts, and cleanup ticket text.
