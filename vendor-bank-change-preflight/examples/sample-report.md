## Bank Change Decision

Hold bank-change updates: high-risk payment-redirection signals require independent verification.

## Request Findings

| Risk | Action | Row | Request | Vendor | Amount at risk | Flags | Reviewer next step |
|---|---|---:|---|---|---:|---|---|
| high | hold_change | 2 | BCR-1001 | Acme Medical Supplies | 188000.00 | bank_details_changed, callback_missing_or_incomplete, callback_used_untrusted_source, insufficient_dual_approval, request_arrived_outside_controlled_form, lookalike_email_domain, urgency_or_pressure_language, same_week_effective_date, large_payment_exposure, bank_account_reused_by_another_vendor | Do not update vendor bank details until independent callback, dual approval, and evidence are complete. |
| medium | secondary_verification | 4 | BCR-1003 | Blue Harbor Consulting | 52000.00 | bank_details_changed, insufficient_dual_approval, request_arrived_outside_controlled_form, bank_country_mismatch, missing_bank_letter, missing_w9_or_tax_record, first_payment_to_vendor, new_vendor_under_90_days, urgency_or_pressure_language, same_week_effective_date, large_payment_exposure | Route to a second reviewer and verify through a trusted contact source before releasing payment. |
| low | document_and_monitor | 3 | BCR-1002 | Northwind Facilities | 8200.00 | bank_details_changed, request_arrived_outside_controlled_form | Record the evidence trail and confirm all required artifacts before the next payment run. |

## Controls Checked

- Independent callback source, callback completion, and dual approval.
- Email-domain mismatch or lookalike domain against the vendor master.
- Bank country mismatch, reused bank details, new-vendor timing, and first-payment exposure.
- Missing bank letter or tax record, urgency language, and same-week effective dates.

## Safe Release Steps

1. Hold all `hold_change` rows outside the ERP or bank portal until a trusted-contact callback is complete.
2. Require a second internal approver for all bank-detail changes and high-value payments.
3. Archive the callback source, reviewer names, bank evidence, and request packet with the vendor record.
4. Re-run this preflight after evidence is corrected; do not rely on email-thread continuity as proof.
