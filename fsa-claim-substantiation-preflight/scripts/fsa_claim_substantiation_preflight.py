#!/usr/bin/env python3
"""Preflight FSA/HRA/HSA claim substantiation packets before submission."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path


TRUE_VALUES = {"1", "true", "yes", "y", "present", "provided", "attached", "complete", "signed"}
FALSE_VALUES = {"0", "false", "no", "n", "missing", "none", "unknown", ""}
EVIDENCE_KEYWORDS = {
    "eob": ("eob", "explanation", "benefits"),
    "itemized_receipt": ("receipt", "invoice", "statement", "superbill"),
    "letter_of_medical_necessity": ("lmn", "medical_necessity", "necessity"),
    "prescription_present": ("prescription", "rx"),
    "provider_certification": ("certification", "signature", "signed"),
    "provider_tax_id": ("tin", "tax", "ssn", "ein"),
    "deductible_met_date": ("deductible", "hdhp"),
}
LMN_EXPENSE_TERMS = (
    "fitness",
    "gym",
    "wellness",
    "massage",
    "vitamin",
    "supplement",
    "weight_loss",
    "special_food",
    "compounded",
)
PRESCRIPTION_REVIEW_TERMS = ("rx", "prescription", "medication", "medicine", "drug")


@dataclass(frozen=True)
class Claim:
    row_number: int
    claim_id: str
    account_type: str
    expense_type: str
    service_date: date | None
    purchase_date: date | None
    amount: Decimal
    patient_name: str
    dependent_name: str
    provider_name: str
    coverage_start: date | None
    coverage_end: date | None
    claim_deadline: date | None
    fields: dict[str, str]


@dataclass(frozen=True)
class Finding:
    claim: Claim
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


def parse_decimal(value: object) -> Decimal:
    raw = str(value or "").strip().replace("$", "").replace(",", "")
    if not raw:
        return Decimal("0")
    try:
        return Decimal(raw)
    except InvalidOperation:
        return Decimal("0")


def money(value: Decimal) -> str:
    return f"USD {value:.2f}"


def load_rows(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        raise SystemExit(f"Claims file not found: {path}")
    if path.suffix.lower() == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            for key in ("claims", "rows", "expenses", "reimbursements"):
                if isinstance(payload.get(key), list):
                    return list(payload[key])
            raise SystemExit("JSON input must contain claims, rows, expenses, or reimbursements.")
        if isinstance(payload, list):
            return list(payload)
        raise SystemExit("JSON input must be a list or an object containing claim rows.")
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def parse_claims(path: Path) -> list[Claim]:
    claims: list[Claim] = []
    for offset, raw in enumerate(load_rows(path), start=2):
        row = {str(key).strip().lower(): str(value or "").strip() for key, value in dict(raw).items()}
        claim_id = row.get("claim_id") or row.get("id") or row.get("expense_id") or f"row-{offset}"
        claims.append(
            Claim(
                row_number=offset,
                claim_id=claim_id,
                account_type=norm(row.get("account_type") or row.get("plan_type") or "health_fsa"),
                expense_type=norm(row.get("expense_type") or row.get("category") or row.get("description")),
                service_date=parse_date(row.get("service_date") or row.get("care_date") or row.get("date_of_service")),
                purchase_date=parse_date(row.get("purchase_date") or row.get("payment_date")),
                amount=parse_decimal(row.get("amount") or row.get("claim_amount")),
                patient_name=row.get("patient_name") or row.get("member_name") or "",
                dependent_name=row.get("dependent_name") or row.get("care_recipient") or "",
                provider_name=row.get("provider_name") or row.get("merchant") or row.get("care_provider") or "",
                coverage_start=parse_date(row.get("coverage_start") or row.get("plan_start")),
                coverage_end=parse_date(row.get("coverage_end") or row.get("plan_end")),
                claim_deadline=parse_date(row.get("claim_deadline") or row.get("runout_deadline") or row.get("deadline")),
                fields=row,
            )
        )
    if not claims:
        raise SystemExit("No FSA claim rows found.")
    return claims


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


def has_field_or_evidence(claim: Claim, key: str, evidence: dict[str, list[str]]) -> bool:
    if truthy(claim.fields.get(key, "")):
        return True
    claim_id = claim.claim_id.lower()
    return any(
        claim_id in filename and any(keyword in filename for keyword in EVIDENCE_KEYWORDS.get(key, ()))
        for filename in evidence
    )


def evidence_list(claim: Claim, evidence: dict[str, list[str]]) -> str:
    claim_id = claim.claim_id.lower()
    matched = [name for name in sorted(evidence) if claim_id in name]
    return ", ".join(matched[:4]) if matched else "no matching local evidence files"


def add(
    findings: list[Finding],
    claim: Claim,
    severity: str,
    action: str,
    flag: str,
    evidence: str,
    next_step: str,
) -> None:
    findings.append(Finding(claim, severity, action, flag, evidence, next_step))


def receipt_fields_complete(claim: Claim) -> bool:
    required = (
        "receipt_has_provider",
        "receipt_has_service_date",
        "receipt_has_description",
        "receipt_has_amount",
    )
    person_present = truthy(claim.fields.get("receipt_has_patient")) or bool(claim.patient_name or claim.dependent_name)
    return person_present and all(truthy(claim.fields.get(key)) for key in required)


def analyze_claim(claim: Claim, evidence: dict[str, list[str]], today: date) -> list[Finding]:
    findings: list[Finding] = []
    local_evidence = evidence_list(claim, evidence)
    account = claim.account_type
    expense = claim.expense_type
    is_dependent_care = "dependent" in account or "dcfsa" in account or "care" in account and "fsa" in account
    is_lp_fsa = "limited" in account or "lpfsa" in account or "lex" in account

    if truthy(claim.fields.get("live_portal_action_requested")):
        add(
            findings,
            claim,
            "blocker",
            "portal_guardrail",
            "live_portal_action_requested",
            local_evidence,
            "Prepare a packet only; a human authorized owner must submit, appeal, repay, or edit live portal records.",
        )

    if claim.claim_deadline is None:
        add(
            findings,
            claim,
            "review",
            "deadline_escalation",
            "missing_claim_deadline",
            "No claim_deadline or runout_deadline provided.",
            "Check the plan document or administrator notice before waiting on nonessential documents.",
        )
    else:
        days_left = (claim.claim_deadline - today).days
        if days_left < 0:
            add(
                findings,
                claim,
                "blocker",
                "deadline_escalation",
                "claim_deadline_passed",
                f"Deadline {claim.claim_deadline.isoformat()} is {abs(days_left)} days past {today.isoformat()}.",
                "Ask the administrator about late claim, appeal, correction, or repayment options before resubmission.",
            )
        elif days_left <= 14:
            add(
                findings,
                claim,
                "review",
                "deadline_escalation",
                "claim_deadline_within_14_days",
                f"Deadline {claim.claim_deadline.isoformat()} is {days_left} days away.",
                "Use an owner/date checklist and prioritize required substantiation over optional context.",
            )

    service_date = claim.service_date or claim.purchase_date
    if not service_date:
        add(
            findings,
            claim,
            "blocker",
            "hold_claim",
            "missing_service_date",
            local_evidence,
            "Add a date of service or dependent-care date; payment date alone is not enough for packet readiness.",
        )
    elif (claim.coverage_start and service_date < claim.coverage_start) or (
        claim.coverage_end and service_date > claim.coverage_end
    ):
        add(
            findings,
            claim,
            "blocker",
            "hold_claim",
            "service_date_outside_coverage_period",
            f"Service date {service_date.isoformat()} is outside {claim.coverage_start} to {claim.coverage_end}.",
            "Verify coverage period, grace period, carryover, or plan-specific exception before submitting.",
        )

    if is_dependent_care:
        if not claim.dependent_name:
            add(
                findings,
                claim,
                "blocker",
                "hold_claim",
                "dependent_name_missing",
                local_evidence,
                "Add the dependent or care recipient name required by the claim form.",
            )
        if not claim.provider_name:
            add(
                findings,
                claim,
                "blocker",
                "provider_document_request",
                "provider_name_missing",
                local_evidence,
                "Add caregiver or facility name before resubmission.",
            )
        if not has_field_or_evidence(claim, "provider_certification", evidence):
            add(
                findings,
                claim,
                "blocker",
                "provider_document_request",
                "dependent_care_certification_missing",
                local_evidence,
                "Get a provider-signed certification or compliant itemized dependent-care statement.",
            )
        if not truthy(claim.fields.get("provider_tax_id")) and not has_field_or_evidence(claim, "provider_tax_id", evidence):
            add(
                findings,
                claim,
                "review",
                "provider_document_request",
                "dependent_care_provider_tax_id_missing",
                local_evidence,
                "Check whether the plan form requires provider SSN/TIN/EIN or acceptable unavailable-provider handling.",
            )
        if not truthy(claim.fields.get("work_related_care")):
            add(
                findings,
                claim,
                "review",
                "benefits_owner_review",
                "work_related_care_context_missing",
                local_evidence,
                "Add the plan-required work-related-care context or route to the benefits owner.",
            )
    else:
        if truthy(claim.fields.get("insurance_involved")) and not has_field_or_evidence(claim, "eob", evidence):
            add(
                findings,
                claim,
                "blocker",
                "hold_claim",
                "missing_eob_for_insured_service",
                local_evidence,
                "Add the EOB or plan statement showing insurance processing and patient responsibility.",
            )
        if not has_field_or_evidence(claim, "itemized_receipt", evidence):
            add(
                findings,
                claim,
                "blocker",
                "hold_claim",
                "missing_itemized_receipt",
                local_evidence,
                "Add an itemized receipt or provider statement; payment proof alone is not enough.",
            )
        elif not receipt_fields_complete(claim):
            add(
                findings,
                claim,
                "blocker",
                "employee_correction",
                "receipt_missing_required_fields",
                local_evidence,
                "Receipt should show patient, provider, service date, description, and amount.",
            )

    if truthy(claim.fields.get("payment_proof_only")):
        add(
            findings,
            claim,
            "blocker",
            "hold_claim",
            "payment_proof_only_not_enough",
            local_evidence,
            "Replace card/bank proof with itemized substantiation or EOB support.",
        )

    lmn_needed = any(term in expense for term in LMN_EXPENSE_TERMS) or truthy(claim.fields.get("letter_of_medical_necessity_required"))
    if lmn_needed:
        lmn_expiration = parse_date(claim.fields.get("lmn_expiration"))
        if not has_field_or_evidence(claim, "letter_of_medical_necessity", evidence):
            add(
                findings,
                claim,
                "blocker",
                "provider_document_request",
                "lmn_required_or_expired",
                local_evidence,
                "Get a current provider-signed LMN that matches the claimed item or service.",
            )
        elif lmn_expiration and lmn_expiration < today:
            add(
                findings,
                claim,
                "blocker",
                "provider_document_request",
                "lmn_required_or_expired",
                f"LMN expiration {lmn_expiration.isoformat()} is before {today.isoformat()}.",
                "Request an updated LMN before resubmission.",
            )

    if truthy(claim.fields.get("prescription_required")) and not has_field_or_evidence(
        claim, "prescription_present", evidence
    ):
        add(
            findings,
            claim,
            "blocker",
            "provider_document_request",
            "prescription_support_missing",
            local_evidence,
            "Attach the required prescription or route to provider/benefits owner review.",
        )
    elif any(term in expense for term in PRESCRIPTION_REVIEW_TERMS) and not truthy(claim.fields.get("prescription_present")):
        add(
            findings,
            claim,
            "review",
            "benefits_owner_review",
            "prescription_or_plan_rule_review",
            local_evidence,
            "Check the plan category and current administrator instructions for prescription or OTC support.",
        )

    if is_lp_fsa and not ("dental" in expense or "vision" in expense):
        if not claim.fields.get("deductible_met_date") and not has_field_or_evidence(claim, "deductible_met_date", evidence):
            add(
                findings,
                claim,
                "review",
                "benefits_owner_review",
                "lpfsa_deductible_timing_review",
                local_evidence,
                "LPFSA medical claims usually need plan-specific post-deductible support or owner review.",
            )

    if truthy(claim.fields.get("already_reimbursed")):
        add(
            findings,
            claim,
            "blocker",
            "hold_claim",
            "possible_double_reimbursement",
            local_evidence,
            "Explain prior reimbursement, offset, or exclusion before resubmitting the same expense.",
        )

    if truthy(claim.fields.get("paid_by_debit_card")) and not findings:
        add(
            findings,
            claim,
            "info",
            "benefits_owner_review",
            "debit_card_substantiation_archive",
            local_evidence,
            "Keep itemized receipt/EOB in case the administrator asks for debit-card substantiation.",
        )

    return findings


def duplicate_findings(claims: list[Claim], evidence: dict[str, list[str]]) -> list[Finding]:
    keys = Counter(
        (
            norm(claim.patient_name or claim.dependent_name),
            claim.service_date.isoformat() if claim.service_date else "",
            norm(claim.provider_name),
            f"{claim.amount:.2f}",
            claim.expense_type,
        )
        for claim in claims
        if claim.amount > 0
    )
    findings: list[Finding] = []
    for claim in claims:
        key = (
            norm(claim.patient_name or claim.dependent_name),
            claim.service_date.isoformat() if claim.service_date else "",
            norm(claim.provider_name),
            f"{claim.amount:.2f}",
            claim.expense_type,
        )
        if keys[key] > 1:
            add(
                findings,
                claim,
                "blocker",
                "hold_claim",
                "possible_duplicate_claim",
                evidence_list(claim, evidence),
                "Confirm this expense was not submitted or reimbursed twice before resubmission.",
            )
    return findings


def analyze_claims(claims: list[Claim], evidence: dict[str, list[str]], today: date) -> list[Finding]:
    findings = duplicate_findings(claims, evidence)
    for claim in claims:
        findings.extend(analyze_claim(claim, evidence, today))
    return findings


def render_report(claims: list[Claim], findings: list[Finding], today: date) -> str:
    blockers = [finding for finding in findings if finding.severity == "blocker"]
    reviews = [finding for finding in findings if finding.severity == "review"]
    if blockers:
        decision = "Hold claim packet pending evidence repair"
    elif reviews:
        decision = "Review before submission"
    else:
        decision = "Packet appears ready for authorized owner review"

    lines = [
        "## FSA Claim Substantiation Decision",
        decision,
        "",
        "## Packet Summary",
        (
            f"Review date: {today.isoformat()}. Claims reviewed: {len(claims)}. "
            f"Blockers: {len(blockers)}. Review items: {len(reviews)}."
        ),
        "",
        "## Findings",
        "| Severity | Action | Claim | Account | Expense | Amount | Flag | Evidence | Next step |",
        "|---|---|---|---|---|---:|---|---|---|",
    ]
    if findings:
        for finding in findings:
            claim = finding.claim
            lines.append(
                "| "
                + " | ".join(
                    [
                        finding.severity,
                        finding.action,
                        claim.claim_id,
                        claim.account_type,
                        claim.expense_type or "unknown",
                        money(claim.amount),
                        finding.flag,
                        finding.evidence.replace("|", "/"),
                        finding.next_step.replace("|", "/"),
                    ]
                )
                + " |"
            )
    else:
        lines.append("| info | owner_review | all | all | all | USD 0.00 | no_material_packet_gaps | supplied fields | Archive evidence and submit only through an authorized owner. |")

    lines.extend(
        [
            "",
            "## Correction Checklist",
            "- Add EOBs or plan statements when insurance processed the service.",
            "- Replace card/bank payment proof with itemized receipt or provider statement.",
            "- Confirm receipt fields: patient/dependent, provider, service/care date, description, and amount.",
            "- Add current LMN, prescription, dependent-care certification, TIN, deductible support, or plan-owner notes when relevant.",
            "- Check coverage period, runout deadline, and duplicate reimbursement status before resubmission.",
            "",
            "## Guardrails",
            "Administrative packet-readiness support only. No tax, legal, medical, payroll, plan-design, portal-submission, repayment, or reimbursement decision is made here.",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claims", required=True, type=Path, help="CSV or JSON claim rows.")
    parser.add_argument("--evidence-dir", type=Path, help="Optional local evidence directory.")
    parser.add_argument("--today", default=date.today().isoformat(), help="Review date in YYYY-MM-DD format.")
    parser.add_argument("--output", type=Path, help="Optional report output path.")
    args = parser.parse_args(argv)

    today = parse_date(args.today)
    if today is None:
        raise SystemExit("--today must be a valid date.")

    claims = parse_claims(args.claims)
    evidence = collect_evidence(args.evidence_dir)
    findings = analyze_claims(claims, evidence, today)
    report = render_report(claims, findings, today)

    if args.output:
        args.output.write_text(report + "\n", encoding="utf-8")
    print(report)
    return 2 if any(finding.severity == "blocker" for finding in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
