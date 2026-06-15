#!/usr/bin/env python3
"""Preflight FMLA certification packets before owner review."""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any


EVIDENCE_KEYWORDS = {
    "eligibility_notice": ("eligibility", "wh-381", "notice-eligibility"),
    "rights_notice": ("rights", "responsibilities", "wh-381"),
    "certification": ("certification", "wh-380", "medical-cert", "provider"),
    "cure_notice": ("cure", "incomplete", "insufficient", "defect", "wh-382"),
    "designation_notice": ("designation", "wh-382", "approved", "denied"),
    "delivery_proof": ("delivery", "submitted", "receipt", "email", "fax", "upload"),
}

SENSITIVE_FILENAME = re.compile(
    r"(token|secret|api[-_ ]?key|private[-_ ]?key|password|ssn|social[-_ ]?security|"
    r"diagnosis|full[-_ ]?medical|claim[-_ ]?number|portal|login|employee[-_ ]?id|bank)",
    re.IGNORECASE,
)

INTERMITTENT_TERMS = ("intermittent", "reduced", "flare", "episode", "as needed", "as-needed")
FAMILY_TERMS = ("family", "spouse", "parent", "child", "son", "daughter", "care for", "caregiver")


@dataclass(frozen=True)
class FMLACase:
    row_number: int
    case_id: str
    employee_role: str
    employer_employee_count: int | None
    tenure_months: int | None
    hours_worked_last_12_months: int | None
    worksite_employee_count_75_miles: int | None
    leave_reason: str
    leave_start_date: date | None
    certification_requested_date: date | None
    certification_due_date: date | None
    certification_submitted_date: date | None
    incomplete_or_insufficient_notice: bool
    cure_notice_date: date | None
    cure_due_date: date | None
    certification_signed: bool
    provider_contact_info: bool
    serious_health_condition_checked: bool
    incapacity_duration: bool
    treatment_schedule: bool
    intermittent_frequency: bool
    unable_to_work_or_care_statement: bool
    family_relationship: str
    eligibility_notice_received: bool
    rights_responsibilities_notice_received: bool
    designation_notice_received: bool
    live_action_requested: bool
    fields: dict[str, str]


@dataclass(frozen=True)
class Finding:
    severity: str
    action: str
    case_id: str
    leave_reason: str
    flag: str
    evidence: str
    next_step: str


def parse_date(value: str) -> date | None:
    value = value.strip()
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"invalid date '{value}', expected YYYY-MM-DD")


def parse_int(value: str) -> int | None:
    value = value.strip()
    if not value:
        return None
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"invalid integer '{value}'") from exc


def truthy(value: str) -> bool:
    return value.strip().lower() in {"yes", "y", "true", "1", "present", "available", "attached", "sent"}


def normalize_row(raw: dict[str, Any]) -> dict[str, str]:
    return {str(key): "" if value is None else str(value).strip() for key, value in raw.items()}


