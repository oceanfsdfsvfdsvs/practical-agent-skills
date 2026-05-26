#!/usr/bin/env python3
"""Preflight patient medical bills against insurance EOBs before payment or dispute."""

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


TRUE_VALUES = {"1", "true", "yes", "y", "processed", "complete", "itemized"}
FALSE_VALUES = {"0", "false", "no", "n", "unprocessed", "pending", "missing", ""}
DEFAULT_POLICY = {
    "balance_tolerance": "1.00",
    "financial_assistance_balance_over": "1000.00",
    "surprise_facility_types": ["emergency", "in_network_hospital", "hospital_outpatient"],
    "facility_based_terms": [
        "anesthesia",
        "radiology",
        "pathology",
        "lab",
        "assistant surgeon",
        "hospitalist",
        "intensivist",
        "neonatology",
    ],
}


@dataclass(frozen=True)
class BillRow:
    row_number: int
    bill_id: str
    provider: str
    service_date: date | None
    cpt: str
    description: str
    charge: Decimal
    patient_balance: Decimal
    insurance_processed: bool
    network_status: str
    facility_type: str
    itemized: bool
    notes: str


@dataclass(frozen=True)
class EobRow:
    row_number: int
    claim_id: str
    provider: str
    service_date: date | None
    cpt: str
    description: str
    allowed_amount: Decimal
    plan_paid: Decimal
    patient_responsibility: Decimal
    denial_code: str
    denial_reason: str
    network_status: str


@dataclass(frozen=True)
class Finding:
    row: BillRow
    risk: str
    action: str
    flag: str
    evidence: str
    next_step: str


def norm(value: object) -> str:
    return " ".join(str(value or "").strip().lower().split())


def parse_bool(value: object) -> bool:
    raw = norm(value)
    if raw in TRUE_VALUES:
        return True
    if raw in FALSE_VALUES:
        return False
    return False


def parse_decimal(value: object) -> Decimal:
    raw = str(value or "").strip().replace(",", "").replace("$", "")
    if not raw:
        return Decimal("0")
    try:
        return Decimal(raw)
    except InvalidOperation:
        return Decimal("0")


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


def money(value: Decimal, currency: str = "USD") -> str:
    return f"{currency} {value:.2f}"


def load_records(path: Path, keys: tuple[str, ...]) -> list[dict[str, object]]:
    if not path.exists():
        raise SystemExit(f"Input file not found: {path}")
    if path.suffix.lower() == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            for key in keys:
                if isinstance(payload.get(key), list):
                    return list(payload[key])
            raise SystemExit(f"JSON input must contain one of: {', '.join(keys)}.")
        if isinstance(payload, list):
            return list(payload)
        raise SystemExit("JSON input must be a list or an object containing rows.")
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_policy(path: Path | None) -> dict[str, object]:
    policy = dict(DEFAULT_POLICY)
    if not path:
        return policy
    if not path.exists():
        raise SystemExit(f"Policy file not found: {path}")
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise SystemExit("Policy JSON must be an object.")
    policy.update(loaded)
    return policy


def parse_bills(path: Path) -> list[BillRow]:
    rows: list[BillRow] = []
    for offset, raw in enumerate(load_records(path, ("bills", "rows", "statements")), start=2):
        row = {str(key).strip().lower(): value for key, value in dict(raw).items()}
        rows.append(
            BillRow(
                row_number=offset,
                bill_id=str(row.get("bill_id") or row.get("account") or row.get("statement_id") or "").strip(),
                provider=str(row.get("provider") or row.get("facility") or row.get("billing_entity") or "").strip(),
                service_date=parse_date(row.get("service_date") or row.get("date_of_service") or row.get("date")),
                cpt=str(row.get("cpt") or row.get("hcpcs") or row.get("code") or "").strip(),
                description=str(row.get("description") or row.get("service") or "").strip(),
                charge=parse_decimal(row.get("charge") or row.get("billed_amount")),
                patient_balance=parse_decimal(row.get("patient_balance") or row.get("balance") or row.get("amount_due")),
                insurance_processed=parse_bool(row.get("insurance_processed") or row.get("insurance_status")),
                network_status=norm(row.get("network_status") or row.get("network")),
                facility_type=norm(row.get("facility_type") or row.get("setting")),
                itemized=parse_bool(row.get("itemized") or row.get("itemized_bill")),
                notes=str(row.get("notes") or row.get("memo") or "").strip(),
            )
        )
    if not rows:
        raise SystemExit("No medical bill rows found.")
    return rows


