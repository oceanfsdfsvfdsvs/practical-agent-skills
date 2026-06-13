#!/usr/bin/env python3
"""Preflight workers' compensation denial packets before owner review."""

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
    "denial_letter": ("denial", "notice", "claim-denied", "rejection"),
    "incident_report": ("incident", "injury-report", "supervisor-notice", "first-report"),
    "medical_records": ("medical", "provider", "doctor", "clinic", "diagnosis", "treatment"),
    "work_restrictions": ("restriction", "light-duty", "work-status", "off-work"),
    "witness_statement": ("witness", "coworker", "supervisor", "statement"),
    "billing": ("bill", "eob", "invoice", "collection", "authorization"),
    "exchange_proof": ("exchange", "delivery", "served", "mailing", "receipt"),
}

SENSITIVE_FILENAME = re.compile(
    r"(token|secret|api[-_ ]?key|private[-_ ]?key|password|ssn|social[-_ ]?security|full[-_ ]?claim|"
    r"portal|login|full[-_ ]?medical|health[-_ ]?insurance[-_ ]?id|bank)",
    re.IGNORECASE,
)

CAUSATION_TERMS = (
    "not work",
    "not-work",
    "non work",
    "non-work",
    "work-related",
    "causation",
    "pre-existing",
    "preexisting",
    "prior condition",
    "medical evidence",
    "insufficient medical",
    "ime",
    "medical necessity",
    "treatment",
    "authorization",
)

EMPLOYER_DISPUTE_TERMS = ("late", "notice", "report", "employer", "dispute", "job duty", "scope")


@dataclass(frozen=True)
class CompCase:
    row_number: int
    case_id: str
    state: str
    worker_role: str
    injury_date: date | None
    report_date: date | None
    denial_date: date | None
    appeal_deadline: date | None
    hearing_date: date | None
    denial_reason: str
    denial_letter: bool
    incident_report: bool
    medical_records: bool
    medical_record_work_related: bool
    work_restrictions: bool
    witness_statement: bool
    employer_dispute: bool
    prior_condition_dispute: bool
    treatment_denied_or_bills: bool
    health_insurance_crossover: bool
    return_to_work_status: str
    evidence_exchanged_to_parties: bool
    live_action_requested: bool
    fields: dict[str, str]


@dataclass(frozen=True)
class Finding:
    severity: str
    action: str
    case_id: str
    state: str
    denial_reason: str
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
    return value.strip().lower() in {"yes", "y", "true", "1", "present", "available", "attached", "sent"}


def normalize_row(raw: dict[str, Any]) -> dict[str, str]:
    return {str(key): "" if value is None else str(value).strip() for key, value in raw.items()}


def case_from_row(raw: dict[str, Any], row_number: int) -> CompCase:
    row = normalize_row(raw)
    return CompCase(
        row_number=row_number,
        case_id=row.get("case_id") or f"row-{row_number}",
        state=row.get("state", ""),
        worker_role=row.get("worker_role", ""),
        injury_date=parse_date(row.get("injury_date", "")),
        report_date=parse_date(row.get("report_date", "")),
        denial_date=parse_date(row.get("denial_date", "")),
        appeal_deadline=parse_date(row.get("appeal_deadline", "")),
        hearing_date=parse_date(row.get("hearing_date", "")),
        denial_reason=row.get("denial_reason", ""),
        denial_letter=truthy(row.get("denial_letter", "")),
        incident_report=truthy(row.get("incident_report", "")),
        medical_records=truthy(row.get("medical_records", "")),
        medical_record_work_related=truthy(row.get("medical_record_work_related", "")),
        work_restrictions=truthy(row.get("work_restrictions", "")),
        witness_statement=truthy(row.get("witness_statement", "")),
        employer_dispute=truthy(row.get("employer_dispute", "")),
        prior_condition_dispute=truthy(row.get("prior_condition_dispute", "")),
        treatment_denied_or_bills=truthy(row.get("treatment_denied_or_bills", "")),
        health_insurance_crossover=truthy(row.get("health_insurance_crossover", "")),
        return_to_work_status=row.get("return_to_work_status", ""),
        evidence_exchanged_to_parties=truthy(row.get("evidence_exchanged_to_parties", "")),
        live_action_requested=truthy(row.get("live_action_requested", "")),
        fields=row,
    )


def read_cases(path: Path) -> list[CompCase]:
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            for key in ("cases", "claims", "appeals", "rows"):
                if key in data:
                    data = data[key]
                    break
        if not isinstance(data, list):
            raise ValueError("JSON input must be a list or contain cases, claims, appeals, or rows")
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


