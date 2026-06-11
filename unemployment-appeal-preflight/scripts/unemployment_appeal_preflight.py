#!/usr/bin/env python3
"""Preflight unemployment insurance appeal and hearing packets."""

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
    "determination_notice": ("determination", "decision", "denial", "disqualification", "overpayment"),
    "hearing_notice": ("hearing-notice", "notice-of-hearing", "hearing", "appeal-notice"),
    "hearing_packet": ("hearing-packet", "packet", "issue-list", "exhibits", "appeal-file"),
    "claimant_statement": ("claimant-statement", "statement", "timeline", "response"),
    "employer_evidence": ("employer", "writeup", "warning", "investigation", "incident", "policy", "exhibit"),
    "separation_timeline": ("timeline", "separation", "termination", "resignation", "last-day"),
    "policy_or_handbook": ("policy", "handbook", "rule", "procedure", "code-of-conduct"),
    "warning_or_writeup": ("warning", "writeup", "discipline", "coaching", "final-warning"),
    "firsthand_witness": ("witness", "supervisor", "coworker", "manager", "declaration"),
    "work_search_or_weekly_certification": ("certification", "weekly", "work-search", "job-search", "payment-request"),
    "medical_or_caregiver_evidence": ("medical", "doctor", "caregiver", "schedule", "restriction", "accommodation"),
    "good_cause_explanation": ("good-cause", "quit-reason", "resignation", "safety", "pay", "schedule"),
    "evidence_exchange": ("delivery", "mail", "fax", "email", "tracking", "exchange", "proof"),
}

SENSITIVE_FILENAME = re.compile(
    r"(token|secret|api[-_ ]?key|private[-_ ]?key|password|ssn|social[-_ ]?security|claimant[-_ ]?id|portal[-_ ]?login|bank[-_ ]?account|routing[-_ ]?number|tax[-_ ]?id)",
    re.IGNORECASE,
)

MISCONDUCT_ISSUES = {"misconduct", "discharge", "fired", "termination", "employer_appeal"}
QUIT_ISSUES = {"voluntary_quit", "quit", "resignation", "good_cause"}
ABLE_AVAILABLE_ISSUES = {"able_available", "able_and_available", "work_search", "refusal_of_work", "availability"}
OVERPAYMENT_ISSUES = {"overpayment", "repayment", "waiver", "retroactive_disqualification"}


@dataclass(frozen=True)
class AppealCase:
    row_number: int
    case_id: str
    party_role: str
    state: str
    appeal_stage: str
    issue_type: str
    determination_date: date | None
    appeal_deadline: date | None
    hearing_date: date | None
    live_action_requested: bool
    fields: dict[str, str]


@dataclass(frozen=True)
class Finding:
    severity: str
    action: str
    case_id: str
    state: str
    stage: str
    issue: str
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
    return value.strip().lower() in {"yes", "y", "true", "1", "present", "available", "attached", "sent", "submitted"}


def normalize_issue(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def normalize_row(raw: dict[str, Any]) -> dict[str, str]:
    return {str(key): "" if value is None else str(value).strip() for key, value in raw.items()}


def row_to_case(row_number: int, raw: dict[str, Any]) -> AppealCase:
    row = normalize_row(raw)
    return AppealCase(
        row_number=row_number,
        case_id=row.get("case_id") or f"row-{row_number}",
        party_role=row.get("party_role", "").lower(),
        state=row.get("state", "").upper(),
        appeal_stage=normalize_issue(row.get("appeal_stage", "")),
        issue_type=normalize_issue(row.get("issue_type", "")),
        determination_date=parse_date(row.get("determination_date", "")),
        appeal_deadline=parse_date(row.get("appeal_deadline", "")),
        hearing_date=parse_date(row.get("hearing_date", "")),
        live_action_requested=truthy(row.get("live_action_requested", "")),
        fields=row,
    )


def read_cases(path: Path) -> list[AppealCase]:
    if path.suffix.lower() == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            rows = payload.get("cases") or payload.get("appeals") or payload.get("hearings") or payload.get("rows")
            if rows is None:
                raise ValueError("JSON input must contain cases, appeals, hearings, or rows")
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


def evidence_present(case: AppealCase, evidence: dict[str, list[Path]], evidence_type: str) -> tuple[bool, list[str]]:
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


def evidence_label(case: AppealCase, evidence: dict[str, list[Path]], evidence_type: str) -> str:
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
    case: AppealCase,
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
            state=case.state or "unspecified",
            stage=case.appeal_stage or "unspecified",
            issue=case.issue_type or "unspecified",
            flag=flag,
            evidence=evidence,
            next_step=next_step,
        )
    )


def issue_in(issue: str, issue_set: set[str]) -> bool:
    return issue in issue_set or any(part in issue_set for part in issue.split("_"))


