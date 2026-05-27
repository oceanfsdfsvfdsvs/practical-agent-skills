#!/usr/bin/env python3
"""Preflight a homeowners or renters contents inventory before adjuster submission."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path


TRUE_VALUES = {"1", "true", "yes", "y", "scheduled"}
FALSE_VALUES = {"0", "false", "no", "n", ""}
MISSING_VALUES = {"", "none", "n/a", "na", "missing", "unknown", "tbd"}
DEFAULT_POLICY = {
    "coverage_limit": "0",
    "deductible": "0",
    "high_value_threshold": "1500.00",
    "receipt_required_over": "500.00",
    "quantity_review_threshold": 24,
    "special_sublimit_categories": [
        "jewelry",
        "firearms",
        "collectibles",
        "art",
        "cash",
        "silverware",
        "business equipment",
        "tools",
    ],
    "business_property_terms": ["business", "freelance", "home office", "client work"],
}


@dataclass(frozen=True)
class InventoryRow:
    row_number: int
    item_id: str
    room: str
    category: str
    description: str
    quantity: int
    claimed_replacement_cost: Decimal
    age_years: str
    condition: str
    ownership_evidence: str
    damage_evidence: str
    replacement_source: str
    serial_or_model: str
    scheduled_item: bool
    recovered_value: Decimal
    notes: str


@dataclass(frozen=True)
class Finding:
    row: InventoryRow
    risk: str
    action: str
    flag: str
    evidence: str
    next_step: str


def norm(value: object) -> str:
    return " ".join(str(value or "").strip().lower().split())


def display(value: str) -> str:
    return value.strip() or "-"


def parse_decimal(value: object) -> Decimal:
    raw = str(value or "").strip().replace(",", "").replace("$", "")
    if not raw:
        return Decimal("0")
    try:
        return Decimal(raw)
    except InvalidOperation:
        return Decimal("0")


def parse_int(value: object, default: int = 0) -> int:
    raw = str(value or "").strip()
    if not raw:
        return default
    try:
        return int(Decimal(raw))
    except InvalidOperation:
        return default


def parse_bool(value: object) -> bool:
    raw = norm(value)
    if raw in TRUE_VALUES:
        return True
    if raw in FALSE_VALUES:
        return False
    return False


def is_missing(value: object) -> bool:
    return norm(value) in MISSING_VALUES


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
        raise SystemExit("JSON input must be a list or an object containing inventory rows.")
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


def parse_inventory(path: Path) -> list[InventoryRow]:
    rows: list[InventoryRow] = []
    for offset, raw in enumerate(load_records(path, ("inventory", "items", "rows")), start=2):
        row = {str(key).strip().lower(): value for key, value in dict(raw).items()}
        quantity = parse_int(row.get("quantity") or row.get("qty"), default=1)
        if quantity < 1:
            quantity = 1
        rows.append(
            InventoryRow(
                row_number=offset,
                item_id=str(row.get("item_id") or row.get("id") or "").strip(),
                room=str(row.get("room") or row.get("location") or "").strip(),
                category=str(row.get("category") or row.get("type") or "").strip(),
                description=str(row.get("description") or row.get("item") or "").strip(),
                quantity=quantity,
                claimed_replacement_cost=parse_decimal(
                    row.get("claimed_replacement_cost") or row.get("replacement_cost") or row.get("claimed_amount")
                ),
                age_years=str(row.get("age_years") or row.get("age") or "").strip(),
                condition=str(row.get("condition") or "").strip(),
                ownership_evidence=str(row.get("ownership_evidence") or row.get("proof_owned") or "").strip(),
                damage_evidence=str(row.get("damage_evidence") or row.get("loss_evidence") or "").strip(),
                replacement_source=str(row.get("replacement_source") or row.get("value_source") or "").strip(),
                serial_or_model=str(row.get("serial_or_model") or row.get("model") or row.get("serial") or "").strip(),
                scheduled_item=parse_bool(row.get("scheduled_item") or row.get("scheduled")),
                recovered_value=parse_decimal(row.get("recovered_value") or row.get("salvage_value")),
                notes=str(row.get("notes") or row.get("memo") or "").strip(),
            )
        )
    if not rows:
        raise SystemExit("No inventory rows found.")
    return rows


def as_decimal(policy: dict[str, object], key: str) -> Decimal:
    return parse_decimal(policy.get(key))


def as_int(policy: dict[str, object], key: str) -> int:
    return parse_int(policy.get(key))


def as_set(policy: dict[str, object], key: str) -> set[str]:
    value = policy.get(key, [])
    if not isinstance(value, list):
        return set()
    return {norm(item) for item in value}


def duplicate_key(row: InventoryRow) -> tuple[str, str, str, str]:
    return (
        norm(row.room),
        norm(row.category),
        norm(row.description),
        f"{row.claimed_replacement_cost:.2f}",
    )


def classify(rows: list[InventoryRow], policy: dict[str, object]) -> list[Finding]:
    high_value_threshold = as_decimal(policy, "high_value_threshold")
    receipt_required_over = as_decimal(policy, "receipt_required_over")
    quantity_review_threshold = as_int(policy, "quantity_review_threshold")
    sublimit_categories = as_set(policy, "special_sublimit_categories")
    business_terms = as_set(policy, "business_property_terms")
    duplicate_counts = Counter(duplicate_key(row) for row in rows if row.description)
    findings: list[Finding] = []

    def add(row: InventoryRow, risk: str, action: str, flag: str, evidence: str, next_step: str) -> None:
        findings.append(Finding(row, risk, action, flag, evidence, next_step))

    for row in rows:
        text = norm(f"{row.category} {row.description} {row.notes}")
        high_value = row.claimed_replacement_cost >= high_value_threshold
        receipt_threshold = row.claimed_replacement_cost >= receipt_required_over

        if not row.room or not row.category or not row.description or row.claimed_replacement_cost <= 0:
            add(
                row,
                "high",
                "repair_core_fields",
                "missing_core_inventory_fields",
                "Room, category, description, quantity, or claimed replacement cost is missing.",
                "Complete core inventory fields before adjuster submission.",
            )

        if (high_value or receipt_threshold or row.scheduled_item) and is_missing(row.ownership_evidence):
            add(
                row,
                "high",
                "strengthen_ownership_evidence",
                "missing_ownership_evidence",
                "No ownership evidence for a high-value, scheduled, or receipt-threshold item.",
                "Add receipt, appraisal, dated photo/video, serial/model record, warranty, purchase-history export, or corroborating owner statement.",
            )

        if is_missing(row.damage_evidence):
            add(
                row,
                "medium",
                "add_damage_or_loss_evidence",
                "missing_damage_or_loss_evidence",
                "No damage photo, room-loss photo, theft report reference, restoration inventory, or total-loss context is listed.",
                "Attach loss-specific evidence and map it to this row or room.",
            )

        if receipt_threshold and is_missing(row.replacement_source):
            add(
                row,
                "medium",
                "support_replacement_cost",
                "request_replacement_cost_support",
                "Claimed replacement cost lacks receipt, quote, catalog page, model detail, or replacement source.",
                "Add a current equivalent, receipt, quote, purchase-history export, model detail, or explain the valuation source.",
            )

        if (receipt_threshold or high_value) and (is_missing(row.age_years) or is_missing(row.condition)):
            add(
                row,
                "medium",
                "review_depreciation_inputs",
                "missing_age_or_condition_for_acv_review",
                "Age or condition is missing for a material item.",
                "Fill age and condition so ACV/depreciation review is traceable.",
            )

        if row.scheduled_item or norm(row.category) in sublimit_categories:
            add(
                row,
                "high",
                "policy_sublimit_review",
                "policy_sublimit_or_scheduled_property_review",
                "Category, notes, or scheduled-item flag may trigger policy sublimit or endorsement review.",
                "Check declarations, endorsements, and sublimit pages before treating this as ordinary household contents.",
            )

        if any(term in text for term in business_terms):
            add(
                row,
                "medium",
                "policy_sublimit_review",
                "business_property_sublimit_review",
                "Category or notes suggest business, freelance, home-office, or client-work property.",
                "Separate the item for policy review and gather business-use context.",
            )

        if duplicate_counts[duplicate_key(row)] > 1:
            add(
                row,
                "medium",
                "dedupe_or_grouping_review",
                "possible_duplicate_inventory_row",
                "Another row has the same room, category, description, and claimed amount.",
                "Merge duplicates or explain why each row is a distinct item.",
            )

        if row.quantity >= quantity_review_threshold and row.claimed_replacement_cost < receipt_required_over:
            add(
                row,
                "low",
                "dedupe_or_grouping_review",
                "large_quantity_grouping_review",
                "Large quantity of lower-value household goods may be easier to review as a grouped line.",
                "Confirm insurer format; group or annotate quantity basis if appropriate.",
            )

        if row.recovered_value > 0 or any(term in text for term in {"salvage", "recovered", "repairable", "cleaned"}):
            add(
                row,
                "medium",
                "salvage_recovered_value_review",
                "salvage_or_recovered_value_review",
                "Recovered, repairable, cleaned, or salvageable value is present or implied.",
                "Add consistent notes for recovered value, repair status, and any claimed replacement amount.",
            )

    return findings


def render(rows: list[InventoryRow], findings: list[Finding], policy: dict[str, object]) -> str:
    claimed_total = sum((row.claimed_replacement_cost for row in rows), Decimal("0"))
    coverage_limit = as_decimal(policy, "coverage_limit")
    high_count = sum(1 for finding in findings if finding.risk == "high")
    review_count = sum(1 for finding in findings if finding.risk in {"medium", "low"})
    if high_count:
        decision = "Hold packet pending evidence repair"
    elif review_count:
        decision = "Review before adjuster submission"
    else:
        decision = "Inventory packet appears ready for adjuster review"

    coverage_note = "No contents coverage limit supplied."
    if coverage_limit > 0:
        coverage_note = (
            "Claimed total exceeds the provided contents limit; review policy limits and prioritization."
            if claimed_total > coverage_limit
            else "Claimed total is within the provided contents limit."
        )

    lines = [
        "## Contents Claim Decision",
        decision,
        "",
        "## Exception Summary",
        f"- Inventory rows reviewed: {len(rows)}",
        f"- Claimed replacement total: {money(claimed_total)}",
        f"- High-risk findings: {high_count}",
        f"- Review findings: {review_count}",
        f"- Coverage note: {coverage_note}",
        "",
        "## Inventory Exceptions",
    ]
    if findings:
        lines.append(
            "| Risk | Action | Row | Item | Room | Category | Claimed | Flag | Evidence | Next step |"
        )
        lines.append("|---|---|---:|---|---|---|---:|---|---|---|")
        for finding in findings:
            row = finding.row
            lines.append(
                "| "
                + " | ".join(
                    [
                        finding.risk,
                        finding.action,
                        str(row.row_number),
                        display(row.description),
                        display(row.room),
                        display(row.category),
                        money(row.claimed_replacement_cost),
                        finding.flag,
                        finding.evidence,
                        finding.next_step,
                    ]
                )
                + " |"
            )
    else:
        lines.append("No material preflight exceptions found. Use `ready_for_adjuster_review` for row-level status.")

    lines.extend(
        [
            "",
            "## Adjuster Packet Checklist",
            "- Contents inventory export mapped to insurer-required fields.",
            "- Photos, room walkthroughs, receipts, purchase history, appraisals, warranties, model/serial records, and replacement-cost support.",
            "- Policy declarations, personal-property limit, deductible, and sublimit or scheduled-property pages.",
            "- Damage/loss evidence linked to each item or room.",
            "- Communication log for adjuster requests, submitted files, response dates, and open questions.",
            "",
            "## Guardrails",
            "- This is evidence-readiness support, not legal, coverage, tax, construction, valuation, or public-adjuster advice.",
            "- Do not fabricate receipts, photos, purchase dates, model numbers, appraisals, or ownership stories.",
            "- Keep final coverage, settlement, proof-of-loss, complaint, and legal decisions with the insured or authorized professional.",
            "- Redact policy numbers, claim numbers, SSNs, payment data, credentials, and unrelated family records before sharing files with an agent.",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", required=True, type=Path, help="CSV or JSON contents inventory.")
    parser.add_argument("--policy", type=Path, help="Optional policy JSON with thresholds and category lists.")
    parser.add_argument("--output", type=Path, help="Optional Markdown report path.")
    args = parser.parse_args()

    policy = load_policy(args.policy)
    rows = parse_inventory(args.inventory)
    findings = classify(rows, policy)
    report = render(rows, findings, policy)

    if args.output:
        args.output.write_text(report + "\n", encoding="utf-8")
    else:
        print(report)

    return 2 if any(finding.risk == "high" for finding in findings) else (1 if findings else 0)


if __name__ == "__main__":
    raise SystemExit(main())
