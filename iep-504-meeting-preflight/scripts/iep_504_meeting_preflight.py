#!/usr/bin/env python3
"""Preflight IEP and 504 meeting packets before review or escalation."""

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
    "prior_plan": ("prior-plan", "current-plan", "iep", "504", "plan"),
    "evaluation_report": ("evaluation", "reevaluation", "assessment", "psychoeducational", "eval-report"),
    "progress_report": ("progress", "present-level", "baseline", "goal-progress", "report-card"),
    "service_log": ("service-log", "minutes", "provider-log", "delivery-log", "therapy-log"),
    "accommodation_log": ("accommodation", "implementation", "teacher-log", "testing-log"),
    "parent_concerns": ("parent-concern", "concerns", "agenda", "meeting-questions"),
    "school_notice": ("notice", "prior-written", "meeting-notice", "pwn"),
    "behavior_data": ("behavior", "incident", "fba", "bip", "discipline"),
    "discipline_notice": ("discipline", "suspension", "manifestation", "incident", "mdr"),
    "transition_plan": ("transition", "postsecondary", "agency", "course-plan"),
    "assistive_technology_review": ("assistive", "at-review", "device", "aac", "technology"),
}

SENSITIVE_FILENAME = re.compile(
    r"(token|secret|api[-_ ]?key|private[-_ ]?key|password|full[-_ ]?card|cvv|ssn|passport|student[-_ ]?id|portal[-_ ]?login)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class MeetingCase:
    row_number: int
    case_id: str
    student_role: str
    meeting_type: str
    plan_type: str
    grade_band: str
    primary_concern: str
    requested_change: str
    meeting_date: date | None
    last_evaluation_date: date | None
    reevaluation_due_date: date | None
    consent_status: str
    live_action_requested: bool
    fields: dict[str, str]


@dataclass(frozen=True)
class Finding:
    severity: str
    action: str
    case_id: str
    plan_type: str
    meeting_type: str
    concern: str
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


def truthy(value: str) -> bool:
    return value.strip().lower() in {"yes", "y", "true", "1", "present", "available", "attached", "sent", "granted"}


def normalize_row(raw: dict[str, Any]) -> dict[str, str]:
    return {str(key): "" if value is None else str(value).strip() for key, value in raw.items()}


def row_to_case(row_number: int, raw: dict[str, Any]) -> MeetingCase:
    row = normalize_row(raw)
    return MeetingCase(
        row_number=row_number,
        case_id=row.get("case_id") or f"row-{row_number}",
        student_role=row.get("student_role", ""),
        meeting_type=row.get("meeting_type", "").lower().replace(" ", "_"),
        plan_type=row.get("plan_type", ""),
        grade_band=row.get("grade_band", "").lower(),
        primary_concern=row.get("primary_concern", ""),
        requested_change=row.get("requested_change", ""),
        meeting_date=parse_date(row.get("meeting_date", "")),
        last_evaluation_date=parse_date(row.get("last_evaluation_date", "")),
        reevaluation_due_date=parse_date(row.get("reevaluation_due_date", "")),
        consent_status=row.get("consent_status", "").lower(),
        live_action_requested=truthy(row.get("live_action_requested", "")),
        fields=row,
    )


def read_cases(path: Path) -> list[MeetingCase]:
    if path.suffix.lower() == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            rows = payload.get("cases") or payload.get("meetings") or payload.get("students") or payload.get("rows")
            if rows is None:
                raise ValueError("JSON input must contain cases, meetings, students, or rows")
        else:
            rows = payload
        if not isinstance(rows, list):
            raise ValueError("JSON cases payload must be a list")
        return [row_to_case(index, row) for index, row in enumerate(rows, start=2)]

    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return [row_to_case(index, raw) for index, raw in enumerate(reader, start=2)]


def evidence_index(evidence_dir: Path) -> dict[str, list[Path]]:
    files: dict[str, list[Path]] = {}
    if not evidence_dir.exists():
        return files
    for path in evidence_dir.rglob("*"):
        if path.is_file():
            files.setdefault(path.name.lower(), []).append(path)
    return files


def evidence_present(case: MeetingCase, evidence: dict[str, list[Path]], evidence_type: str) -> tuple[bool, list[str]]:
    if truthy(case.fields.get(evidence_type, "")):
        return True, [f"csv:{evidence_type}"]

    case_key = case.case_id.lower()
    keywords = EVIDENCE_KEYWORDS[evidence_type]
    hits: list[str] = []
    for name, paths in evidence.items():
        name_without_case = name.replace(case_key, "")
        if case_key in name and any(keyword in name_without_case for keyword in keywords):
            hits.extend(str(path) for path in paths)
    return bool(hits), hits[:3]


def evidence_label(case: MeetingCase, evidence: dict[str, list[Path]], evidence_type: str) -> str:
    present, hits = evidence_present(case, evidence, evidence_type)
    if present:
        return ", ".join(hits[:2])
    return f"no {evidence_type.replace('_', ' ')} found"


def sensitive_hits(evidence: dict[str, list[Path]]) -> list[str]:
    hits: list[str] = []
    for paths in evidence.values():
        for path in paths:
            if SENSITIVE_FILENAME.search(path.name):
                hits.append(str(path))
    return sorted(hits)


def add_finding(
    findings: list[Finding],
    case: MeetingCase,
    severity: str,
    action: str,
    flag: str,
    evidence: str,
    next_step: str,
) -> None:
    findings.append(
        Finding(
            severity=severity,
            action=action,
            case_id=case.case_id,
            plan_type=case.plan_type or "unspecified",
            meeting_type=case.meeting_type or "unspecified",
            concern=case.primary_concern or case.requested_change or "unspecified",
            flag=flag,
            evidence=evidence,
            next_step=next_step,
        )
    )


def needs_current_evaluation(case: MeetingCase) -> bool:
    text = f"{case.meeting_type} {case.primary_concern} {case.requested_change}".lower()
    triggers = ("eligibility", "reevaluation", "service", "placement", "assistive", "transition", "support", "change")
    return any(trigger in text for trigger in triggers)


def needs_progress(case: MeetingCase) -> bool:
    text = f"{case.meeting_type} {case.primary_concern} {case.requested_change}".lower()
    return any(trigger in text for trigger in ("annual", "goal", "progress", "service", "reading", "math", "writing", "support"))


def needs_implementation(case: MeetingCase) -> bool:
    text = f"{case.meeting_type} {case.primary_concern} {case.requested_change}".lower()
    return any(trigger in text for trigger in ("service", "missed", "accommodation", "implementation", "minutes", "testing"))


def evaluate(case: MeetingCase, evidence: dict[str, list[Path]], today: date) -> list[Finding]:
    findings: list[Finding] = []

    if not case.plan_type:
        add_finding(findings, case, "Blocker", "hold_meeting_packet", "plan_type_missing", "case row missing plan type", "Identify whether this is an IEP, 504, evaluation-only, or records-review packet.")
    if not case.meeting_type:
        add_finding(findings, case, "Blocker", "hold_meeting_packet", "meeting_type_missing", "case row missing meeting type", "Add the meeting type before assigning evidence gates.")
    if not case.primary_concern and not case.requested_change:
        add_finding(findings, case, "Blocker", "hold_meeting_packet", "concern_or_requested_change_missing", "no concern or requested change found", "Write a concise concern and requested discussion topic.")

    if not evidence_present(case, evidence, "prior_plan")[0]:
        add_finding(findings, case, "Blocker", "hold_meeting_packet", "prior_plan_missing", evidence_label(case, evidence, "prior_plan"), "Add the current IEP/504 plan or document that no plan exists.")

    if not evidence_present(case, evidence, "parent_concerns")[0]:
        add_finding(findings, case, "Review", "goal_data_mapping", "parent_concerns_missing", evidence_label(case, evidence, "parent_concerns"), "Add a concise parent/adult-student concern statement and meeting questions.")

    if case.meeting_date is None:
        add_finding(findings, case, "Review", "deadline_escalation", "meeting_date_missing", "case row missing meeting date", "Add meeting date so packet readiness can be timed.")
    elif case.meeting_date < today:
        add_finding(findings, case, "Blocker", "deadline_escalation", "meeting_date_passed", f"meeting date {case.meeting_date.isoformat()}", "Verify whether this is a follow-up packet and add meeting notes or outcome.")
    elif (case.meeting_date - today).days <= 7:
        add_finding(findings, case, "Review", "deadline_escalation", "meeting_within_7_days", f"meeting date {case.meeting_date.isoformat()}", "Prioritize missing records and owner questions before the meeting.")

    if needs_current_evaluation(case):
        eval_present = evidence_present(case, evidence, "evaluation_report")[0]
        stale = case.last_evaluation_date is None or (today - case.last_evaluation_date).days > 1095
        if not eval_present or stale:
            add_finding(findings, case, "Blocker", "evaluation_repair", "current_evaluation_missing_or_stale", evidence_label(case, evidence, "evaluation_report"), "Locate current evaluation or reevaluation evidence before asking for eligibility, service, placement, or support changes.")

    if case.reevaluation_due_date and case.reevaluation_due_date < today:
        add_finding(findings, case, "Blocker", "deadline_escalation", "reevaluation_deadline_review", f"reevaluation due {case.reevaluation_due_date.isoformat()}", "Ask the authorized owner to verify reevaluation status and district-specific timing.")
    elif case.reevaluation_due_date and (case.reevaluation_due_date - today).days <= 30:
        add_finding(findings, case, "Review", "deadline_escalation", "reevaluation_due_within_30_days", f"reevaluation due {case.reevaluation_due_date.isoformat()}", "Prepare reevaluation questions and consent/notice records.")

    if needs_progress(case) and not evidence_present(case, evidence, "progress_report")[0]:
        add_finding(findings, case, "Blocker", "goal_data_mapping", "progress_report_missing", evidence_label(case, evidence, "progress_report"), "Add present levels, goal progress, baseline data, or work samples tied to the requested change.")

    if needs_implementation(case):
        if "504" in case.plan_type.lower() or "accommodation" in f"{case.meeting_type} {case.primary_concern} {case.requested_change}".lower():
            if not evidence_present(case, evidence, "accommodation_log")[0]:
                add_finding(findings, case, "Blocker", "implementation_review", "accommodation_log_missing", evidence_label(case, evidence, "accommodation_log"), "Add dated examples or logs showing whether accommodations were implemented.")
        else:
            if not evidence_present(case, evidence, "service_log")[0]:
                add_finding(findings, case, "Blocker", "implementation_review", "service_log_missing", evidence_label(case, evidence, "service_log"), "Add service delivery logs, provider notes, or minutes evidence for the reviewed period.")

    behavior_context = f"{case.meeting_type} {case.primary_concern} {case.requested_change}".lower()
    if any(term in behavior_context for term in ("manifestation", "discipline", "suspension", "behavior", "safety")):
        if not evidence_present(case, evidence, "behavior_data")[0] or not evidence_present(case, evidence, "discipline_notice")[0]:
            add_finding(findings, case, "Blocker", "behavior_or_discipline_review", "behavior_or_discipline_data_missing", "behavior data or discipline notice missing", "Add discipline notice, incident dates, behavior data, support plan, and prior intervention history.")

    if "transition" in behavior_context and not evidence_present(case, evidence, "transition_plan")[0]:
        add_finding(findings, case, "Blocker", "transition_or_at_review", "transition_plan_missing", evidence_label(case, evidence, "transition_plan"), "Add age/grade context, transition goals, postsecondary interests, course planning, or agency notes.")

    if any(term in behavior_context for term in ("assistive", "technology", "device", "aac")) and not evidence_present(case, evidence, "assistive_technology_review")[0]:
        add_finding(findings, case, "Review", "transition_or_at_review", "assistive_technology_review_missing", evidence_label(case, evidence, "assistive_technology_review"), "Add trial data, access barriers, device history, or specialist input.")

    if "evaluation" in behavior_context and case.consent_status in {"", "missing", "pending", "unknown"}:
        add_finding(findings, case, "Review", "deadline_escalation", "evaluation_consent_status_unclear", f"consent status: {case.consent_status or 'missing'}", "Clarify consent/request status before relying on evaluation timelines.")

    if not evidence_present(case, evidence, "school_notice")[0] and any(term in behavior_context for term in ("evaluation", "reevaluation", "manifestation", "placement", "service")):
        add_finding(findings, case, "Review", "deadline_escalation", "notice_or_school_response_missing", evidence_label(case, evidence, "school_notice"), "Add meeting notice, prior written notice, records response, or school response if available.")

    if case.live_action_requested:
        add_finding(findings, case, "Blocker", "hold_meeting_packet", "live_action_requested", "case requested email, portal, complaint, consent, or filing action", "Prepare packet only; authorized owner must send messages, consent decisions, complaints, or filings.")

    if not findings:
        add_finding(findings, case, "Review", "owner_review", "ready_for_owner_review", "no material local blockers found", "Authorized owner should verify final questions, privacy redactions, and jurisdiction-specific requirements.")

    return findings


def render_report(cases: list[MeetingCase], findings: list[Finding], sensitive: list[str], today: date) -> str:
    blockers = [finding for finding in findings if finding.severity == "Blocker"]
    reviews = [finding for finding in findings if finding.severity != "Blocker"]
    if blockers:
        decision = "Hold meeting packet pending evidence repair"
    elif reviews:
        decision = "Review before meeting"
    else:
        decision = "Packet appears ready for authorized owner review"

    lines = [
        "## IEP/504 Meeting Decision",
        decision,
        "",
        "## Meeting Summary",
        f"Review date: {today.isoformat()}. Cases reviewed: {len(cases)}. Blockers: {len(blockers)}. Review items: {len(reviews)}.",
        "",
        "## Findings",
        "| Severity | Action | Case | Plan | Meeting type | Concern | Flag | Evidence | Next step |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for finding in findings:
        lines.append(
            "| {severity} | {action} | {case_id} | {plan_type} | {meeting_type} | {concern} | {flag} | {evidence} | {next_step} |".format(
                severity=finding.severity,
                action=finding.action,
                case_id=finding.case_id,
                plan_type=finding.plan_type,
                meeting_type=finding.meeting_type,
                concern=finding.concern.replace("|", "/"),
                flag=finding.flag,
                evidence=finding.evidence.replace("|", "/"),
                next_step=finding.next_step.replace("|", "/"),
            )
        )

    lines.extend(
        [
            "",
            "## Packet Checklist",
            "- Current IEP or 504 plan, prior amendments, and meeting notice.",
            "- Current evaluation or reevaluation, present levels, progress data, and work samples.",
            "- Service logs, accommodation implementation logs, provider notes, and dated examples.",
            "- Parent/adult-student concerns, requested discussion topics, and owner questions.",
            "- Consent, notice, records request, behavior, discipline, transition, or assistive-technology records when relevant.",
            "",
            "## Sensitive File Review",
        ]
    )
    if sensitive:
        lines.append("Potentially sensitive filenames need review before sharing:")
        for path in sensitive:
            lines.append(f"- {path}")
    else:
        lines.append("No sensitive evidence filenames detected by the local filename scan.")

    lines.extend(
        [
            "",
            "## Guardrails",
            "This report is administrative packet support, not legal, clinical, eligibility, placement, entitlement, or school-discipline advice. Do not submit complaints, emails, portal messages, consent decisions, or service-change requests without authorized owner action. Redact student IDs, SSNs, credentials, unrelated diagnoses, private family details, and secrets.",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", required=True, type=Path, help="CSV or JSON meeting case file")
    parser.add_argument("--evidence-dir", required=True, type=Path, help="Directory containing redacted local evidence files")
    parser.add_argument("--today", default=date.today().isoformat(), help="Review date in YYYY-MM-DD format")
    args = parser.parse_args()

    today = parse_date(args.today)
    if today is None:
        raise ValueError("--today must be a real date")

    cases = read_cases(args.cases)
    evidence = evidence_index(args.evidence_dir)
    findings: list[Finding] = []
    for case in cases:
        findings.extend(evaluate(case, evidence, today))

    print(render_report(cases, findings, sensitive_hits(evidence), today))
    return 2 if any(finding.severity == "Blocker" for finding in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
