---
name: credit-report-dispute-preflight
description: Preflight credit report error disputes before a consumer, caregiver, housing or financial counselor, benefits advocate, or legal-aid intake helper sends a bureau dispute, furnisher dispute, identity-theft packet, CFPB complaint, or follow-up letter. Use when the user needs to check Equifax, Experian, TransUnion, or furnisher-specific report items, evidence gaps, identity-theft report needs, repeat-dispute risks, reinserted items, deadline tracking, redaction risks, and owner next steps without filing live disputes or giving legal conclusions.
---

# Credit Report Dispute Preflight

Use the repository copy at `credit-report-dispute-preflight/SKILL.md` as the canonical workflow. Keep the full skill directory available so relative paths for `references/`, `templates/`, `examples/`, and `scripts/` resolve correctly.

Claude Code install check:

```bash
mkdir -p ~/.claude/skills
cp -R .claude/skills/credit-report-dispute-preflight ~/.claude/skills/
```

Smoke-test the local fixture from the repository root:

```bash
python3 credit-report-dispute-preflight/scripts/credit_report_dispute_preflight.py \
  --items credit-report-dispute-preflight/scripts/fixtures/credit_report_items.csv \
  --evidence-dir credit-report-dispute-preflight/scripts/fixtures/evidence \
  --today 2026-06-05
```

Expected result: a Markdown report with `Credit Report Dispute Decision`, at least one `Hold dispute packet pending evidence repair`, and blockers such as `identity_theft_report_missing`, `highlighted_report_page_missing`, `repeat_dispute_needs_new_evidence`, `reinserted_item_prior_deletion_missing`, and `live_action_requested`.
