#!/usr/bin/env python3
"""Preflight prior authorization denial appeal packets before submission."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path


TRUE_VALUES = {"1", "true", "yes", "y", "present", "available", "complete", "signed"}
FALSE_VALUES = {"0", "false", "no", "n", "missing", "none", "unknown", ""}
DENIAL_REASON_ALIASES = {
    "medical necessity": "medical_necessity",
    "not medically necessary": "medical_necessity",
    "med necessity": "medical_necessity",
    "step therapy": "step_therapy",
    "fail first": "step_therapy",
    "missing information": "missing_information",
    "incomplete documentation": "missing_information",
    "code mismatch": "coding_or_site_mismatch",
    "cpt mismatch": "coding_or_site_mismatch",
    "site of service": "coding_or_site_mismatch",
    "out of network": "network_or_referral",
    "referral missing": "network_or_referral",
    "quantity limit": "quantity_or_dose_limit",
    "dose limit": "quantity_or_dose_limit",
    "continuation": "continuation_or_renewal",
    "renewal": "continuation_or_renewal",
}
EVIDENCE_KEYWORDS = {
    "denial_letter": ("denial", "adverse", "notice", "letter"),
    "medical_records": ("record", "chart", "clinical", "note", "visit"),
    "letter_of_medical_necessity": ("medical_necessity", "lmn", "letter_of_medical", "necessity"),
    "payer_criteria": ("criteria", "policy", "guideline", "coverage"),
    "step_therapy_trials": ("step", "trial", "failed", "alternative"),
    "contraindications_documented": ("contraindication", "intolerance", "allergy"),
    "objective_results": ("lab", "imaging", "score", "result", "test"),
    "representative_authorization": ("representative", "authorization", "poa", "consent"),
    "urgency_attestation": ("urgent", "expedited", "attestation", "safety"),
    "peer_to_peer": ("peer", "p2p"),
}


@dataclass(frozen=True)
class Case:
    row_number: int
    case_id: str
    patient_role: str
    plan_type: str
    stage: str
    service_type: str
    requested_service: str
    diagnosis_code: str
    procedure_code: str
    denial_reason: str
    denial_date: date | None
    appeal_deadline: date | None
    urgent: bool
    fields: dict[str, str]


@dataclass(frozen=True)
class Finding:
    case: Case
    severity: str
    action: str
    flag: str
    evidence: str
    next_step: str


def norm(value: object) -> str:
    return " ".join(str(value or "").strip().lower().replace("-", "_").split())


def truthy(value: object) -> bool:
    raw = norm(value)
    if raw in TRUE_VALUES:
        return True
    if raw in FALSE_VALUES:
        return False
    return bool(raw)


def parse_date(value: object) -> date | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    return None


def load_rows(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        raise SystemExit(f"Input file not found: {path}")
    if path.suffix.lower() == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            for key in ("cases", "appeals", "rows"):
                if isinstance(payload.get(key), list):
                    return list(payload[key])
            raise SystemExit("JSON input must contain cases, appeals, or rows.")
        if isinstance(payload, list):
            return list(payload)
        raise SystemExit("JSON input must be a list or an object containing rows.")
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def parse_cases(path: Path) -> list[Case]:
    cases: list[Case] = []
    for offset, raw in enumerate(load_rows(path), start=2):
        row = {str(key).strip().lower(): str(value or "").strip() for key, value in dict(raw).items()}
        case_id = row.get("case_id") or row.get("appeal_id") or row.get("request_id") or f"row-{offset}"
        denial_reason = classify_denial_reason(row.get("denial_reason") or row.get("reason") or "")
        cases.append(
            Case(
                row_number=offset,
                case_id=case_id,
                patient_role=norm(row.get("patient_role") or row.get("requester_role") or "patient"),
                plan_type=norm(row.get("plan_type") or row.get("coverage_type")),
                stage=norm(row.get("stage") or row.get("request_stage") or "appeal"),
                service_type=norm(row.get("service_type") or row.get("category")),
                requested_service=row.get("requested_service") or row.get("service") or "",
                diagnosis_code=row.get("diagnosis_code") or row.get("icd10") or row.get("dx") or "",
                procedure_code=row.get("procedure_code") or row.get("cpt_hcpcs_ndc") or row.get("code") or "",
                denial_reason=denial_reason,
                denial_date=parse_date(row.get("denial_date")),
                appeal_deadline=parse_date(row.get("appeal_deadline") or row.get("deadline")),
                urgent=truthy(row.get("urgent") or row.get("expedited")),
                fields=row,
            )
        )
    if not cases:
        raise SystemExit("No prior authorization appeal cases found.")
    return cases


def classify_denial_reason(raw: str) -> str:
    clean = norm(raw).replace("_", " ")
    for needle, label in DENIAL_REASON_ALIASES.items():
        if needle in clean:
            return label
    return norm(raw) or "unknown"


def collect_evidence(evidence_dir: Path | None) -> dict[str, list[str]]:
    if not evidence_dir:
        return {}
    if not evidence_dir.exists():
        raise SystemExit(f"Evidence directory not found: {evidence_dir}")
    evidence: dict[str, list[str]] = {}
    for path in evidence_dir.rglob("*"):
        if path.is_file():
            evidence.setdefault(path.name.lower(), []).append(str(path.relative_to(evidence_dir)))
    return evidence


def has_field_or_evidence(case: Case, key: str, evidence: dict[str, list[str]]) -> bool:
    if truthy(case.fields.get(key, "")):
        return True
    case_id = case.case_id.lower()
    for filename in evidence:
        if case_id not in filename:
            continue
        if any(keyword in filename for keyword in EVIDENCE_KEYWORDS.get(key, ())):
            return True
    return False


def evidence_list(case: Case, evidence: dict[str, list[str]]) -> str:
    case_id = case.case_id.lower()
    matched = [name for name in sorted(evidence) if case_id in name]
    return ", ".join(matched[:4]) if matched else "no matching local evidence files"


def add(
    findings: list[Finding],
    case: Case,
    severity: str,
    action: str,
    flag: str,
    evidence: str,
    next_step: str,
) -> None:
    findings.append(Finding(case, severity, action, flag, evidence, next_step))


def analyze_case(case: Case, evidence: dict[str, list[str]], today: date) -> list[Finding]:
    findings: list[Finding] = []
    local_evidence = evidence_list(case, evidence)

    if not has_field_or_evidence(case, "denial_letter", evidence):
        add(
            findings,
            case,
            "blocker",
            "hold_appeal",
            "missing_denial_letter",
            local_evidence,
            "Get the written denial/adverse determination with reason, deadline, and appeal instructions.",
        )

    if case.appeal_deadline is None:
        add(
            findings,
            case,
            "review",
            "deadline_triage",
            "missing_appeal_deadline",
            "No appeal_deadline provided.",
            "Read the denial letter or plan appeal section and enter the deadline before drafting.",
        )
    else:
        days_left = (case.appeal_deadline - today).days
        if days_left < 0:
            add(
                findings,
                case,
                "blocker",
                "deadline_escalation",
                "appeal_deadline_passed",
                f"Deadline {case.appeal_deadline.isoformat()} is {abs(days_left)} days past {today.isoformat()}.",
                "Ask the plan about late appeal, grievance, external review, or provider resubmission options.",
            )
        elif days_left <= 7:
            add(
                findings,
                case,
                "review",
                "deadline_escalation",
                "appeal_deadline_within_7_days",
                f"Deadline {case.appeal_deadline.isoformat()} is {days_left} days away.",
                "Use an owner/date checklist and avoid waiting for nonessential materials.",
            )

    if case.patient_role not in {"patient", "member", "self"} and not has_field_or_evidence(
        case, "representative_authorization", evidence
    ):
        add(
            findings,
            case,
            "blocker",
            "authorization_needed",
            "representative_authorization_missing",
            f"Requester role is {case.patient_role or 'unknown'}.",
            "Collect signed representative authorization before sending appeal materials.",
        )

    if not case.denial_reason or case.denial_reason == "unknown":
        add(
            findings,
            case,
            "blocker",
            "reason_mapping",
            "denial_reason_unknown",
            "Denial reason is missing or unmapped.",
            "Map the denial to medical necessity, step therapy, missing information, coding/site, network, or quantity limit.",
        )

    if not has_field_or_evidence(case, "payer_criteria", evidence):
        add(
            findings,
            case,
            "review",
            "criteria_mapping",
            "missing_payer_criteria_mapping",
            "No payer criteria/policy evidence found.",
            "Attach the plan criteria or quote the denial-specific criteria and map every requirement to evidence.",
        )

    if case.denial_reason in {"medical_necessity", "missing_information", "continuation_or_renewal"}:
        if not has_field_or_evidence(case, "medical_records", evidence):
            add(
                findings,
                case,
                "blocker",
                "evidence_repair",
                "medical_records_missing",
                local_evidence,
                "Attach relevant chart notes, history, prior treatments, and provider assessment.",
            )
        if not has_field_or_evidence(case, "letter_of_medical_necessity", evidence):
            add(
                findings,
                case,
                "blocker",
                "evidence_repair",
                "missing_letter_of_medical_necessity",
                local_evidence,
                "Prepare a provider-signed letter tying diagnosis, requested service, criteria, and risk of delay.",
            )
        if not has_field_or_evidence(case, "objective_results", evidence) and case.service_type in {
            "imaging",
            "procedure",
            "therapy",
            "dme",
        }:
            add(
                findings,
                case,
                "review",
                "evidence_repair",
                "objective_support_missing",
                local_evidence,
                "Add labs, imaging, functional scores, therapy notes, or exam findings that support necessity.",
            )

    step_required = truthy(case.fields.get("step_therapy_required", "")) or case.denial_reason == "step_therapy"
    if step_required:
        if not has_field_or_evidence(case, "step_therapy_trials", evidence) and not truthy(
            case.fields.get("failed_alternatives_documented", "")
        ):
            add(
                findings,
                case,
                "blocker",
                "step_therapy_repair",
                "missing_step_therapy_documentation",
                local_evidence,
                "List required alternatives, trial dates, outcomes, failures, intolerance, or contraindications.",
            )
        if truthy(case.fields.get("contraindication_claimed", "")) and not has_field_or_evidence(
            case, "contraindications_documented", evidence
        ):
            add(
                findings,
                case,
                "blocker",
                "step_therapy_repair",
                "contraindication_not_documented",
                local_evidence,
                "Attach prior adverse reaction, allergy, interaction, or clinician contraindication documentation.",
            )

    if case.denial_reason == "coding_or_site_mismatch" or truthy(case.fields.get("quantity_or_site_mismatch", "")):
        add(
            findings,
            case,
            "review",
            "coding_site_reconciliation",
            "code_site_quantity_reconciliation_needed",
            f"Code/service: {case.procedure_code or 'missing'} / {case.requested_service or 'missing'}.",
            "Reconcile requested CPT/HCPCS/NDC, units, site of service, provider type, and scheduled date.",
        )

    if truthy(case.fields.get("prior_appeal_rejected", "")) and not truthy(case.fields.get("addresses_rejection_reason", "")):
        add(
            findings,
            case,
            "blocker",
            "rejection_repair",
            "repeat_appeal_does_not_address_rejection",
            "Prior appeal rejected and current packet does not address the rejection reason.",
            "Add a rejection-specific response table before resubmitting.",
        )

    if case.urgent or truthy(case.fields.get("patient_safety_risk", "")):
        if not has_field_or_evidence(case, "urgency_attestation", evidence):
            add(
                findings,
                case,
                "review",
                "expedited_review_check",
                "expedited_support_missing",
                "Urgent/expedited flag is set without a supporting attestation.",
                "Ask the treating clinician whether an expedited appeal statement is clinically appropriate.",
            )

    if truthy(case.fields.get("peer_to_peer_requested", "")) and not has_field_or_evidence(case, "peer_to_peer", evidence):
        add(
            findings,
            case,
            "review",
            "peer_to_peer_log",
            "peer_to_peer_not_logged",
            "Peer-to-peer requested but no local outcome/log found.",
            "Record date, reviewer, topics discussed, outcome, and documents requested.",
        )

    if truthy(case.fields.get("live_portal_action_requested", "")):
        add(
            findings,
            case,
            "blocker",
            "manual_owner_action",
            "live_portal_action_requested",
            "Input requested a live portal action.",
            "Do not submit portal messages or appeals from this skill; prepare the packet for authorized owner review.",
        )

    return findings


def render_report(cases: list[Case], findings: list[Finding], today: date) -> str:
    blockers = [item for item in findings if item.severity == "blocker"]
    reviews = [item for item in findings if item.severity == "review"]
    if blockers:
        decision = "Hold appeal pending evidence repair"
    elif reviews:
        decision = "Review before submission"
    else:
        decision = "Packet appears ready for authorized owner review"

    by_case: dict[str, list[Finding]] = {}
    for finding in findings:
        by_case.setdefault(finding.case.case_id, []).append(finding)

    lines = [
        "## Prior Authorization Appeal Decision",
        decision,
        "",
        "## Appeal Summary",
        f"- Review date: {today.isoformat()}",
        f"- Cases reviewed: {len(cases)}",
        f"- Blockers: {len(blockers)}",
        f"- Review items: {len(reviews)}",
        "",
        "## Findings",
        "| Severity | Action | Case | Service | Denial reason | Flag | Evidence | Next step |",
        "|---|---|---|---|---|---|---|---|",
    ]
    if findings:
        for finding in findings:
            case = finding.case
            lines.append(
                "| "
                + " | ".join(
                    [
                        finding.severity,
                        finding.action,
                        case.case_id,
                        case.requested_service or case.service_type or "unknown",
                        case.denial_reason,
                        finding.flag,
                        finding.evidence.replace("|", "/"),
                        finding.next_step.replace("|", "/"),
                    ]
                )
                + " |"
            )
    else:
        lines.append("| info | owner_review | all | supplied packet | none | no_material_gaps_found | supplied fields | Have the authorized owner verify and submit through the plan's process. |")

    flag_counts = Counter(item.flag for item in findings)
    lines.extend(
        [
            "",
            "## Packet Checklist",
            "- Written denial/adverse determination with appeal instructions and deadline.",
            "- Patient/member authorization if anyone else files or discusses the appeal.",
            "- Denial reason mapped to payer criteria, with each criterion tied to evidence.",
            "- Provider-signed medical necessity or reconsideration letter when clinical review is needed.",
            "- Chart notes, prior treatment history, objective results, and step-therapy failure/intolerance evidence.",
            "- Coding, units, site-of-service, and provider-type reconciliation for code/site/quantity denials.",
            "- Peer-to-peer log, call log, fax/portal receipts, and owner/date tracker.",
            "",
            "## Flag Counts",
        ]
    )
    for flag, count in sorted(flag_counts.items()):
        lines.append(f"- {flag}: {count}")
    if not flag_counts:
        lines.append("- no_material_gaps_found: 1")

    lines.extend(
        [
            "",
            "## Guardrails",
            "- This is administrative workflow support, not medical, legal, insurance-coverage, or billing advice.",
            "- Do not invent clinical facts, diagnoses, trials, failed therapies, contraindications, signatures, or plan criteria.",
            "- Do not upload uncensored PHI, full member IDs, SSNs, credentials, payment card data, or secrets into prompts.",
            "- Do not submit appeals, portal messages, complaints, or external review requests without explicit authorization.",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", required=True, type=Path, help="CSV or JSON prior authorization appeal cases")
    parser.add_argument("--evidence-dir", type=Path, help="Directory containing local evidence files")
    parser.add_argument("--today", default=date.today().isoformat(), help="Review date in YYYY-MM-DD format")
    args = parser.parse_args(argv)

    today = parse_date(args.today)
    if today is None:
        raise SystemExit("--today must use YYYY-MM-DD, YYYY/MM/DD, MM/DD/YYYY, or DD/MM/YYYY.")

    cases = parse_cases(args.cases)
    evidence = collect_evidence(args.evidence_dir)
    findings: list[Finding] = []
    for case in cases:
        findings.extend(analyze_case(case, evidence, today))

    print(render_report(cases, findings, today))
    return 2 if any(finding.severity == "blocker" for finding in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
