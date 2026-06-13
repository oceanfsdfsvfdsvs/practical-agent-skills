---
name: workers-comp-denial-preflight
description: Review workers' compensation claim denial, delayed care, medical causation, pre-existing condition, late reporting, employer dispute, hearing, or appeal packets before an injured worker, caregiver, HR partner, union steward, legal-aid intake helper, or claims advocate organizes evidence or seeks owner review. Use when the user needs denial-letter, deadline, medical-record, incident-report, witness, work-restriction, health-insurance-crossover, evidence-exchange, and live-action guardrails without giving legal advice or contacting an insurer, employer, agency, or court.
---

# Workers' Comp Denial Preflight

This is a Claude Code mirror for the repository skill at `workers-comp-denial-preflight/SKILL.md`.

Install the full repository or keep the `workers-comp-denial-preflight` directory beside this mirror so relative paths to `references/`, `templates/`, `examples/`, and `scripts/` resolve correctly.

Core workflow:

1. Ask the user to redact SSNs, claim numbers, portal credentials, full medical histories, health insurance IDs, bank data, tax identifiers, employer trade secrets, and unrelated personal data.
2. Read `workers-comp-denial-preflight/references/workers-comp-denial-rules.md`.
3. Run the local preflight when cases are available:

```bash
python3 workers-comp-denial-preflight/scripts/workers_comp_denial_preflight.py \
  --cases /absolute/path/workers_comp_cases.csv \
  --evidence-dir /absolute/path/evidence \
  --today 2026-06-14
```

4. Produce the Markdown decision report with findings, packet checklist, and guardrails.

Do not decide compensability, predict appeal outcomes, give legal or medical advice, file appeals, upload evidence, contact adjusters, contact employers, contact providers, contact agencies, contact courts, or send portal messages. Prepare owner-reviewed evidence and questions only.
