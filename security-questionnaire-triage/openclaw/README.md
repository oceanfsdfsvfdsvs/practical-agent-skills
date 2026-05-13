# OpenClaw Notes

Install by copying the `security-questionnaire-triage/` directory into the OpenClaw workspace skills directory.

Suggested check when supported by your CLI:

```bash
openclaw skills check security-questionnaire-triage
```

The bundled local validation does not require network access:

```bash
python3 security-questionnaire-triage/scripts/security_questionnaire_triage.py \
  security-questionnaire-triage/scripts/fixtures/security_questions.csv \
  --evidence-register security-questionnaire-triage/scripts/fixtures/evidence_register.csv \
  --answer-bank security-questionnaire-triage/scripts/fixtures/answer_bank.csv
```
