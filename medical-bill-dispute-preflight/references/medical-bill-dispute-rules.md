# Medical Bill Dispute Rules

Use these rules before telling a user that a medical bill is ready to pay.

## Core Evidence

- A provider bill shows what the provider is asking the patient to pay.
- An EOB shows what the insurer processed, the allowed amount, plan payment, denial status, and patient responsibility.
- An itemized bill or superbill shows service dates, CPT/HCPCS, descriptions, quantities, and charges.
- A corrected claim or reprocessed EOB should replace older conflicting versions when the user confirms it is final.

## Hold Payment Triggers

- The bill balance is greater than the EOB patient responsibility for the same provider/date/CPT.
- A bill was received but no EOB is available and insurance should have been processed.
- The provider says insurance was not processed, member information was wrong, or a corrected claim is pending.
- The same provider/date/CPT/amount appears more than once without a clear separate claim.
- The statement is not itemized enough to verify what was charged.

## Reconciliation Triggers

- Provider, date of service, CPT/HCPCS, or patient responsibility differs between bill and EOB.
- A bill cites a gross charge after the EOB shows a lower allowed amount or lower patient responsibility.
- The provider has a bill but the insurer has no claim, or the insurer has a claim but the provider says no balance exists.

## Appeal Review Triggers

- EOB denial code, noncovered service, missing information, coordination-of-benefits issue, or prior authorization denial appears.
- The EOB says the patient owes the full charge because insurance denied the claim.
- The next step is to request the plan appeal procedure and evidence requirements, not to invent coverage arguments.

## Surprise-Billing Review Triggers

- Out-of-network emergency care.
- Out-of-network anesthesia, radiology, pathology, neonatology, assistant surgeon, hospitalist, intensivist, or lab services at an in-network facility.
- A provider bill exceeds the EOB cost sharing or looks like a balance bill.
- Route these to No Surprises Act or state insurance department review when facts fit; do not make legal conclusions.

## Financial Assistance Review Triggers

- The balance is unaffordable, high, or from a nonprofit hospital.
- The user has income hardship, Medicaid eligibility concerns, charity-care eligibility, or self-pay discount questions.
- Separate affordability negotiation from error correction; a bill can be correct and still need financial assistance screening.

## Privacy Guardrails

- Redact SSNs, full member IDs, full account numbers, card data, credentials, and unrelated clinical notes.
- Keep a call log with date, phone number, representative, reference number, promised action, and follow-up date.
- Ask for written confirmation before paying disputed balances or closing an appeal.