def evaluate(case: AppealCase, evidence: dict[str, list[Path]], today: date) -> list[Finding]:
    findings: list[Finding] = []

    if not case.state:
        add_finding(findings, case, "Review", "hold_appeal_packet", "state_missing", "case row missing state", "Add the state agency because deadlines and hearing rules are state-specific.")
    if not case.appeal_stage:
        add_finding(findings, case, "Blocker", "hold_appeal_packet", "appeal_stage_missing", "case row missing appeal stage", "Identify whether this is filing, hearing, reopening, employer appeal, overpayment, or second-level appeal.")
    if not case.issue_type:
        add_finding(findings, case, "Blocker", "hold_appeal_packet", "issue_type_missing", "case row missing issue type", "Add the issue listed on the determination or hearing notice.")

    if not evidence_present(case, evidence, "determination_notice")[0]:
        add_finding(findings, case, "Blocker", "hold_appeal_packet", "determination_notice_missing", evidence_label(case, evidence, "determination_notice"), "Add the exact determination or decision being appealed.")

    if case.appeal_deadline is None:
        add_finding(findings, case, "Review", "deadline_escalation", "appeal_deadline_missing", "case row missing appeal deadline", "Read the official notice and add the appeal deadline before deciding readiness.")
    elif case.appeal_deadline < today:
        add_finding(findings, case, "Blocker", "deadline_escalation", "appeal_deadline_passed", f"appeal deadline {case.appeal_deadline.isoformat()}", "Ask the authorized owner to verify late-appeal options and add a dated late-filing explanation or proof.")
    elif (case.appeal_deadline - today).days <= 3:
        add_finding(findings, case, "Review", "deadline_escalation", "appeal_deadline_within_3_days", f"appeal deadline {case.appeal_deadline.isoformat()}", "Prioritize owner-reviewed appeal text and delivery proof.")

    if case.hearing_date:
        if not evidence_present(case, evidence, "hearing_notice")[0]:
            add_finding(findings, case, "Blocker", "hold_appeal_packet", "hearing_notice_missing", evidence_label(case, evidence, "hearing_notice"), "Add the hearing notice with call-in, login, party, and issue instructions.")
        if not evidence_present(case, evidence, "hearing_packet")[0]:
            add_finding(findings, case, "Blocker", "hold_appeal_packet", "hearing_packet_missing", evidence_label(case, evidence, "hearing_packet"), "Locate the hearing packet, issue list, or exhibit packet before preparing testimony.")
        if case.hearing_date < today:
            add_finding(findings, case, "Blocker", "deadline_escalation", "hearing_date_passed", f"hearing date {case.hearing_date.isoformat()}", "Verify whether this is a reopening, appeal-board, or follow-up packet and add the decision or no-show details.")
        elif (case.hearing_date - today).days <= 7:
            add_finding(findings, case, "Review", "deadline_escalation", "hearing_within_7_days", f"hearing date {case.hearing_date.isoformat()}", "Finalize exhibit exchange, witness availability, call-in instructions, and hearing outline.")

    exchanged = truthy(case.fields.get("evidence_exchanged_to_all_parties", ""))
    exchange_evidence = evidence_present(case, evidence, "evidence_exchange")[0]
    if case.hearing_date and not exchanged and not exchange_evidence:
        add_finding(findings, case, "Blocker", "evidence_exchange_repair", "evidence_not_exchanged_to_all_parties", "case row says no and no exchange proof found", "Send only owner-approved exhibits to the hearing office and every listed party using the official process.")

    issue = case.issue_type
    if issue_in(issue, MISCONDUCT_ISSUES):
        has_employer_evidence = evidence_present(case, evidence, "employer_evidence")[0]
        has_policy = evidence_present(case, evidence, "policy_or_handbook")[0]
        has_witness = evidence_present(case, evidence, "firsthand_witness")[0] or truthy(case.fields.get("firsthand_witness", ""))
        if not (has_employer_evidence and (has_policy or has_witness)):
            add_finding(findings, case, "Blocker", "issue_evidence_mapping", "misconduct_evidence_missing_or_unsupported", evidence_label(case, evidence, "employer_evidence"), "Map the alleged final incident to policy, warning, investigation, and firsthand witness records.")
        if not evidence_present(case, evidence, "claimant_statement")[0]:
            add_finding(findings, case, "Review", "issue_evidence_mapping", "claimant_statement_missing", evidence_label(case, evidence, "claimant_statement"), "Prepare a concise dated statement that addresses the listed issue without contradicting prior statements.")

    if issue_in(issue, QUIT_ISSUES):
        if not evidence_present(case, evidence, "good_cause_explanation")[0]:
            add_finding(findings, case, "Blocker", "issue_evidence_mapping", "quit_reason_or_good_cause_missing", evidence_label(case, evidence, "good_cause_explanation"), "Add a dated quit reason, preservation attempts, and supporting records for the stated issue.")
        if not evidence_present(case, evidence, "separation_timeline")[0]:
            add_finding(findings, case, "Review", "issue_evidence_mapping", "separation_timeline_missing", evidence_label(case, evidence, "separation_timeline"), "Add a short timeline with last day worked, resignation notice, employer response, and relevant events.")

    if issue_in(issue, ABLE_AVAILABLE_ISSUES):
        if not evidence_present(case, evidence, "work_search_or_weekly_certification")[0]:
            add_finding(findings, case, "Blocker", "certification_continuity", "weekly_certification_or_work_search_missing", evidence_label(case, evidence, "work_search_or_weekly_certification"), "Add weekly certifications, work-search logs, or payment requests for affected weeks.")
        if not evidence_present(case, evidence, "medical_or_caregiver_evidence")[0] and any(word in issue for word in ("able", "available")):
            add_finding(findings, case, "Review", "issue_evidence_mapping", "availability_support_missing", evidence_label(case, evidence, "medical_or_caregiver_evidence"), "If availability was limited, add dated records explaining restrictions and availability windows.")

    if issue_in(issue, OVERPAYMENT_ISSUES):
        if not evidence_present(case, evidence, "work_search_or_weekly_certification")[0]:
            add_finding(findings, case, "Blocker", "issue_evidence_mapping", "affected_weeks_or_payment_history_missing", evidence_label(case, evidence, "work_search_or_weekly_certification"), "Add payment history, affected weeks, certifications, and the overpayment notice reason.")

    if case.party_role == "claimant" and not evidence_present(case, evidence, "work_search_or_weekly_certification")[0]:
        add_finding(findings, case, "Review", "certification_continuity", "weekly_certification_or_work_search_missing", evidence_label(case, evidence, "work_search_or_weekly_certification"), "Confirm whether weekly certifications and work-search records must continue during the appeal.")

    if truthy(case.fields.get("language_access_or_accommodation", "")):
        add_finding(findings, case, "Review", "owner_review", "language_access_or_accommodation_review", "case row requests access support", "Have the authorized owner verify interpreter, disability, phone, or scheduling accommodation steps on the official notice.")

    if case.live_action_requested:
        add_finding(findings, case, "Blocker", "owner_review", "live_action_requested", "live action requested in case row", "Do not file, upload, withdraw, request subpoenas, contact agencies, or join hearings from this workflow.")

    return findings