def evidence_present(case: CompCase, evidence: dict[str, list[Path]], evidence_type: str) -> tuple[bool, list[str]]:
    field_value = getattr(case, evidence_type, False)
    if isinstance(field_value, bool) and field_value:
        return True, [f"csv:{evidence_type}"]

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
    case: CompCase,
    flag: str,
    evidence: str,
    next_step: str,
) -> None:
    findings.append(
        Finding(
            severity=severity,
            action=action,
            case_id=case.case_id,
            state=case.state or "unknown",
            denial_reason=case.denial_reason or "missing",
            flag=flag,
            evidence=evidence,
            next_step=next_step,
        )
    )


def evaluate_case(case: CompCase, evidence: dict[str, list[Path]], today: date) -> list[Finding]:
    findings: list[Finding] = []

    denial_letter_present, denial_letter_hits = evidence_present(case, evidence, "denial_letter")
    incident_present, incident_hits = evidence_present(case, evidence, "incident_report")
    medical_present, medical_hits = evidence_present(case, evidence, "medical_records")
    restrictions_present, restriction_hits = evidence_present(case, evidence, "work_restrictions")
    witness_present, witness_hits = evidence_present(case, evidence, "witness_statement")

    if not case.denial_date:
        add(findings, "Blocker", "deadline_escalation", case, "denial_date_missing", "none", "Add the denial date from the written notice.")
    if not case.appeal_deadline:
        add(findings, "Blocker", "deadline_escalation", case, "appeal_deadline_missing", "none", "Add the notice deadline or have the authorized owner verify the applicable review window.")
    elif case.appeal_deadline < today:
        add(
            findings,
            "Blocker",
            "deadline_escalation",
            case,
            "appeal_deadline_passed",
            f"appeal_deadline={case.appeal_deadline.isoformat()}",
            "Ask the authorized owner to verify whether any reopening, good-cause, or alternative review path exists.",
        )
    elif (case.appeal_deadline - today).days <= 7:
        add(
            findings,
            "Review",
            "deadline_escalation",
            case,
            "appeal_deadline_near",
            f"appeal_deadline={case.appeal_deadline.isoformat()}",
            "Escalate deadline review before spending time on nonessential packet polish.",
        )

    if not denial_letter_present:
        add(findings, "Blocker", "hold_packet", case, "denial_letter_missing", "none", "Add the written denial letter or denial notice before final review.")
    if not case.denial_reason:
        add(findings, "Blocker", "hold_packet", case, "denial_reason_missing", "none", "Transcribe the denial reason exactly enough to map evidence gaps.")

    if case.injury_date and case.report_date and (case.report_date - case.injury_date).days > 3:
        add(
            findings,
            "Review",
            "employer_dispute_repair",
            case,
            "injury_report_delay_review",
            f"injury_date={case.injury_date.isoformat()}; report_date={case.report_date.isoformat()}",
            "Collect supervisor notice, contemporaneous notes, texts, emails, or witness support for reporting timeline review.",
        )

    causation_needed = (
        reason_contains(case.denial_reason, CAUSATION_TERMS)
        or case.prior_condition_dispute
        or case.treatment_denied_or_bills
    )
    if causation_needed and (not medical_present or not case.medical_record_work_related):
        add(
            findings,
            "Blocker",
            "medical_causation_repair",
            case,
            "medical_causation_evidence_missing",
            ", ".join(medical_hits) if medical_hits else "none",
            "Add provider record tying injury, work duties, treatment, and restrictions together; do not invent medical opinions.",
        )

    employer_dispute_needed = case.employer_dispute or reason_contains(case.denial_reason, EMPLOYER_DISPUTE_TERMS)
    if employer_dispute_needed and not incident_present:
        add(
            findings,
            "Blocker",
            "employer_dispute_repair",
            case,
            "incident_report_missing",
            ", ".join(incident_hits) if incident_hits else "none",
            "Add incident report, supervisor notice, or contemporaneous written report evidence.",
        )
    if employer_dispute_needed and not witness_present:
        add(
            findings,
            "Review",
            "employer_dispute_repair",
            case,
            "witness_statement_missing",
            ", ".join(witness_hits) if witness_hits else "none",
            "Capture firsthand witness name, role, availability, and what they personally observed.",
        )

    if not restrictions_present:
        add(
            findings,
            "Blocker",
            "medical_causation_repair",
            case,
            "work_restrictions_missing",
            ", ".join(restriction_hits) if restriction_hits else "none",
            "Add current work status or restriction note before return-to-work, wage-loss, or treatment review.",
        )

    if case.prior_condition_dispute and not case.fields.get("prior_condition_context", ""):
        add(
            findings,
            "Review",
            "medical_causation_repair",
            case,
            "prior_condition_context_missing",
            "csv:prior_condition_dispute",
            "Ask the authorized medical or legal owner what prior-condition context is relevant and safe to include.",
        )

    if case.treatment_denied_or_bills or case.health_insurance_crossover:
        billing_present, billing_hits = evidence_present(case, evidence, "billing")
        if not billing_present:
            add(
                findings,
                "Blocker",
                "billing_crossover_review",
                case,
                "billing_crossover_review",
                "none",
                "Add provider bill, EOB, authorization denial, collection notice, or timely-filing trail for owner review.",
            )
        else:
            add(
                findings,
                "Review",
                "billing_crossover_review",
                case,
                "billing_crossover_review",
                ", ".join(billing_hits),
                "Have the authorized owner verify provider, health-insurer, and workers' comp billing next steps.",
            )

    if case.hearing_date and not case.evidence_exchanged_to_parties:
        exchange_present, exchange_hits = evidence_present(case, evidence, "exchange_proof")
        if not exchange_present:
            add(
                findings,
                "Blocker",
                "evidence_exchange_repair",
                case,
                "evidence_not_exchanged_to_all_parties",
                "none",
                "Before hearing review, verify required evidence exchange and delivery proof with the authorized owner.",
            )

    if case.live_action_requested:
        add(
            findings,
            "Blocker",
            "hold_packet",
            case,
            "live_action_requested",
            "csv:live_action_requested",
            "Do not upload, file, call, message, or send anything; prepare an owner-reviewed packet only.",
        )

    return findings


