# DSAR Preflight Rules

This reference is an operations checklist, not legal advice. Treat local counsel, privacy owner policy, and regulator guidance as the source of authority.

## Intake Completeness

Block or repair fulfillment when:

- received date is missing;
- request type is unclear;
- requester identity is not verified;
- authorized agent proof is absent or incomplete;
- jurisdiction or policy SLA is unknown;
- scope cannot be mapped to systems or match keys.

## Deadline Routing

Use the policy SLA map first. Defaults:

| Jurisdiction term | Default SLA used by fixture |
|---|---:|
| GDPR, EU, EEA, UK | 30 days |
| CCPA, CPRA, California | 45 days |
| Unknown | 30 days |

Flags:

- `response_deadline_overdue`: escalate immediately and document remediation.
- `response_deadline_due_soon`: prioritize verification, owner tasks, and response assembly.
- `complex_request_extension_review`: many scoped systems near the due-soon window; privacy owner should decide whether extension handling is appropriate.

## Identity And Authority

Do not disclose or delete data until verification is complete. Authorized-agent requests need proof before fulfillment. Use proportionate verification and avoid collecting more data than needed.

## System Coverage

Map the request scope and match keys to the inventory before claiming there is no responsive data. If no system matches, route to data owner review. If multiple owners match, assign owner tasks with due dates.

## Access And Portability

For access, portability, or copy requests:

- systems without export support need a manual export or no-export explanation;
- sensitive data needs redaction and reviewer approval;
- warehouse and support data often require owner review because they may contain other people data.

## Deletion And Erasure

For deletion or erasure requests:

- separate deletable systems from legal hold, retention lock, fraud, security, accounting, tax, and dispute exceptions;
- unsupported deletion needs a documented manual action, suppression, anonymization, or exception path;
- never mark "ready" until exception language is owner-approved.

## Output Requirements

Every report should include:

- decision;
- row-level findings;
- evidence;
- next step;
- owner routing;
- guardrails that no live export, deletion, or requester communication occurred.