def case_from_row(raw: dict[str, Any], row_number: int) -> FMLACase:
    row = normalize_row(raw)
    return FMLACase(
        row_number=row_number,
        case_id=row.get("case_id") or f"row-{row_number}",
        employee_role=row.get("employee_role", ""),
        employer_employee_count=parse_int(row.get("employer_employee_count", "")),
        tenure_months=parse_int(row.get("tenure_months", "")),
        hours_worked_last_12_months=parse_int(row.get("hours_worked_last_12_months", "")),
        worksite_employee_count_75_miles=parse_int(row.get("worksite_employee_count_75_miles", "")),
        leave_reason=row.get("leave_reason", ""),
        leave_start_date=parse_date(row.get("leave_start_date", "")),
        certification_requested_date=parse_date(row.get("certification_requested_date", "")),
        certification_due_date=parse_date(row.get("certification_due_date", "")),
        certification_submitted_date=parse_date(row.get("certification_submitted_date", "")),
        incomplete_or_insufficient_notice=truthy(row.get("incomplete_or_insufficient_notice", "")),
        cure_notice_date=parse_date(row.get("cure_notice_date", "")),
        cure_due_date=parse_date(row.get("cure_due_date", "")),
        certification_signed=truthy(row.get("certification_signed", "")),
        provider_contact_info=truthy(row.get("provider_contact_info", "")),
        serious_health_condition_checked=truthy(row.get("serious_health_condition_checked", "")),
        incapacity_duration=truthy(row.get("incapacity_duration", "")),
        treatment_schedule=truthy(row.get("treatment_schedule", "")),
        intermittent_frequency=truthy(row.get("intermittent_frequency", "")),
        unable_to_work_or_care_statement=truthy(row.get("unable_to_work_or_care_statement", "")),
        family_relationship=row.get("family_relationship", ""),
        eligibility_notice_received=truthy(row.get("eligibility_notice_received", "")),
        rights_responsibilities_notice_received=truthy(row.get("rights_responsibilities_notice_received", "")),
        designation_notice_received=truthy(row.get("designation_notice_received", "")),
        live_action_requested=truthy(row.get("live_action_requested", "")),
        fields=row,
    )


def read_cases(path: Path) -> list[FMLACase]:
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            for key in ("cases", "requests", "leaves", "rows"):
                if key in data:
                    data = data[key]
                    break
        if not isinstance(data, list):
            raise ValueError("JSON input must be a list or contain cases, requests, leaves, or rows")
        return [case_from_row(row, index + 1) for index, row in enumerate(data)]

    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return [case_from_row(row, index) for index, row in enumerate(reader, start=2)]


def evidence_index(evidence_dir: Path) -> dict[str, list[Path]]:
    files: dict[str, list[Path]] = {}
    if not evidence_dir.exists():
        return files
    for path in evidence_dir.rglob("*"):
        if path.is_file():
            files.setdefault(path.name.lower(), []).append(path)
    return files


def evidence_present(case: FMLACase, evidence: dict[str, list[Path]], evidence_type: str) -> tuple[bool, list[str]]:
    case_key = case.case_id.lower()
    hits: list[str] = []
    for name, paths in evidence.items():
        name_without_case = name.replace(case_key, "")
        if case_key in name and any(keyword in name_without_case for keyword in EVIDENCE_KEYWORDS[evidence_type]):
            hits.extend(str(path) for path in paths)
    return bool(hits), hits[:3]


def sensitive_hits(evidence: dict[str, list[Path]]) -> list[str]:
    hits: list[str] = []
    for paths in evidence.values():
        for path in paths:
            if SENSITIVE_FILENAME.search(path.name):
                hits.append(str(path))
    return sorted(hits)


def reason_contains(reason: str, terms: tuple[str, ...]) -> bool:
    lower = reason.lower()
    return any(term in lower for term in terms)


def add(
    findings: list[Finding],
    severity: str,
    action: str,
    case: FMLACase,
    flag: str,
    evidence: str,
    next_step: str,
) -> None:
    findings.append(
        Finding(
            severity=severity,
            action=action,
            case_id=case.case_id,
            leave_reason=case.leave_reason or "missing",
            flag=flag,
            evidence=evidence,
            next_step=next_step,
        )
    )


