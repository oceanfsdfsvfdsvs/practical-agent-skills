# Medical Bill Dispute Preflight

Review patient medical bills against insurance EOBs before paying, disputing, appealing, or escalating a confusing balance.

This skill is for patients, caregivers, benefits advocates, HR benefits teams, and billing helpers who need a structured first pass over medical bills without logging into insurer or provider systems. It turns local bill/EOB exports into an action-oriented dispute packet.

## What It Catches

- Provider bill balances that exceed the EOB patient responsibility.
- Bills that arrived before an EOB or before insurance was processed.
- Duplicate provider/date/CPT/amount lines.
- Missing CPT/HCPCS, service dates, or itemized detail.
- EOB denial lines that may need appeal instructions.
- Emergency or facility-related out-of-network clues that should be reviewed under surprise-billing rules.
- High balances that should trigger financial-assistance, charity-care, self-pay, or payment-plan screening.

## Quick Start

```bash
python3 medical-bill-dispute-preflight/scripts/medical_bill_dispute_preflight.py \
  --bills medical-bill-dispute-preflight/scripts/fixtures/medical_bills.csv \
  --eob medical-bill-dispute-preflight/scripts/fixtures/eob.csv \
  --policy medical-bill-dispute-preflight/scripts/fixtures/policy.json
```

Input may be CSV or JSON. Preferred bill fields:

```text
bill_id, provider, service_date, cpt, description, charge, patient_balance,
insurance_processed, network_status, facility_type, itemized, notes
```

Preferred EOB fields:

```text
claim_id, provider, service_date, cpt, description, allowed_amount, plan_paid,
patient_responsibility, denial_code, denial_reason, network_status
```

## Output

The script produces a Markdown report with:

- Overall billing decision.
- Exception summary.
- Row-level billing exceptions.
- Dispute packet checklist.
- Privacy, authority, and medical/legal guardrails.

## Safety

- This is administrative and financial workflow support, not medical, legal, tax, credit-repair, or insurance-coverage advice.
- The script does not call provider portals, insurer portals, collection agencies, or government complaint systems.
- Do not paste uncensored PHI, full member IDs, SSNs, payment card numbers, credentials, secrets, or private legal advice into public prompts.
- Keep final payment, appeal, complaint, and legal decisions with the patient or authorized benefits owner.