def parse_eob(path: Path | None) -> list[EobRow]:
    if not path:
        return []
    rows: list[EobRow] = []
    for offset, raw in enumerate(load_records(path, ("eob", "claims", "rows")), start=2):
        row = {str(key).strip().lower(): value for key, value in dict(raw).items()}
        rows.append(
            EobRow(
                row_number=offset,
                claim_id=str(row.get("claim_id") or row.get("eob_id") or "").strip(),
                provider=str(row.get("provider") or row.get("facility") or "").strip(),
                service_date=parse_date(row.get("service_date") or row.get("date_of_service") or row.get("date")),
                cpt=str(row.get("cpt") or row.get("hcpcs") or row.get("code") or "").strip(),
                description=str(row.get("description") or row.get("service") or "").strip(),
                allowed_amount=parse_decimal(row.get("allowed_amount") or row.get("allowed")),
                plan_paid=parse_decimal(row.get("plan_paid") or row.get("paid_by_plan")),
                patient_responsibility=parse_decimal(
                    row.get("patient_responsibility") or row.get("member_responsibility") or row.get("you_owe")
                ),
                denial_code=str(row.get("denial_code") or row.get("remark_code") or "").strip(),
                denial_reason=str(row.get("denial_reason") or row.get("remarks") or "").strip(),
                network_status=norm(row.get("network_status") or row.get("network")),
            )
        )
    return rows


def match_key(provider: str, service_date: date | None, cpt: str) -> tuple[str, str, str]:
    return (norm(provider), service_date.isoformat() if service_date else "", norm(cpt))


def duplicate_key(row: BillRow) -> tuple[str, str, str, str]:
    return (
        norm(row.provider),
        row.service_date.isoformat() if row.service_date else "",
        norm(row.cpt),
        f"{row.charge:.2f}",
    )


def as_decimal(policy: dict[str, object], key: str) -> Decimal:
    return parse_decimal(policy.get(key))


def as_set(policy: dict[str, object], key: str) -> set[str]:
    value = policy.get(key, [])
    if not isinstance(value, list):
        return set()
    return {norm(item) for item in value}


def classify(bills: list[BillRow], eobs: list[EobRow], policy: dict[str, object]) -> list[Finding]:
    tolerance = as_decimal(policy, "balance_tolerance")
    assistance_threshold = as_decimal(policy, "financial_assistance_balance_over")
    surprise_facility_types = as_set(policy, "surprise_facility_types")
    facility_based_terms = as_set(policy, "facility_based_terms")
    eob_by_key = {match_key(eob.provider, eob.service_date, eob.cpt): eob for eob in eobs}
    duplicate_counts = Counter(duplicate_key(row) for row in bills if row.charge > 0)
    findings: list[Finding] = []

    def add(row: BillRow, risk: str, action: str, flag: str, evidence: str, next_step: str) -> None:
        findings.append(Finding(row, risk, action, flag, evidence, next_step))

    for row in bills:
        eob = eob_by_key.get(match_key(row.provider, row.service_date, row.cpt))
        text = norm(f"{row.provider} {row.description} {row.notes}")

        if not row.itemized or not row.cpt or not row.service_date:
            add(
                row,
                "medium",
                "request_itemized_bill",
                "request_itemized_bill",
                "Bill line lacks CPT/HCPCS, service date, or itemized support.",
                "Request an itemized bill or superbill with codes, dates, quantities, and charges.",
            )

        if duplicate_counts[duplicate_key(row)] > 1:
            add(
                row,
                "high",
                "hold_payment",
                "duplicate_bill_line",
                "Same provider, service date, CPT, and charge appears more than once.",
                "Ask provider billing to confirm whether this is a duplicate statement or a separate claim.",
            )

        if not eob and (not row.insurance_processed or row.patient_balance > 0):
            add(
                row,
                "high",
                "hold_payment",
                "missing_eob_or_unprocessed_insurance",
                "Insurance is marked unprocessed or no matching EOB line was found.",
                "Ask provider to submit or correct the claim and ask insurer whether an EOB is pending.",
            )
        elif eob:
            if row.patient_balance > eob.patient_responsibility + tolerance:
                add(
                    row,
                    "high",
                    "hold_payment",
                    "balance_exceeds_eob_patient_responsibility",
                    f"Bill balance {money(row.patient_balance)} exceeds EOB responsibility {money(eob.patient_responsibility)}.",
                    "Ask provider billing to reconcile the account to the EOB before payment.",
                )
            if eob.denial_code or eob.denial_reason:
                denial = " ".join(part for part in (eob.denial_code, eob.denial_reason) if part)
                add(
                    row,
                    "high",
                    "appeal_review",
                    "appeal_review",
                    f"EOB denial or remark: {denial}.",
                    "Ask insurer for appeal procedure, deadline, and required evidence.",
                )
            if row.network_status and eob.network_status and row.network_status != eob.network_status:
                add(
                    row,
                    "medium",
                    "provider_insurer_reconciliation",
                    "network_status_mismatch",
                    f"Bill network status is {row.network_status}; EOB network status is {eob.network_status}.",
                    "Ask provider and insurer to confirm network status and claim processing.",
                )

        surprise_context = row.facility_type in surprise_facility_types or "surprise" in text or "balance bill" in text
        facility_based = any(term and term in text for term in facility_based_terms)
        out_of_network = "out" in row.network_status
        if out_of_network and (surprise_context or facility_based):
            add(
                row,
                "high",
                "no_surprises_review",
                "no_surprises_review",
                "Out-of-network emergency or facility-based billing clue appears in the bill data.",
                "Review No Surprises Act or state insurance department complaint path before paying disputed balance.",
            )

        if assistance_threshold and row.patient_balance >= assistance_threshold:
            add(
                row,
                "medium",
                "financial_assistance_review",
                "financial_assistance_review",
                f"Patient balance {money(row.patient_balance)} meets or exceeds configured assistance threshold.",
                "Ask provider about financial assistance, charity care, self-pay discount, or payment-plan screening.",
            )

    return findings


