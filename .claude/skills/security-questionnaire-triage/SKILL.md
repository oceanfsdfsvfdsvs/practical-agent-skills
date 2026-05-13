---
name: security-questionnaire-triage
description: Triage B2B security questionnaires into evidence-backed answers, escalation items, and safe non-answer labels.
---

# Security Questionnaire Triage

Use this mirror to invoke the repository skill at `security-questionnaire-triage/SKILL.md`.

## Workflow

1. Load the questionnaire, evidence register, and answer bank.
2. Run `security-questionnaire-triage/scripts/security_questionnaire_triage.py` when local CSVs exist.
3. Draft answers only from approved evidence or reusable answer-bank entries.
4. Mark sensitive, unsupported, or private-evidence requests for controlled-channel handling.

Keep the full repository available so relative script, template, and fixture paths resolve correctly.
