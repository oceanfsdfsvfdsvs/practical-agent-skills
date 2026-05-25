# Expense Reimbursement Preflight

Catch employee reimbursement exceptions before approval, payroll, or ERP export.

Expense platforms can capture receipts, but many small teams and mixed-tool workflows still send finance incomplete reports: missing receipts, duplicate uploads, meal expenses without attendees, mileage claims above policy, stale submissions, and uncoded rows. This skill packages a local-first review workflow plus a deterministic fixture script.

## What It Does

- Reads local CSV or JSON expense-report exports.
- Applies a local policy JSON for receipt thresholds, category limits, mileage rate, late submissions, and prohibited categories.
- Flags hold, manager-review, employee-correction, finance-review, and coding-review exceptions.
- Produces a Markdown report with row-level evidence and next steps.
- Avoids live expense-system changes, hidden network calls, and fraud conclusions.

## Run The Fixture

```bash
python3 expense-reimbursement-preflight/scripts/expense_reimbursement_preflight.py \
  --expenses expense-reimbursement-preflight/scripts/fixtures/expense_report.csv \
  --policy expense-reimbursement-preflight/scripts/fixtures/policy.json \
  --today 2026-05-26
```

The fixture exits `2` because it intentionally contains hold-level reimbursement exceptions.

## Input Format

Preferred CSV columns:

```text
report_id,employee,expense_date,submitted_date,category,merchant,amount,currency,receipt_id,receipt_attached,itemized_receipt,business_purpose,attendees,project,gl_code,miles,notes
```

JSON inputs may be a list of rows or an object containing `expenses`, `rows`, `claims`, or `report`.

## Runtime Notes

- Codex/OpenAI: use `SKILL.md` and `agents/openai.yaml`.
- Claude Code: use `.claude/skills/expense-reimbursement-preflight/SKILL.md`.
- OpenClaw: see `openclaw/README.md`.
- Hermes: native packaging is blocked until the runtime contract is verified; see `hermes/README.md`.
