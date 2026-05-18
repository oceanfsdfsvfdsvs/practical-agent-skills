# Bank Change Control Rules

## Evidence That Can Support A Change

- Independent callback completed using a trusted contact source from the vendor master, contract, procurement record, prior verified invoice, or known relationship owner.
- Two internal approvers for bank-detail changes, especially high-value payments or first payments.
- Bank letter, voided check, portal confirmation, or equivalent evidence supplied through a controlled intake process.
- Vendor tax or onboarding record matches the vendor record being changed.
- Request and approval trail archived with the vendor record outside the prompt transcript.

## High-Risk Signals

- Callback is missing, incomplete, or performed using the phone/email supplied in the change request.
- Sender domain is a lookalike of the trusted vendor domain.
- New bank details are reused by a different vendor.
- Request arrives as an urgent email, invoice attachment, or thread reply outside the controlled intake process.
- Request asks for same-day or next-day payment after changing bank details.

## Medium-Risk Signals

- Sender domain differs from the trusted vendor domain.
- Vendor country and bank country do not match.
- First payment to a vendor or vendor created in the last 90 days.
- Only one internal approver reviewed the change.
- Missing bank letter, W-9/tax record, or equivalent evidence.
- Large payment exposure is tied to the change.

## Common Failure Modes

- Treating a real email thread as proof that the sender is still safe.
- Calling the phone number in the request email or attachment instead of a trusted source.
- Updating the vendor master before evidence is complete, then letting normal payment approvals carry the bad record forward.
- Assuming a small first payment is harmless when it establishes attacker-controlled remittance details.
- Skipping dual approval because a manager or vendor says the payment is urgent.

## Reviewer Rule

When evidence is incomplete, preserve the vendor relationship and payment deadline by saying what is needed next:

1. Hold the bank-detail update outside the ERP or bank portal.
2. Complete callback using an independent trusted source.
3. Add second internal approval.
4. Archive evidence and rerun the preflight.
