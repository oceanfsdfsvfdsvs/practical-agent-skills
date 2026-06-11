---
name: unemployment-appeal-preflight
description: Review unemployment insurance denial, employer appeal, hearing, overpayment, misconduct, voluntary quit, able-and-available, work-search, or late-appeal packets before a claimant, employer, legal-aid intake helper, workforce navigator, or benefits advocate submits an appeal, prepares for a hearing, requests reopening, or organizes evidence. Use when the user needs deadline, issue, evidence-exchange, witness, hearing-packet, weekly-certification, and live-portal-action guardrails without giving legal advice or contacting an agency.
---

# Unemployment Appeal Preflight

This is a Claude Code mirror for the repository skill at `unemployment-appeal-preflight/SKILL.md`.

Install the full repository or keep the `unemployment-appeal-preflight` directory beside this mirror so relative paths to `references/`, `templates/`, `examples/`, and `scripts/` resolve correctly.

Core workflow:

1. Ask the user to redact SSNs, claimant IDs, portal credentials, bank data, full medical details, employer trade secrets, and unrelated personal data.
2. Read `unemployment-appeal-preflight/references/unemployment-appeal-rules.md`.
3. Run the local preflight when cases are available:

```bash
python3 unemployment-appeal-preflight/scripts/unemployment_appeal_preflight.py \
  --cases /absolute/path/appeal_cases.csv \
  --evidence-dir /absolute/path/evidence \
  --today 2026-06-12
```

4. Produce the Markdown decision report with findings, checklist, and guardrails.

Do not decide eligibility, predict hearing outcomes, file appeals, upload evidence, contact agencies, contact employers, request subpoenas, join hearings, or send portal messages. Prepare owner-reviewed evidence and questions only.
