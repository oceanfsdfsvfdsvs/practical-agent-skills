# Practical Agent Skills

[English](README.md) | [简体中文](README.zh-CN.md)

Local-first agent skills for real work where a plain prompt is too inconsistent: finance controls, invoice matching, customer escalations, access offboarding, contract renewals, SaaS license rightsizing, security questionnaires, CI forensics, import checks, feature-flag cleanup, UTM governance, and AI work review.

Each skill is designed to be:

- **Useful in a real workflow**: selected for recurring pain, cost, risk, or review burden.
- **Safer than a generic prompt**: includes rules, templates, fixtures, scripts, or guardrails.
- **Portable across agent runtimes**: Codex/OpenAI-style metadata, Claude Code mirrors where available, and OpenClaw install notes.
- **Open-source friendly**: no required secrets, hidden telemetry, or live SaaS/API calls for local validation.

## Skills

| Skill | Best For | What It Produces | Validation |
|---|---|---|---|
| [`ap-duplicate-payment-preflight`](ap-duplicate-payment-preflight/SKILL.md) | AP teams reviewing payment runs before ACH/wire/check release. | Duplicate-payment exception report with hold/review rows. | Fixture script covered by `quick_validate.py`. |
| [`chargeback-evidence-pack`](chargeback-evidence-pack/SKILL.md) | Merchants assembling dispute evidence packs. | Reason-coded evidence inventory and challenge recommendation. | Fixture script covered by `quick_validate.py`. |
| [`contract-renewal-risk-preflight`](contract-renewal-risk-preflight/SKILL.md) | Procurement, finance, IT, and ops teams reviewing vendor renewals before cancellation windows pass. | Auto-renewal risk report, notice deadlines, owner actions. | Fixture script covered by `quick_validate.py`. |
| [`customer-escalation-timeline`](customer-escalation-timeline/SKILL.md) | Support, CS, CX, and engineering escalation teams reconstructing customer handoffs before closure or executive review. | Escalation timeline, handoff packet, owner/SLA/customer-update closure gates. | Fixture script covered by `quick_validate.py`. |
| [`csv-import-preflight`](csv-import-preflight/SKILL.md) | Ops/CS teams importing CSV/TSV data into SaaS/admin tools. | Block/review/pass import report with risky rows. | Fixture script covered by `quick_validate.py`. |
| [`employee-offboarding-access-preflight`](employee-offboarding-access-preflight/SKILL.md) | IT, security, HR ops, MSPs, and compliance owners closing departure or role-change access reviews. | Lingering access, direct-login SaaS, session/MFA, secret, group, and device closure-gate report. | Fixture script covered by `quick_validate.py`. |
| [`feature-flag-debt-audit`](feature-flag-debt-audit/SKILL.md) | Engineering teams cleaning stale feature flags. | Cleanup candidates, guardrails, code references, tickets. | Fixture script covered by `quick_validate.py`. |
| [`flaky-ci-forensics`](flaky-ci-forensics/SKILL.md) | Engineering teams triaging intermittent CI/test failures. | Failure cluster, flake confidence, cost estimate, fix plan. | Fixture script covered by `quick_validate.py`. |
| [`invoice-three-way-match-preflight`](invoice-three-way-match-preflight/SKILL.md) | AP, procurement, receiving, and ops teams reviewing invoice/PO/receipt mismatches before payment release. | Three-way match exception report with hold/route rows and owner-specific next steps. | Fixture script covered by `quick_validate.py`. |
| [`saas-license-rightsize`](saas-license-rightsize/SKILL.md) | IT, finance, procurement, MSP, and ops teams auditing SaaS seats before renewals or budget reviews. | Reclaim, downgrade, duplicate-account, stale-admin, and owner-review plan with savings estimate. | Fixture script covered by `quick_validate.py`. |
| [`security-questionnaire-triage`](security-questionnaire-triage/SKILL.md) | B2B teams answering security questionnaires. | Evidence-backed answer draft and escalation labels. | Fixture script covered by `quick_validate.py`. |
| [`utm-governance-preflight`](utm-governance-preflight/SKILL.md) | Marketing ops, growth, RevOps, analytics, and agency teams reviewing campaign links before launch or reporting freeze. | UTM launch-gate report with missing parameter, alias, source/medium swap, naming drift, and sensitive-label fixes. | Fixture script covered by `quick_validate.py`. |
| [`vendor-bank-change-preflight`](vendor-bank-change-preflight/SKILL.md) | Finance, AP, accounting, and procurement teams reviewing supplier bank-detail changes before payment. | Payment-redirection risk report with hold/verify/release actions. | Fixture script covered by `quick_validate.py`. |
| [`workslop-review`](workslop-review/SKILL.md) | Managers and ICs reviewing vague AI-assisted work output. | Rubric-based critique and accountable rewrite. | Prompt/workflow skill; no script required. |

## Standalone Repositories

These focused repos have their own audience-specific landing pages:

