---
name: dsar-request-preflight
description: Triage data subject access, deletion, correction, and portability requests against identity, authority, deadline, system-inventory, export, deletion-exception, and owner-routing checks before a privacy team fulfills or responds.
---

# DSAR Request Preflight

Use this Claude Code mirror with the repository copy of `dsar-request-preflight/` available so relative script and fixture paths resolve.

Follow the canonical instructions in `dsar-request-preflight/SKILL.md`. Preserve the same safety boundaries:

- privacy-operations support only, not legal advice;
- no live export, deletion, portal action, or requester message without explicit authorization;
- redact secrets, credentials, full payment data, SSNs, and unrelated personal data;
- run `dsar-request-preflight/scripts/dsar_request_preflight.py` when local intake and system inventory paths are available;
- produce the DSAR request decision, action summary, row-level findings, owner routing, and guardrails.

Validation:

```bash
python3 dsar-request-preflight/scripts/dsar_request_preflight.py \
  --requests dsar-request-preflight/scripts/fixtures/requests.csv \
  --systems dsar-request-preflight/scripts/fixtures/systems.csv \
  --policy dsar-request-preflight/scripts/fixtures/policy.json \
  --today 2026-05-30
```