def evaluate_case(case: FMLACase, evidence: dict[str, list[Path]], today: date) -> list[Finding]:
    findings: list[Finding] = []

    if case.live_action_requested:
        add(
            findings,
            "high",
            "hold_packet",
            case,
            "live_action_requested",
            "row requests live submission/contact/action",
            "Stop before contacting HR, provider, leave administrator, agency, or portal; prepare owner questions only.",
        )

    sensitive = sensitive_hits(evidence)
    if sensitive:
        add(
            findings,
            "high",
            "hold_packet",
            case,
            "sensitive_filename_review",
            "; ".join(sensitive[:3]),
            "Rename or remove sensitive files before sharing packet contents with an agent.",
        )

    if case.employer_employee_count is None or case.tenure_months is None or case.hours_worked_last_12_months is None:
        add(
            findings,
            "medium",
            "eligibility_review",
            case,
            "eligibility_inputs_missing",
            "employer size, tenure, or hours missing",
            "Collect eligibility notice or owner-confirmed employment facts before treating the packet as ready.",
        )
    else:
        if case.employer_employee_count < 50:
            add(
                findings,
                "medium",
                "eligibility_review",
                case,
                "employer_size_below_usual_threshold",
                f"employer_employee_count={case.employer_employee_count}",
                "Route to authorized owner for FMLA/state-leave applicability review.",
            )
        if case.tenure_months < 12:
            add(
                findings,
                "medium",
                "eligibility_review",
                case,
                "tenure_below_12_months",
                f"tenure_months={case.tenure_months}",
                "Confirm eligibility notice and any non-FMLA leave path before relying on FMLA protection.",
            )
        if case.hours_worked_last_12_months < 1250:
            add(
                findings,
                "medium",
                "eligibility_review",
                case,
                "hours_below_1250",
                f"hours_worked_last_12_months={case.hours_worked_last_12_months}",
                "Confirm hours calculation and eligibility notice with the authorized owner.",
            )

    if case.worksite_employee_count_75_miles is not None and case.worksite_employee_count_75_miles < 50:
        add(
            findings,
            "medium",
            "eligibility_review",
            case,
            "worksite_count_below_usual_threshold",
            f"worksite_employee_count_75_miles={case.worksite_employee_count_75_miles}",
            "Confirm worksite count and state/local leave alternatives with the authorized owner.",
        )

    has_eligibility_file, eligibility_files = evidence_present(case, evidence, "eligibility_notice")
    if not case.eligibility_notice_received and not has_eligibility_file:
        add(
            findings,
            "high",
            "hold_packet",
            case,
            "eligibility_notice_missing",
            "no eligibility notice field or evidence file",
            "Ask authorized owner to locate or request eligibility notice before final classification.",
        )
    elif has_eligibility_file:
        add(
            findings,
            "low",
            "owner_review",
            case,
            "eligibility_notice_evidence_present",
            ", ".join(eligibility_files),
            "Use the notice to verify deadlines and owner questions.",
        )

    has_rights_file, _ = evidence_present(case, evidence, "rights_notice")
    if not case.rights_responsibilities_notice_received and not has_rights_file:
        add(
            findings,
            "medium",
            "hold_packet",
            case,
            "rights_responsibilities_notice_missing",
            "no rights/responsibilities notice field or evidence file",
            "Locate rights and responsibilities notice before submission/designation review.",
        )

    has_certification_file, _ = evidence_present(case, evidence, "certification")
    if not has_certification_file:
        add(
            findings,
            "medium",
            "hold_packet",
            case,
            "certification_evidence_file_missing",
            "no case-matched certification file in evidence directory",
            "Attach a redacted certification or transcribe the material fields before final review.",
        )

    if case.certification_requested_date is None:
        add(
            findings,
            "medium",
            "deadline_escalation",
            case,
            "certification_request_date_missing",
            "certification_requested_date blank",
            "Collect request date to verify the certification window.",
        )

    if case.certification_due_date is None:
        add(
            findings,
            "high",
            "deadline_escalation",
            case,
            "certification_due_date_missing",
            "certification_due_date blank",
            "Collect the due date from the written request or owner system before treating packet as ready.",
        )
    elif case.certification_submitted_date is None and today > case.certification_due_date:
        add(
            findings,
            "high",
            "deadline_escalation",
            case,
            "certification_deadline_passed",
            f"due {case.certification_due_date.isoformat()}; submitted missing",
            "Confirm owner escalation path and document any good-faith effort or extension request.",
        )
    elif case.certification_submitted_date and case.certification_submitted_date > case.certification_due_date:
        add(
            findings,
            "high",
            "deadline_escalation",
            case,
            "certification_submitted_after_due_date",
            f"submitted {case.certification_submitted_date.isoformat()} after due {case.certification_due_date.isoformat()}",
            "Prepare timeline and good-faith-effort evidence for authorized owner review.",
        )
    elif case.certification_due_date and 0 <= (case.certification_due_date - today).days <= 3:
        add(
            findings,
            "medium",
            "deadline_escalation",
            case,
            "certification_deadline_imminent",
            f"due {case.certification_due_date.isoformat()}",
            "Prioritize missing fields and delivery proof before the deadline.",
        )

    if not case.certification_signed:
        add(
            findings,
            "high",
            "hold_packet",
            case,
            "provider_signature_missing",
            "certification_signed=no",
            "Ask authorized owner/provider process to repair signature/date before submission.",
        )

    if not case.provider_contact_info:
        add(
            findings,
            "medium",
            "hold_packet",
            case,
            "provider_contact_missing",
            "provider_contact_info=no",
            "Collect provider contact fields or document why the form does not require them.",
        )

    if not case.serious_health_condition_checked:
        add(
            findings,
            "high",
            "hold_packet",
            case,
            "serious_health_condition_field_missing",
            "serious_health_condition_checked=no",
            "Prepare provider question about the applicable certification section; do not choose it for the provider.",
        )

    if not case.incapacity_duration:
        add(
            findings,
            "medium",
            "hold_packet",
            case,
            "incapacity_duration_missing",
            "incapacity_duration=no",
            "Ask authorized provider process to clarify incapacity period or expected duration.",
        )

    if not case.treatment_schedule:
        add(
            findings,
            "medium",
            "hold_packet",
            case,
            "treatment_schedule_missing",
            "treatment_schedule=no",
            "Ask authorized provider process to clarify appointment/treatment schedule if applicable.",
        )

    if not case.unable_to_work_or_care_statement:
        add(
            findings,
            "medium",
            "hold_packet",
            case,
            "work_or_care_statement_missing",
            "unable_to_work_or_care_statement=no",
            "Clarify whether the certification states inability to work or need to care for a covered family member.",
        )

    if reason_contains(case.leave_reason, INTERMITTENT_TERMS) and not case.intermittent_frequency:
        add(
            findings,
            "high",
            "intermittent_schedule_repair",
            case,
            "intermittent_frequency_missing",
            "intermittent/reduced leave reason without frequency/duration",
            "Prepare provider questions for expected frequency, duration, and treatment or flare-up pattern.",
        )

    if reason_contains(case.leave_reason, FAMILY_TERMS) and not case.family_relationship:
        add(
            findings,
            "high",
            "hold_packet",
            case,
            "family_relationship_missing",
            "family-care leave reason without relationship field",
            "Confirm covered relationship field is completed before owner review.",
        )

    if case.incomplete_or_insufficient_notice:
        has_cure_file, cure_files = evidence_present(case, evidence, "cure_notice")
        if case.cure_notice_date is None or not has_cure_file:
            add(
                findings,
                "high",
                "cure_notice_review",
                case,
                "written_cure_notice_missing",
                "incomplete/insufficient marked but cure notice date or file missing",
                "Locate written notice listing exact deficiencies before denial or cure review.",
            )
        else:
            add(
                findings,
                "low",
                "cure_notice_review",
                case,
                "written_cure_notice_present",
                ", ".join(cure_files),
                "Use notice to map each defect to a repair question.",
            )
        if case.cure_due_date is None:
            add(
                findings,
                "high",
                "deadline_escalation",
                case,
                "cure_due_date_missing",
                "cure_due_date blank",
                "Collect cure due date before deciding packet readiness.",
            )
        elif today > case.cure_due_date:
            add(
                findings,
                "high",
                "deadline_escalation",
                case,
                "cure_deadline_passed",
                f"cure due {case.cure_due_date.isoformat()}",
                "Escalate to authorized owner with defect list and any good-faith-effort evidence.",
            )

    has_designation_file, _ = evidence_present(case, evidence, "designation_notice")
    if not case.designation_notice_received and not has_designation_file:
        add(
            findings,
            "medium",
            "owner_review",
            case,
            "designation_notice_not_yet_documented",
            "designation notice not marked or found",
            "Track designation notice or pending status after the certification is reviewed.",
        )

    has_delivery_file, _ = evidence_present(case, evidence, "delivery_proof")
    if case.certification_submitted_date and not has_delivery_file:
        add(
            findings,
            "medium",
            "hold_packet",
            case,
            "delivery_proof_missing",
            "submitted date exists but no delivery proof file",
            "Attach confirmation, fax receipt, email receipt, or portal confirmation if available.",
        )

    if not findings:
        add(
            findings,
            "low",
            "owner_review",
            case,
            "no_local_blockers_found",
            "required fields present in provided row",
            "Packet appears ready for authorized owner review; do not treat this as legal approval.",
        )

    return findings


