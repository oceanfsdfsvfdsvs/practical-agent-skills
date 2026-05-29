# DSAR Request Preflight

Local-first workflow support for privacy-rights intake: access, deletion, correction, erasure, portability, and consumer data requests.

The skill helps privacy, legal ops, support ops, and startup teams catch operational blockers before fulfillment:

- deadline due-soon or overdue checks;
- identity and authorized-agent verification gaps;
- system-inventory coverage gaps;
- export support and manual-export review needs;
- deletion support, retention lock, legal hold, and exception review;
- sensitive/minor data review routing;
- owner assignment across CRM, billing, support, warehouse, and marketing systems.

It does not give legal advice, decide whether a request may be denied, send responses, export data, or delete records.

## Quick Start

```bash
python3 scripts/dsar_request_preflight.py \
  --requests scripts/fixtures/requests.csv \
  --systems scripts/fixtures/systems.csv \
  --policy scripts/fixtures/policy.json \
  --today 2026-05-30
```

The fixture exits `2` because it intentionally contains high-risk blockers. In normal use, pass absolute paths from the repository root:

```bash
python3 dsar-request-preflight/scripts/dsar_request_preflight.py \
  --requests /absolute/path/requests.csv \
  --systems /absolute/path/systems.csv
```

## Inputs

Request intake fields:

- `request_id`
- `received_date`
- `requester`
- `jurisdiction`
- `request_type`
- `identity_status`
- `authorized_agent`
- `agent_proof`
- `scope`
- `match_keys`
- `sensitive_context`
- `notes`

System inventory fields:

- `system`
- `owner`
- `data_categories`
- `match_keys`
- `export_supported`
- `deletion_supported`
- `retention_lock`
- `legal_hold`
- `processor`

## Output

The script prints a Markdown report with:

- overall DSAR request decision;
- action summary;
- row-level request findings;
- request-to-owner routing;
- top flags and guardrails.

Use `templates/response-readiness-report.md` for a reusable packet.

## Runtime Notes

- Codex/OpenAI-style agents: use `SKILL.md` and `agents/openai.yaml`.
- Claude Code: copy `.claude/skills/dsar-request-preflight/SKILL.md` into your Claude skills folder.
- OpenClaw: see `openclaw/README.md`.
- Hermes: see `hermes/README.md`; native handler verification is blocked until the local Hermes spec is available.

## Safety

Run this only on redacted exports when possible. Do not paste credentials, tokens, SSNs, full payment data, or unrelated personal data into prompts or fixtures. The script reads explicit local paths and does not make network calls.
