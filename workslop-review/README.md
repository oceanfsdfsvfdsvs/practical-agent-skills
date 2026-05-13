# Workslop Review

Prompt/rubric skill for reviewing vague AI-assisted work output before it wastes reviewer time or creates false confidence.

## Use For

- Status updates, analysis docs, research summaries, strategy notes, and handoffs.
- Finding missing context, unsupported claims, unclear owners, weak decisions, and generic AI filler.
- Producing a concise critique plus a more accountable rewrite.

## Validate Manually

Ask an agent to apply:

- `workslop-review/templates/review-rubric.md`
- `workslop-review/examples/bad-status-update.md`

Expected output should identify ambiguity, missing evidence, missing owner, unclear decision, and an improved rewrite.

## Runtime Notes

- Codex/OpenAI: use `SKILL.md` plus `agents/openai.yaml`.
- Claude Code: use `.claude/skills/workslop-review/SKILL.md`.
- OpenClaw: see `openclaw/README.md`.
