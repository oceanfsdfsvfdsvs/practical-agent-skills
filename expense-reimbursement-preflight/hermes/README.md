# Hermes Runtime Notes

This skill is packaged as a Markdown skill plus a local Python validator. It does not include a Hermes-native `skill.yaml` or handler because the current local Hermes skill packaging contract has not been verified for this repository.

Status: `blocked-for-runtime-verification`

Use the skill content and local script as source material until Hermes native packaging is confirmed:

```bash
python3 expense-reimbursement-preflight/scripts/expense_reimbursement_preflight.py \
  --expenses expense-reimbursement-preflight/scripts/fixtures/expense_report.csv \
  --policy expense-reimbursement-preflight/scripts/fixtures/policy.json \
  --today 2026-05-26
```

Do not claim Hermes runtime success until the skill has been installed and inspected with the target Hermes CLI or documented runtime.