- [`ap-duplicate-payment-preflight`](https://github.com/oceanfsdfsvfdsvs/ap-duplicate-payment-preflight): catch duplicate vendor payments before release.
- [`chargeback-evidence-pack`](https://github.com/oceanfsdfsvfdsvs/chargeback-evidence-pack): assemble merchant dispute evidence packs.
- [`flaky-ci-forensics`](https://github.com/oceanfsdfsvfdsvs/flaky-ci-forensics): turn flaky CI failures into triage reports.
- [`feature-flag-debt-audit`](https://github.com/oceanfsdfsvfdsvs/feature-flag-debt-audit): clean stale feature flags without deleting guardrails.

## Quick Start

Clone or copy this repository, then validate the local fixtures:

```bash
python3 quick_validate.py
```

Use one skill by pointing your agent at its `SKILL.md`:

```text
Use the flaky-ci-forensics skill on this JUnit XML, CI log, and history CSV.
```

For script-backed skills, run the bundled local tool first and paste or attach the output to your agent:

```bash
python3 ap-duplicate-payment-preflight/scripts/ap_duplicate_payment_preflight.py \
  --payments ap-duplicate-payment-preflight/scripts/fixtures/ap_payments.csv
```

## Runtime Install

### Codex / OpenAI-Style Agents

Copy any skill directory into your configured skills folder, or reference the repository path directly when your agent supports local skills. Each skill has:

- `SKILL.md`
- `agents/openai.yaml`
- Optional `scripts/`, `templates/`, `references/`, `examples/`, and runtime notes.

### Claude Code

Claude Code can use the mirrored files under `.claude/skills/<skill-name>/SKILL.md`. To install all mirrors:

```bash
mkdir -p ~/.claude/skills
cp -R .claude/skills/* ~/.claude/skills/
```

For script-backed skills, keep the full repository available so relative script paths resolve correctly.

### OpenClaw

Copy the skill directories into your OpenClaw workspace skills directory. Each skill has either an `openclaw/README.md` or can be installed as a plain Markdown skill directory.

Suggested local check, when supported by your OpenClaw CLI:

```bash
openclaw skills check <skill-name>
```

If your OpenClaw version requires a registry URL or ClawHub package, use this repository as source material until packaging support is configured.

## Compatibility Matrix

| Skill | Codex/OpenAI | Claude Code | OpenClaw | Local Script |
|---|---|---|---|---|
| `ap-duplicate-payment-preflight` | `SKILL.md`, `agents/openai.yaml` | Mirror bundled | Install notes bundled | Yes |
| `chargeback-evidence-pack` | `SKILL.md`, `agents/openai.yaml` | Mirror bundled | Install notes bundled | Yes |
| `contract-renewal-risk-preflight` | `SKILL.md`, `agents/openai.yaml` | Mirror bundled | Install notes bundled | Yes |
| `customer-escalation-timeline` | `SKILL.md`, `agents/openai.yaml` | Mirror bundled | Install notes bundled | Yes |
| `csv-import-preflight` | `SKILL.md`, `agents/openai.yaml` | Mirror bundled | Install notes bundled | Yes |
| `employee-offboarding-access-preflight` | `SKILL.md`, `agents/openai.yaml` | Mirror bundled | Install notes bundled | Yes |
| `feature-flag-debt-audit` | `SKILL.md`, `agents/openai.yaml` | Mirror bundled | Install notes bundled | Yes |
| `flaky-ci-forensics` | `SKILL.md`, `agents/openai.yaml` | Mirror bundled | Install notes bundled | Yes |
| `invoice-three-way-match-preflight` | `SKILL.md`, `agents/openai.yaml` | Mirror bundled | Install notes bundled | Yes |
| `saas-license-rightsize` | `SKILL.md`, `agents/openai.yaml` | Mirror bundled | Install notes bundled | Yes |
| `security-questionnaire-triage` | `SKILL.md`, `agents/openai.yaml` | Mirror bundled | Install notes bundled | Yes |
| `utm-governance-preflight` | `SKILL.md`, `agents/openai.yaml` | Mirror bundled | Install notes bundled | Yes |
| `vendor-bank-change-preflight` | `SKILL.md`, `agents/openai.yaml` | Mirror bundled | Install notes bundled | Yes |
| `workslop-review` | `SKILL.md`, `agents/openai.yaml` | Mirror bundled | Install notes bundled | No, prompt workflow |

## Repository Validation

Run all bundled smoke checks:

```bash
python3 quick_validate.py
python3 -m py_compile \
  ap-duplicate-payment-preflight/scripts/ap_duplicate_payment_preflight.py \
  chargeback-evidence-pack/scripts/chargeback_evidence_pack.py \
  contract-renewal-risk-preflight/scripts/contract_renewal_risk_preflight.py \
  customer-escalation-timeline/scripts/customer_escalation_timeline.py \
  csv-import-preflight/scripts/csv_import_preflight.py \
  employee-offboarding-access-preflight/scripts/employee_offboarding_access_preflight.py \
  feature-flag-debt-audit/scripts/feature_flag_debt_audit.py \
  flaky-ci-forensics/scripts/flaky_ci_forensics.py \
  invoice-three-way-match-preflight/scripts/invoice_three_way_match_preflight.py \
  saas-license-rightsize/scripts/saas_license_rightsize.py \
  security-questionnaire-triage/scripts/security_questionnaire_triage.py \
  utm-governance-preflight/scripts/utm_governance_preflight.py \
  vendor-bank-change-preflight/scripts/vendor_bank_change_preflight.py \
  quick_validate.py
```

The checks use only local fixtures and do not require credentials or network access.

## Safety

- No bundled validation requires secrets.
- Do not paste tokens, private keys, `.env` values, full card data, raw customer data, or private audit evidence into prompts or fixtures.
- Scripts read explicit input paths and write reports only when the caller supplies an output path.
- Skills do not make hidden network calls or modify live SaaS/accounting/CI systems.

## Contributing

High-value skills should solve a recurring real workflow where a generic prompt is unreliable. A new skill should include a clear trigger, non-use cases, guardrails, examples, and at least one durable asset such as a script, rubric, template, checklist, taxonomy, fixture, or reference rule file.