def render_report(cases: list[CompCase], findings: list[Finding], today: date, sensitive: list[str]) -> str:
    blockers = [finding for finding in findings if finding.severity == "Blocker"]
    reviews = [finding for finding in findings if finding.severity != "Blocker"]
    if blockers:
        decision = "Hold packet pending evidence repair"
    elif reviews:
        decision = "Review before filing or hearing"
    else:
        decision = "Packet appears ready for authorized owner review"

    lines = [
        "## Workers' Comp Denial Decision",
        decision,
        "",
        "## Claim Summary",
        f"Review date: {today.isoformat()}. Cases reviewed: {len(cases)}. Blockers: {len(blockers)}. Reviews: {len(reviews)}.",
        "",
        "## Findings",
        "| Severity | Action | Case | State | Denial reason | Flag | Evidence | Next step |",
        "|---|---|---|---|---|---|---|---|",
    ]
    if findings:
        for finding in findings:
            lines.append(
                f"| {finding.severity} | {finding.action} | {finding.case_id} | {finding.state} | "
                f"{finding.denial_reason} | {finding.flag} | {finding.evidence} | {finding.next_step} |"
            )
    else:
        lines.append("| Info | owner_review | all | mixed | none | no_local_blockers_found | csv/evidence | Authorized owner should still verify state-specific procedure and facts. |")

    lines.extend(
        [
            "",
            "## Packet Checklist",
            "- Denial letter and denial reason captured.",
            "- Denial date, appeal deadline, hearing date if any, and review date explicit.",
            "- Incident report, supervisor notice, or reporting timeline proof attached when facts are disputed.",
            "- Medical record ties injury, work duties, treatment, and restrictions together when causation or treatment is disputed.",
            "- Witness names, role, firsthand basis, and availability captured when employer facts are disputed.",
            "- Bills, EOBs, authorization denials, and collection/timely-filing trail tracked when treatment or billing shifted.",
            "- Evidence exchange and delivery proof ready before hearing or appeal review.",
            "",
            "## Guardrails",
            "- This report does not decide compensability, give legal advice, give medical advice, file an appeal, contact an insurer, contact an employer, contact a provider, or contact an agency.",
            "- Redact SSNs, claim numbers, portal credentials, full medical histories, health insurance IDs, bank data, tax identifiers, and unrelated personal data.",
        ]
    )
    if sensitive:
        lines.extend(["", "## Sensitive Filename Review"])
        lines.extend(f"- Review and redact before sharing: {path}" for path in sensitive)

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", required=True, type=Path, help="CSV or JSON workers' comp denial case table.")
    parser.add_argument("--evidence-dir", type=Path, default=Path("."), help="Optional local evidence directory.")
    parser.add_argument("--today", default=date.today().isoformat(), help="Review date in YYYY-MM-DD format.")
    parser.add_argument("--output", type=Path, help="Optional Markdown report output path.")
    args = parser.parse_args()

    today = parse_date(args.today)
    if today is None:
        raise ValueError("--today is required")

    cases = read_cases(args.cases)
    evidence = evidence_index(args.evidence_dir)
    findings: list[Finding] = []
    for case in cases:
        findings.extend(evaluate_case(case, evidence, today))
    report = render_report(cases, findings, today, sensitive_hits(evidence))

    if args.output:
        args.output.write_text(report, encoding="utf-8")
    else:
        print(report, end="")

    return 2 if any(finding.severity == "Blocker" for finding in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
