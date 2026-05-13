# Security Questionnaire Response Rules

Use these rules when preparing customer security questionnaire responses.

## Domain Routing

| Domain | Typical Topics | Default Owner |
|---|---|---|
| identity_access | MFA, SSO, RBAC, provisioning, deprovisioning, password policy, privileged access | Security |
| encryption_key_management | TLS, encryption at rest, KMS, key rotation, cryptography | Infrastructure |
| logging_monitoring | audit logs, SIEM, alerting, monitoring, detection | Security operations |
| incident_response | incident process, breach notification, postmortem, escalation | Security and legal |
| vulnerability_management | scanning, patching, penetration tests, CVEs, remediation SLAs | Security |
| sdlc_change | code review, CI/CD, change management, release approval, secure SDLC | Engineering |
| data_privacy | PII, GDPR, CCPA, DPA, retention, deletion, data residency | Privacy and legal |
| subprocessors_vendor | subprocessors, cloud providers, suppliers, vendor reviews | GRC or legal |
| compliance_audit | SOC 2, ISO 27001, PCI, HIPAA, audit reports, certifications | GRC |
| business_continuity | backups, disaster recovery, RTO, RPO, availability, resilience | Infrastructure |
| physical_endpoint | office controls, laptops, MDM, endpoint protection | IT |
| network_infrastructure | firewalls, segmentation, VPN, IP ranges, architecture diagrams | Infrastructure |
| ai_governance | AI features, model training, customer data in AI systems, human review | Product and legal |
| legal_commercial | insurance, liability, indemnity, SLA, contract commitments | Legal |

## Answer Status Rules

| Status | Use When | Allowed Output |
|---|---|---|
| ready_with_cited_answer | Approved answer and current evidence both exist. | Draft answer plus evidence label and reviewer. |
| draft_needs_answer_owner | Current evidence exists, but no approved answer wording exists. | Bounded draft with owner approval required. |
| needs_evidence | The question is answerable, but no current approved evidence supports it. | Evidence request, owner, and blocking reason. |
| sme_or_legal_review | The answer may create a legal, privacy, regulated-data, AI, incident, or commercial commitment. | Reviewer route and suggested safe framing. |
| do_not_answer_in_sheet | The request asks for secrets, customer data, detailed network data, vulnerability details, raw logs, or private evidence. | "Available through approved channel under NDA" style note, if true. |
| not_applicable_candidate | The question appears outside product scope. | Proposed N/A explanation and owner confirmation. |

## Redaction Gates

Never place these directly in a worksheet or chat response:

- Credentials, tokens, keys, secrets, passwords, certificates, private URLs, or environment values.
- Customer data samples, employee lists, raw logs, support tickets, vulnerability scans, penetration-test details, or incident artifacts.
- Production IP ranges, firewall rules, network diagrams, detailed architecture diagrams, or cloud account identifiers.
- Unredacted SOC 2 reports, audit reports, DPAs, insurance certificates, subprocessors lists, or legal terms when the buyer lacks the approved sharing channel.

Use evidence labels, trust-center links, or "available under NDA through the approved channel" only when that is true and supported.

## Excel Intake Checklist

When the questionnaire arrives as `.xlsx`:

1. Preserve the original workbook as the source of truth.
2. Identify the specific worksheet and header row that contain buyer questions.
3. Export only the needed question sheet to CSV for script triage.
4. Keep row IDs, section labels, answer columns, required/optional markers, and due-date columns when present.
5. Do not answer from hidden sheets, comments, formulas, or attachments until they are inspected and summarized separately.
6. After drafting, map answers back to the workbook row IDs and keep high-risk rows in the reviewer queue.

Useful local conversion options:

- Spreadsheet app: open the workbook, select the target worksheet, and export/save that sheet as CSV.
- Python environment with spreadsheet libraries: convert the selected sheet to CSV, preserving cell text values and row numbers.
- If conversion tooling is unavailable, ask for a CSV export or pasted rows and mark the pass as sample-limited.

## Unsupported Claim Traps

Route for review or mark as needs evidence when a draft answer says:

- "Yes", "fully compliant", "always", "never", "guaranteed", "100%", or "all systems" without evidence.
- SOC 2 Type II, ISO 27001, HIPAA, PCI, GDPR, or data residency claims without a current report, legal basis, or scope statement.
- Encryption, key rotation, backup, deletion, retention, AI training, subprocessor, or incident notification claims without current owner-approved evidence.
- "N/A" when the product could process customer data, authentication data, production infrastructure, AI output, or regulated information.

## Buyer-Ready Language Patterns

Prefer:

- "Supported by [evidence label]; available under NDA through [channel]."
- "Implemented for [scope]; exceptions: [known boundary]."
- "Not currently implemented. Planned owner/date: [owner/date] if available."
- "Not applicable to [product/scope] because [specific reason]; confirm with [owner]."
- "We can provide a redacted summary through the trust center rather than placing detailed artifacts in the worksheet."

Avoid:

- Broad commitments that exceed the product scope.
- Copying old answers without checking evidence freshness.
- Mixing facts, future plans, and sales positioning in the same cell.
- Giving detailed security architecture or vulnerability information to satisfy a generic row.
