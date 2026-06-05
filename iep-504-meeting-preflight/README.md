# IEP/504 Meeting Preflight

Check IEP, Section 504, special education evaluation, accommodation, service-log, progress, or school meeting packets before a family, advocate, or school team attends a meeting or escalates a concern.

`iep-504-meeting-preflight` is a local-first agent skill for recurring school-support meetings where a plain prompt often misses current evaluations, prior plans, goal baselines, service logs, progress data, accommodation implementation evidence, consent/notice status, behavior or transition records, and privacy boundaries.

## Use For

- IEP annual reviews, reevaluations, eligibility meetings, service-change requests, and missed-service reviews.
- Section 504 meetings, accommodation implementation concerns, and records-readiness checks.
- Evaluation, reevaluation, behavior-support, manifestation, assistive-technology, transition, or progress-data packet review.
- Families, caregivers, advocates, school support helpers, and school teams preparing neutral meeting packets.

## Why Use This Instead Of A Prompt

- Maps each requested change to the specific school-record evidence needed before a meeting.
- Separates IEP, 504, evaluation, behavior/discipline, transition, and assistive-technology evidence gates.
- Flags stale evaluations, missing progress reports, missing service logs, vague goals, live-action requests, and sensitive-file risks.
- Runs a deterministic local fixture script with no credentials or network calls.

## Run

```bash
python3 iep-504-meeting-preflight/scripts/iep_504_meeting_preflight.py \
  --cases iep-504-meeting-preflight/scripts/fixtures/meeting_cases.csv \
  --evidence-dir iep-504-meeting-preflight/scripts/fixtures/evidence \
  --today 2026-06-06
```

## Runtime Notes

- Codex/OpenAI: use `SKILL.md` plus `agents/openai.yaml`.
- Claude Code: use `.claude/skills/iep-504-meeting-preflight/SKILL.md`.
- OpenClaw: see `openclaw/README.md`.
- Hermes: see `hermes/README.md`; native runtime verification is blocked until the current Hermes skill spec is confirmed.

No validation step requires school portals, SIS access, email sending, complaint filing, student credentials, paid advocate services, or network access.
