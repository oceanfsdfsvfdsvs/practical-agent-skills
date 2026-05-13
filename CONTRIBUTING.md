# Contributing

This repository favors a small set of high-value, reviewable skills over a large catalog of generic prompts.

## Acceptance Bar

A skill should be added only when it meets most of these conditions:

- The pain is real, repeated, and tied to time, money, quality, risk, or trust.
- A plain prompt would be inconsistent or unsafe.
- The skill includes durable assets: rules, scripts, templates, fixtures, examples, checklists, or rubrics.
- Local validation does not require secrets or external services.
- Failure modes and non-use cases are explicit.

## Required Files

Each new skill should include:

- `SKILL.md`
- `agents/openai.yaml`
- `README.md` when the skill includes scripts or runtime notes
- `references/`, `templates/`, `examples/`, or `scripts/fixtures/` when they materially improve repeatability
- `.claude/skills/<skill-name>/SKILL.md` mirror or clear Claude Code install notes
- `openclaw/README.md` when OpenClaw-specific verification is not automated

## Checks

Run:

```bash
python3 quick_validate.py
```

If you add or change Python scripts, also run `python3 -m py_compile` on the edited files.

Do not commit `.env`, credentials, tokens, raw customer data, `.DS_Store`, `__pycache__`, or `.pyc` files.
