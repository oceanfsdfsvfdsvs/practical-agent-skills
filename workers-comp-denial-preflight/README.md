# Workers' Comp Denial Preflight

Check workers' compensation denial and appeal packets before an injured worker, caregiver, HR partner, union steward, clinic helper, legal-aid intake helper, or claims advocate organizes evidence or seeks owner review.

`workers-comp-denial-preflight` is a local-first agent skill for denied or disputed workers' comp claims where a plain prompt often misses denial-letter details, appeal deadlines, medical causation evidence, incident reports, employer dispute records, work restrictions, health-insurance crossover issues, evidence exchange, and live-action boundaries.

## Use For

- Claim denials, disputed treatment authorization, wage-loss disputes, employer disputes, hearing packets, and appeal readiness checks.
- Denial reasons involving late notice, work-relatedness, pre-existing condition, medical necessity, IME, missing records, or incomplete forms.
- Evidence review before an owner, attorney, union representative, ombuds office, state information unit, or claims advocate reviews the packet.
- Batch review of claim rows in CSV/JSON form plus local evidence folders.

## Why Use This Instead Of A Prompt

- Maps denial reasons to specific evidence gaps instead of producing generic appeal advice.
- Separates deadline risk, medical causation, employer dispute, billing crossover, evidence exchange, and live-action blockers.
- Requires denial-letter, incident-report, provider-record, restriction, witness, bill/EOB, and delivery-proof checks.
- Runs a deterministic local fixture script with no credentials or network calls.

## Run

```bash
python3 workers-comp-denial-preflight/scripts/workers_comp_denial_preflight.py \
  --cases workers-comp-denial-preflight/scripts/fixtures/workers_comp_cases.csv \
  --evidence-dir workers-comp-denial-preflight/scripts/fixtures/evidence \
  --today 2026-06-14
```

## Runtime Notes

- Codex/OpenAI: use `SKILL.md` plus `agents/openai.yaml`.
- Claude Code: use `.claude/skills/workers-comp-denial-preflight/SKILL.md`.
- OpenClaw: see `openclaw/README.md`.
- Hermes: see `hermes/README.md`; native runtime verification is blocked until the current Hermes skill spec is confirmed.

No validation step requires insurer portals, employer systems, state agency accounts, medical provider portals, credentials, paid legal services, or network access.