def render(findings: list[Finding], cases: list[AppealCase], today: date, sensitive: list[str]) -> str:
    blocker_count = sum(1 for finding in findings if finding.severity == "Blocker")
    review_count = sum(1 for finding in findings if finding.severity != "Blocker")
    if blocker_count:
        decision = "Hold appeal packet pending evidence repair"
    elif review_count:
        decision = "Review before hearing or filing"
    else:
        decision = "Packet appears ready for authorized owner review"

    lines = [
        "## Unemployment Appeal Decision",
        decision,
        "",
        "## Appeal Summary",
        f"Review date: {today.isoformat()}. Cases reviewed: {len(cases)}. Blockers: {blocker_count}. Reviews: {review_count}.",
        "",
        "## Findings",
        "| Severity | Action | Case | State | Stage | Issue | Flag | Evidence | Next step |",
        "|---|---|---|---|---|---|---|---|---|",
    ]

    if not findings:
        lines.append("| Info | owner_review | all | all | all | all | no_material_local_blockers | local fields and evidence paths | Authorized owner should verify state-specific procedure before filing or hearing. |")
    else:
        for finding in findings:
            lines.append(
                f"| {finding.severity} | {finding.action} | {finding.case_id} | {finding.state} | {finding.stage} | {finding.issue} | {finding.flag} | {finding.evidence} | {finding.next_step} |"
            )

    lines.extend(
        [
            "",
            "## Hearing Packet Checklist",
            "- Determination or decision notice",
            "- Appeal deadline and proof of timely filing",
            "- Hearing notice, call-in instructions, party list, and issue list",
            "- Hearing packet and all exhibits",
            "- Evidence exchanged to the hearing office and every listed party",
            "- Witness names, contact details, firsthand topics, and availability",
            "- Claimant or employer statement tied to the listed issue",
            "- Weekly certifications, work-search logs, payment history, or affected weeks when applicable",
            "- Delivery proof and numbered exhibit pages",
            "",
            "## Guardrails",
            "- This report is not legal advice and does not decide eligibility or hearing outcomes.",
            "- Redact SSNs, claimant IDs, portal credentials, bank data, full medical details, and unrelated personal facts.",
            "- Do not file, upload, withdraw, request subpoenas, contact an agency or employer, or join hearings from this workflow.",
        ]
    )

    if sensitive:
        lines.extend(
            [
                "",
                "## Sensitive Filename Review",
                "The following filenames appear to contain sensitive labels. Rename or redact before sharing:",
            ]
        )
        lines.extend(f"- {path}" for path in sensitive)

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", required=True, type=Path, help="CSV or JSON appeal cases")
    parser.add_argument("--evidence-dir", type=Path, default=Path("."), help="Directory of redacted evidence files")
    parser.add_argument("--today", default=date.today().isoformat(), help="Review date, YYYY-MM-DD")
    args = parser.parse_args()

    today = parse_date(args.today)
    if today is None:
        raise ValueError("--today is required")

    cases = read_cases(args.cases)
    evidence = evidence_index(args.evidence_dir)
    findings: list[Finding] = []
    for case in cases:
        findings.extend(evaluate(case, evidence, today))

    sensitive = sensitive_hits(evidence)
    print(render(findings, cases, today, sensitive))
    return 2 if any(finding.severity == "Blocker" for finding in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
