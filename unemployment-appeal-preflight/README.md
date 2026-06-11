# Unemployment Appeal Preflight

Local-first skill for checking unemployment insurance denial, employer appeal, hearing, overpayment, misconduct, voluntary quit, able-and-available, and work-search appeal packets before filing, evidence exchange, or hearing preparation.

It helps users identify missing notices, deadlines, issue-specific evidence, witness readiness, exhibit exchange, weekly-certification continuity, and live-action boundaries without connecting to any agency portal.

## Run The Fixture

```bash
python3 unemployment-appeal-preflight/scripts/unemployment_appeal_preflight.py \
  --cases unemployment-appeal-preflight/scripts/fixtures/appeal_cases.csv \
  --evidence-dir unemployment-appeal-preflight/scripts/fixtures/evidence \
  --today 2026-06-12
```

The fixture intentionally exits `2` because it includes blocked packets.

## Inputs

CSV or JSON cases with fields such as:

- `case_id`, `party_role`, `state`, `appeal_stage`, `issue_type`
- `determination_date`, `appeal_deadline`, `hearing_date`
- `determination_notice`, `hearing_notice`, `hearing_packet`
- `claimant_statement`, `employer_evidence`, `separation_timeline`
- `policy_or_handbook`, `warning_or_writeup`, `firsthand_witness`, `witness_contact`
- `work_search_or_weekly_certification`, `medical_or_caregiver_evidence`, `good_cause_explanation`
- `evidence_exchanged_to_all_parties`, `language_access_or_accommodation`, `live_action_requested`

The optional evidence directory is matched by case ID and keywords in filenames.

## Output

The script prints a Markdown readiness report:

- decision
- appeal summary
- finding table
- hearing packet checklist
- guardrails

Exit code `0` means no blocker findings. Exit code `2` means at least one blocker needs owner review before filing or hearing.

## Safety

- No network calls.
- No hidden telemetry.
- No credentials required.
- Does not file appeals, upload evidence, contact agencies, contact employers, request subpoenas, join hearings, or send messages.
- Redact SSNs, claimant IDs, portal credentials, bank data, full medical details, and unrelated personal facts.