def render(findings: list[Finding], cases: list[FMLACase], today: date) -> str:
    high_count = sum(1 for finding in findings if finding.severity == "high")
    review_count = sum(1 for finding in findings if finding.severity in {"medium", "low"})
    if high_count:
        decision = "Hold certification packet pending repair"
    elif review_count:
        decision = "Review certification packet before submission or designation"
    else:
        decision = "Packet appears ready for authorized owner review"

    lines = [
        "## FMLA Certification Decision",
        decision,
        "",
        "## Case Summary",
        f"Review date: {today.isoformat()}. Cases reviewed: {len(cases)}. Blockers: {high_count}. Review items: {review_count}.",
        "",
        "## Findings",
        "| Severity | Action | Case | Leave reason | Flag | Evidence | Next step |",
        "|---|---|---|---|---|---|---|",
    ]
    for finding in findings:
        lines.append(
            "| {severity} | {action} | {case_id} | {leave_reason} | {flag} | {evidence} | {next_step} |".format(
                severity=finding.severity,
                action=finding.action,
                case_id=finding.case_id,
                leave_reason=finding.leave_reason.replace("|", "/"),
                flag=finding.flag,
                evidence=finding.evidence.replace("|", "/"),
                next_step=finding.next_step.replace("|", "/"),
            )
        )

    lines.extend(
        [
            "",
            "## Packet Checklist",
            "- Eligibility notice and rights/responsibilities notice",
            "- Certification request date, due date, submitted date, and delivery proof",
            "- Written incomplete/insufficient notice and cure deadline when defects are alleged",
            "- Provider signature/date and provider contact information",
            "- Serious-health-condition, incapacity, treatment, intermittent/reduced-schedule, and work/care statement fields",
            "- Family relationship field for family-care leave",
            "- Designation notice or documented pending-designation status",
            "- Owner questions for HR, provider, leave administrator, union, counsel, or agency",
            "",
            "## Guardrails",
            "- Redact SSNs, full medical histories, employee IDs, claim numbers, portal credentials, bank data, and unrelated personnel data.",
            "- Do not submit, deny, approve, upload, or contact an employer, provider, leave administrator, insurer, union, agency, or court.",
            "- This report is not legal advice, medical advice, employment advice, or a final eligibility/approval decision.",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", required=True, type=Path, help="CSV or JSON FMLA case table")
    parser.add_argument("--evidence-dir", type=Path, default=Path("."), help="Optional local evidence directory")
    parser.add_argument("--today", default=date.today().isoformat(), help="Review date as YYYY-MM-DD")
    parser.add_argument("--output", type=Path, help="Optional path to write the Markdown report")
    args = parser.parse_args()

    today = parse_date(args.today)
    if today is None:
        raise ValueError("--today is required")

    cases = read_cases(args.cases)
    evidence = evidence_index(args.evidence_dir)
    findings: list[Finding] = []
    for case in cases:
        findings.extend(evaluate_case(case, evidence, today))

    report = render(findings, cases, today)
    if args.output:
        args.output.write_text(report + "\n", encoding="utf-8")
    else:
        print(report)

    return 2 if any(finding.severity == "high" for finding in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