def render(bills: list[BillRow], eobs: list[EobRow], findings: list[Finding]) -> str:
    hold_count = sum(1 for finding in findings if finding.action in {"hold_payment", "no_surprises_review", "appeal_review"})
    review_count = len(findings) - hold_count
    if hold_count:
        decision = "Hold payment pending reconciliation: high-risk billing exceptions need written clarification before payment."
    elif review_count:
        decision = "Review before paying: administrative or affordability exceptions need owner disposition."
    else:
        decision = "No material billing exceptions found."

    lines = [
        "## Medical Bill Dispute Decision",
        decision,
        "",
        "## Exception Summary",
        f"- Bill rows reviewed: {len(bills)}",
        f"- EOB rows reviewed: {len(eobs)}",
        f"- Hold exceptions: {hold_count}",
        f"- Review exceptions: {review_count}",
        "",
        "## Billing Exceptions",
        "| Risk | Action | Row | Provider | Service date | CPT | Balance | Flag | Evidence | Next step |",
        "|---|---|---:|---|---|---|---:|---|---|---|",
    ]
    if not findings:
        lines.append(
            "| low | payable_after_archive | - | - | - | - | - | none | No bill/EOB mismatch detected. | Archive bill, EOB, and payment confirmation. |"
        )
    else:
        for finding in findings:
            row = finding.row
            lines.append(
                "| {risk} | {action} | {row_number} | {provider} | {service_date} | {cpt} | {balance} | {flag} | {evidence} | {next_step} |".format(
                    risk=finding.risk,
                    action=finding.action,
                    row_number=row.row_number,
                    provider=row.provider or "-",
                    service_date=row.service_date.isoformat() if row.service_date else "-",
                    cpt=row.cpt or "-",
                    balance=money(row.patient_balance),
                    flag=finding.flag,
                    evidence=finding.evidence,
                    next_step=finding.next_step,
                )
            )
    lines.extend(
        [
            "",
            "## Dispute Packet Checklist",
            "- Itemized bill or superbill for flagged provider lines.",
            "- EOB for each claim and any reprocessed EOB versions.",
            "- Written provider reconciliation request for balances exceeding EOB responsibility.",
            "- Plan appeal instructions for denied or noncovered lines.",
            "- Call log with representative names, reference numbers, promised actions, and dates.",
            "- Financial assistance, charity-care, self-pay, or payment-plan application when affordability is the issue.",
            "",
            "## Guardrails",
            "- This is administrative and financial workflow support, not legal, medical, tax, credit-repair, or insurance-coverage advice.",
            "- Redact SSNs, full member IDs, payment card data, credentials, and unrelated clinical notes.",
            "- Do not submit complaints, appeals, payments, or portal messages without explicit authority.",
            "- Do not advise ignoring valid bills; seek written clarification for disputed balances and track follow-up dates.",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Preflight patient medical bills against insurance EOBs.")
    parser.add_argument("--bills", required=True, type=Path, help="CSV or JSON medical bill export.")
    parser.add_argument("--eob", type=Path, help="CSV or JSON EOB/claim export.")
    parser.add_argument("--policy", type=Path, help="Optional JSON policy thresholds.")
    args = parser.parse_args(argv)

    policy = load_policy(args.policy)
    bills = parse_bills(args.bills)
    eobs = parse_eob(args.eob)
    findings = classify(bills, eobs, policy)
    print(render(bills, eobs, findings))
    return 2 if any(finding.action in {"hold_payment", "no_surprises_review", "appeal_review"} for finding in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
