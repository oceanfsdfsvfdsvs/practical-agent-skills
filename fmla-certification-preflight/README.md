# FMLA Certification Preflight

Check FMLA medical certification and leave paperwork before an employee, caregiver, HR partner, manager, union steward, clinic helper, or benefits advocate submits, cures, designates, or escalates a packet.

`fmla-certification-preflight` is a local-first agent skill for FMLA paperwork where a plain prompt often misses 15-day certification windows, seven-day cure rules, written incomplete/insufficient notices, provider-signature gaps, serious-health-condition fields, intermittent-leave frequency, eligibility-notice issues, and live-action boundaries.

## Use For

- FMLA medical certification packets, cure notices, HR deadline emails, eligibility notices, rights-and-responsibilities notices, and designation readiness checks.
- Leave requests involving an employee's own serious health condition, family-care leave, intermittent leave, reduced schedules, pregnancy/parental bonding documentation routing, and provider form completion.
- Evidence review before an employee, HR owner, leave administrator, attorney, union representative, clinic staff, or benefits advocate reviews the packet.
- Batch review of leave rows in CSV/JSON form plus local evidence folders.

## Why Use This Instead Of A Prompt

- Maps vague or missing certification fields to specific repair questions instead of generic FMLA advice.
- Separates deadline risk, eligibility review, cure-notice review, intermittent schedule repair, packet hold items, and live-action blockers.
- Requires written notice, provider signature/contact, incapacity/schedule, family relationship, designation, and delivery-proof checks.
- Runs a deterministic local fixture script with no credentials or network calls.

## Run

```bash
python3 fmla-certification-preflight/scripts/fmla_certification_preflight.py \
  --cases fmla-certification-preflight/scripts/fixtures/fmla_cases.csv \
  --evidence-dir fmla-certification-preflight/scripts/fixtures/evidence \
  --today 2026-06-16
```

## Runtime Notes

- Codex/OpenAI: use `SKILL.md` plus `agents/openai.yaml`.
- Claude Code: use `.claude/skills/fmla-certification-preflight/SKILL.md`.
- OpenClaw: see `openclaw/README.md`.
- Hermes: see `hermes/README.md`; native runtime verification is blocked until the current Hermes skill spec is confirmed.

No validation step requires HR portals, leave-administrator systems, medical provider portals, employer systems, government agency accounts, credentials, paid legal services, or network access.
