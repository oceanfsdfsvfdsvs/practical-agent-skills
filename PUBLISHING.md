# Publishing Checklist

Use this checklist before making the repository public or pushing a release branch.

## Local Gates

```bash
python3 quick_validate.py
python3 -m py_compile \
  ap-duplicate-payment-preflight/scripts/ap_duplicate_payment_preflight.py \
  chargeback-evidence-pack/scripts/chargeback_evidence_pack.py \
  csv-import-preflight/scripts/csv_import_preflight.py \
  feature-flag-debt-audit/scripts/feature_flag_debt_audit.py \
  flaky-ci-forensics/scripts/flaky_ci_forensics.py \
  security-questionnaire-triage/scripts/security_questionnaire_triage.py \
  quick_validate.py
find . -name .DS_Store -o -name __pycache__ -o -name '*.pyc' -o -name '.env'
```

The final `find` command should print nothing.

## GitHub Release Steps

```bash
git status --short
git remote -v
gh auth status
gh repo create practical-agent-skills --public --source=. --remote=origin --push
git ls-remote origin refs/heads/main
```

If the repository already exists, add the remote explicitly:

```bash
git remote add origin https://github.com/<owner>/practical-agent-skills.git
git push -u origin main
```

Do not push if validation fails, secrets are found, or the target repository is unclear.

## Launch Notes

Suggested repository description:

```text
Practical local-first agent skills for Codex, Claude Code, and OpenClaw.
```

Suggested topics:

```text
agent-skills codex claude-code openclaw ai-agents workflow-automation finance-devtools devtools
```
