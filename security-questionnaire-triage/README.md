# Security Questionnaire Triage

Local-first skill for triaging B2B security questionnaires into approved answers, evidence-backed drafts, and controlled-channel escalations.

## Use For

- Mapping questionnaire rows to security domains.
- Reusing approved answer-bank entries.
- Citing internal evidence labels without pasting private audit artifacts into the questionnaire.
- Marking unsupported or sensitive asks as not safe to answer in-sheet.

## Run

```bash
python3 security-questionnaire-triage/scripts/security_questionnaire_triage.py \
  security-questionnaire-triage/scripts/fixtures/security_questions.csv \
  --evidence-register security-questionnaire-triage/scripts/fixtures/evidence_register.csv \
  --answer-bank security-questionnaire-triage/scripts/fixtures/answer_bank.csv
```

## Runtime Notes

- Codex/OpenAI: use `SKILL.md` plus `agents/openai.yaml`.
- Claude Code: use `.claude/skills/security-questionnaire-triage/SKILL.md`.
- OpenClaw: see `openclaw/README.md`.
