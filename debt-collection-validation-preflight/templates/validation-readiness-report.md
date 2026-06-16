# Debt Collection Validation Preflight Report

Run date: {{run_date}}

## Debt Collection Validation Decision
{{decision}}

## Case Summary
| Case | Collector | Current Creditor | Issue Type | Decision |
|---|---|---|---|---|
| {{case_id}} | {{collector}} | {{current_creditor}} | {{issue_type}} | {{case_decision}} |

## Timeline
| Case | First Contact | Notice Received | Dispute Due | Dispute Sent | Status |
|---|---|---|---|---|---|
| {{case_id}} | {{first_contact}} | {{notice_received}} | {{dispute_due}} | {{dispute_sent}} | {{status}} |

## Evidence Matrix
| Case | Evidence | Status | Source | Repair action |
|---|---|---|---|---|
| {{case_id}} | {{evidence_name}} | {{status}} | {{source}} | {{repair_action}} |

## Blockers
| Case | Blocker | Why it matters | Next action |
|---|---|---|---|
| {{case_id}} | {{blocker}} | {{why_it_matters}} | {{next_action}} |

## Review Flags
| Case | Flag | Why it matters | Next action |
|---|---|---|---|
| {{case_id}} | {{flag}} | {{why_it_matters}} | {{next_action}} |

## Packet Notes

- State only facts supported by attached records.
- Identify the collector, current creditor, original creditor if known, masked account number, dates, disputed portions, requested validation, and attachments.
- Separate validation requests, disputes, original-creditor requests, complaint packets, and court/legal owner review.
- Label current-law, state-law, or lawsuit-response assumptions as "verify before send" unless the user supplied a current official source or counsel instruction.

## Do Not Upload

Full SSNs, full ID scans, bank/card credentials, full account numbers, private keys, tokens, `.env` files, or unrelated consumer records.
