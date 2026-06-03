# Deposit Dispute Rules

Use these rules as a local evidence checklist, not as legal advice. Always mark jurisdiction-specific conclusions as "verify locally" when the state, city, lease type, date rules, or current law is uncertain.

## Core Decision Axes

- **Deadline clock**: Identify move-out, key return, possession surrender, lease-end, and forwarding-address dates. Use the jurisdiction rule only after the triggering event is clear.
- **Itemized deductions**: If any money is withheld, require an itemized statement tied to specific damage, unpaid rent, lease charge, or allowed cost.
- **Normal wear-and-tear**: Flag routine painting, minor scuffs, ordinary carpet wear, light cleaning, and depreciation-like turnover as review items unless evidence shows tenant-caused damage beyond ordinary use.
- **Receipts and estimates**: For large or contested deductions, require receipts, invoices, estimates, or a clear good-faith estimate label when final invoices are unavailable.
- **Condition evidence**: Require move-in condition proof and move-out photos/videos. Missing move-in evidence weakens claims about pre-existing damage; missing move-out evidence weakens tenant rebuttals.
- **Forwarding address**: Treat written forwarding-address proof as material, especially where refund obligations depend on it.
- **Demand packet hygiene**: Use boring facts: dates, amounts, itemized lines, attachments, requested refund, deadline for response, and delivery method. Avoid threats and unsupported accusations.

## Jurisdiction Snapshot For Fixtures

The bundled script uses `scripts/fixtures/state_rules.json` as a small deterministic sample, not a full legal database.

- California sample rule: 21-day return/itemization deadline after possession is returned; itemized deductions and supporting receipts/estimates matter; ordinary wear-and-tear is not a valid deposit use; pre-move-out inspection can matter.
- New York sample rule: 14-day return/itemization deadline after vacating; itemized statement required for retained amounts; ordinary wear-and-tear deductions should be challenged.
- Texas sample rule: 30-day refund deadline, with forwarding-address proof material; normal wear-and-tear cannot be charged against the deposit.
- Massachusetts sample rule: 30-day return/itemization deadline; move-in condition statement, interest/account handling, and itemized damage list can be material.

For other states, use the script's generic review mode and ask the user to provide a current local rule source.

## Common Failure Modes

- Landlord sends a lump-sum cleaning or repair charge with no itemized basis.
- Statement arrives after the statutory window.
- Tenant never sent a forwarding address in writing.
- Photos exist but are not tied to room, date, or case.
- The packet lacks the lease, deposit receipt, or move-in condition checklist.
- Deductions mix unpaid rent, damages, utilities, cleaning, painting, and lease-break fees without separating legal bases.
- The user asks the agent to file in court or submit a government complaint without explicit live-action authorization.
