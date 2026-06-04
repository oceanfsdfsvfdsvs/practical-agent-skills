# Credit Report Dispute Preflight Report

Run date: {{run_date}}

## Credit Report Dispute Decision
{{decision}}

## Item Summary
| Item | Bureau | Furnisher | Error Type | Decision |
|---|---|---|---|---|
| {{item_id}} | {{bureau}} | {{furnisher}} | {{error_type}} | {{item_decision}} |

## Evidence Matrix
| Item | Evidence | Status | Source | Repair action |
|---|---|---|---|---|
| {{item_id}} | {{evidence_name}} | {{status}} | {{source}} | {{repair_action}} |

## Blockers
| Item | Blocker | Why it matters | Next action |
|---|---|---|---|
| {{item_id}} | {{blocker}} | {{why_it_matters}} | {{next_action}} |

## Review Flags
| Item | Flag | Why it matters | Next action |
|---|---|---|---|
| {{item_id}} | {{flag}} | {{why_it_matters}} | {{next_action}} |

## Packet Notes

- State only facts that are supported by attached records.
- Identify the bureau, furnisher, account label, report date, exact disputed field, requested correction, and attachments.
- Separate bureau disputes, furnisher disputes, identity-theft packets, and CFPB complaint follow-up.
- Label current-law and bureau-process assumptions as "verify before send" unless the user supplied a current official source.

## Do Not Upload

Full SSNs, full ID scans, account credentials, full card or bank numbers, private keys, tokens, `.env` files, or unrelated consumer records.
