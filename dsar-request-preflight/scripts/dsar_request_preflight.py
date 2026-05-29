#!/usr/bin/env python3
"""Preflight data subject access/deletion requests before privacy-team fulfillment."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path


DEFAULT_POLICY = {
    "default_sla_days": 30,
    "jurisdiction_sla_days": {
        "ca": 45,
        "california": 45,
        "ccpa": 45,
        "cpra": 45,
        "eu": 30,
        "eea": 30,
        "uk": 30,
        "gdpr": 30,
    },
    "due_soon_days": 7,
    "extension_review_days": 5,
    "sensitive_terms": ["minor", "child", "health", "biometric", "precise location", "ssn", "financial"],
    "deletion_exception_terms": ["tax", "fraud", "legal hold", "chargeback", "accounting", "security"],
}


@dataclass(frozen=True)
class RequestRow:
    row_number: int
    request_id: str
    received_date: date | None
    requester: str
    jurisdiction: str
    request_type: str
    identity_status: str
    authorized_agent: bool
    agent_proof: str
    scope: str
    match_keys: str
    sensitive_context: str
    notes: str


@dataclass(frozen=True)
class SystemRow:
    row_number: int
    system: str
    owner: str
    data_categories: set[str]
    match_keys: set[str]
    export_supported: bool
    deletion_supported: bool
    retention_lock: bool
    legal_hold: bool
    processor: str


@dataclass(frozen=True)
class Finding:
    request: RequestRow
    risk: str
    action: str
    flag: str
    evidence: str
    next_step: str


TRUE_VALUES = {"1", "true", "yes", "y", "supported", "complete", "verified"}
FALSE_VALUES = {"0", "false", "no", "n", "unsupported", "missing", "pending", ""}


def norm(value: object) -> str:
    return " ".join(str(value or "").strip().lower().split())


def split_terms(value: object) -> set[str]:
    raw = str(value or "").replace("|", ",").replace(";", ",")
    return {norm(part) for part in raw.split(",") if norm(part)}


def parse_bool(value: object) -> bool:
    raw = norm(value)
    if raw in TRUE_VALUES:
        return True
    if raw in FALSE_VALUES:
        return False
    return False


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
    policy["jurisdiction_sla_days"] = dict(DEFAULT_POLICY["jurisdiction_sla_days"])
    if not path:
        return policy
    if not path.exists():
        raise SystemExit(f"Policy file not found: {path}")
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise SystemExit("Policy JSON must be an object.")
    if isinstance(loaded.get("jurisdiction_sla_days"), dict):
        merged = dict(policy["jurisdiction_sla_days"])
        merged.update({norm(k): int(v) for k, v in loaded["jurisdiction_sla_days"].items()})
        loaded = dict(loaded)
        loaded["jurisdiction_sla_days"] = merged
    policy.update(loaded)
    return policy


def parse_requests(path: Path) -> list[RequestRow]:
    rows: list[RequestRow] = []
    for offset, raw in enumerate(load_records(path, ("requests", "rows", "dsars")), start=2):
        row = {str(key).strip().lower(): value for key, value in dict(raw).items()}
        rows.append(
            RequestRow(
                row_number=offset,
                request_id=str(row.get("request_id") or row.get("id") or f"row-{offset}").strip(),
                received_date=parse_date(row.get("received_date") or row.get("date_received") or row.get("created_at")),
                requester=str(row.get("requester") or row.get("email") or row.get("name") or "").strip(),
                jurisdiction=norm(row.get("jurisdiction") or row.get("region") or row.get("law")),
                request_type=norm(row.get("request_type") or row.get("type") or row.get("right")),
                identity_status=norm(row.get("identity_status") or row.get("verification_status")),
                authorized_agent=parse_bool(row.get("authorized_agent") or row.get("agent")),
                agent_proof=norm(row.get("agent_proof") or row.get("authorization_proof")),
                scope=str(row.get("scope") or row.get("systems") or row.get("data_scope") or "").strip(),
                match_keys=str(row.get("match_keys") or row.get("identifiers") or row.get("lookup_keys") or "").strip(),
                sensitive_context=str(row.get("sensitive_context") or row.get("sensitive_data") or "").strip(),
                notes=str(row.get("notes") or row.get("memo") or "").strip(),
            )
        )
    if not rows:
        raise SystemExit("No DSAR request rows found.")
    return rows


def parse_systems(path: Path) -> list[SystemRow]:
    rows: list[SystemRow] = []
    for offset, raw in enumerate(load_records(path, ("systems", "inventory", "rows")), start=2):
        row = {str(key).strip().lower(): value for key, value in dict(raw).items()}
        rows.append(
            SystemRow(
                row_number=offset,
                system=str(row.get("system") or row.get("name") or "").strip(),
                owner=str(row.get("owner") or row.get("team") or "").strip(),
                data_categories=split_terms(row.get("data_categories") or row.get("categories") or row.get("scope")),
                match_keys=split_terms(row.get("match_keys") or row.get("identifiers") or row.get("lookup_keys")),
                export_supported=parse_bool(row.get("export_supported") or row.get("access_export")),
                deletion_supported=parse_bool(row.get("deletion_supported") or row.get("delete_supported")),
                retention_lock=parse_bool(row.get("retention_lock") or row.get("retention_exception")),
                legal_hold=parse_bool(row.get("legal_hold")),
                processor=str(row.get("processor") or row.get("vendor") or "").strip(),
            )
        )
    if not rows:
        raise SystemExit("No system inventory rows found.")
    return rows


def sla_days(policy: dict[str, object], jurisdiction: str) -> int:
    mapping = policy.get("jurisdiction_sla_days", {})
    if isinstance(mapping, dict):
        for term in split_terms(jurisdiction):
            if term in mapping:
                return int(mapping[term])
        if jurisdiction in mapping:
            return int(mapping[jurisdiction])
    return int(policy.get("default_sla_days", 30))


def request_terms(request: RequestRow) -> set[str]:
    terms = split_terms(request.scope) | split_terms(request.match_keys)
    if not terms or "all" in terms or "full account" in terms:
        return {"all"}
    return terms


def system_matches(request: RequestRow, system: SystemRow) -> bool:
    terms = request_terms(request)
    if "all" in terms:
        return True
    return bool(terms & system.data_categories or terms & system.match_keys or norm(system.system) in terms)


def has_term(text: str, terms: object) -> bool:
    normalized = norm(text)
    values = terms if isinstance(terms, list) else []
    return any(norm(term) and norm(term) in normalized for term in values)


def add_finding(findings: list[Finding], request: RequestRow, risk: str, action: str, flag: str, evidence: str, next_step: str) -> None:
    findings.append(Finding(request, risk, action, flag, evidence, next_step))


def analyze(requests: list[RequestRow], systems: list[SystemRow], policy: dict[str, object], today: date) -> list[Finding]:
    findings: list[Finding] = []
    due_soon_days = int(policy.get("due_soon_days", 7))
    extension_review_days = int(policy.get("extension_review_days", 5))

    for request in requests:
        matched_systems = [system for system in systems if system_matches(request, system)]
        text_blob = " ".join(
            [request.request_type, request.scope, request.match_keys, request.sensitive_context, request.notes]
        )

        if not request.received_date:
            add_finding(
                findings,
                request,
                "high",
                "triage_blocker",
                "missing_received_date",
                "No received date was provided, so the response deadline cannot be calculated.",
                "Confirm the intake timestamp before assigning SLA or closing the request.",
            )
        else:
            due_date = request.received_date + timedelta(days=sla_days(policy, request.jurisdiction))
            days_left = (due_date - today).days
            if days_left < 0:
                add_finding(
                    findings,
                    request,
                    "critical",
                    "escalate_privacy_owner",
                    "response_deadline_overdue",
                    f"Due date {due_date.isoformat()} passed {-days_left} days ago.",
                    "Escalate for late-response handling and document extension or remediation rationale.",
                )
            elif days_left <= due_soon_days:
                add_finding(
                    findings,
                    request,
                    "high",
                    "accelerate_fulfillment",
                    "response_deadline_due_soon",
                    f"Due date {due_date.isoformat()} is in {days_left} days.",
                    "Prioritize identity, system owner, and response assembly tasks this week.",
                )
            elif days_left <= due_soon_days + extension_review_days and len(matched_systems) > 3:
                add_finding(
                    findings,
                    request,
                    "medium",
                    "extension_review",
                    "complex_request_extension_review",
                    f"{len(matched_systems)} systems appear in scope and due date is {due_date.isoformat()}.",
                    "Decide whether a documented extension or staged response is needed under local policy.",
                )

        if request.identity_status not in {"verified", "complete", "approved"}:
            add_finding(
                findings,
                request,
                "high",
                "verify_identity",
                "identity_verification_missing",
                f"Identity status is '{request.identity_status or 'blank'}'.",
                "Complete proportionate identity verification before disclosing or deleting personal data.",
            )

        if request.authorized_agent and request.agent_proof not in {"received", "verified", "complete"}:
            add_finding(
                findings,
                request,
                "high",
                "verify_agent_authority",
                "authorized_agent_proof_missing",
                "Request came through an authorized agent but proof is missing or incomplete.",
                "Collect signed authorization or other approved proof before fulfillment.",
            )

        if not request.request_type:
            add_finding(
                findings,
                request,
                "medium",
                "clarify_scope",
                "request_type_missing",
                "No access, deletion, correction, opt-out, or portability type was supplied.",
                "Clarify the right requested and log the confirmed scope.",
            )

        if not matched_systems:
            add_finding(
                findings,
                request,
                "high",
                "map_system_scope",
                "no_matching_system_inventory",
                f"Scope '{request.scope or request.match_keys or 'blank'}' did not match the system inventory.",
                "Map data locations before telling the requester no responsive data exists.",
            )
        else:
            owners = sorted({system.owner or "unassigned" for system in matched_systems})
            if len(owners) > 1:
                add_finding(
                    findings,
                    request,
                    "medium",
                    "route_owner_tasks",
                    "multi_owner_fulfillment_required",
                    f"Matched owners: {', '.join(owners)}.",
                    "Assign each owner an export/deletion task and response due date.",
                )

        if any(term in request.request_type for term in ("access", "portability", "copy")):
            unsupported = [system.system for system in matched_systems if not system.export_supported]
            if unsupported:
                add_finding(
                    findings,
                    request,
                    "high",
                    "manual_export_review",
                    "access_export_not_supported",
                    f"Systems without export support: {', '.join(unsupported)}.",
                    "Create a manual export or documented no-export explanation for each system.",
                )

        if any(term in request.request_type for term in ("delete", "deletion", "erasure")):
            blocked = [
                system.system
                for system in matched_systems
                if system.legal_hold or system.retention_lock or not system.deletion_supported
            ]
            if blocked:
                add_finding(
                    findings,
                    request,
                    "high",
                    "deletion_exception_review",
                    "deletion_blocked_or_exception_needed",
                    f"Deletion is blocked or unsupported in: {', '.join(blocked)}.",
                    "Separate deletable data from retention, legal-hold, security, accounting, or unsupported-system exceptions.",
                )
            if has_term(text_blob, policy.get("deletion_exception_terms")):
                add_finding(
                    findings,
                    request,
                    "medium",
                    "deletion_exception_review",
                    "possible_deletion_exception_context",
                    "Request notes or scope mention a retention/security/legal/accounting context.",
                    "Have privacy/legal owner approve the exception language before sending the response.",
                )

        if has_term(text_blob, policy.get("sensitive_terms")):
            add_finding(
                findings,
                request,
                "high",
                "sensitive_data_review",
                "sensitive_or_minor_data_context",
                "Request scope or notes mention sensitive, child, health, financial, biometric, or location data.",
                "Apply the stricter verification, redaction, and response review path.",
            )

    return findings


def render(requests: list[RequestRow], systems: list[SystemRow], findings: list[Finding]) -> str:
    critical_or_high = [finding for finding in findings if finding.risk in {"critical", "high"}]
    if critical_or_high:
        decision = "Hold fulfillment pending repair"
    elif findings:
        decision = "Review before response"
    else:
        decision = "Ready for controlled fulfillment"

    counts = Counter(finding.flag for finding in findings)
    action_counts = Counter(finding.action for finding in findings)
    owner_map: dict[str, set[str]] = defaultdict(set)
    for request in requests:
        for system in systems:
            if system_matches(request, system):
                owner_map[request.request_id].add(system.owner or "unassigned")

    lines = [
        "## DSAR Request Decision",
        decision,
        "",
        "## Request Summary",
        f"Requests reviewed: {len(requests)}",
        f"Systems in inventory: {len(systems)}",
        f"Findings: {len(findings)}",
        f"Critical/high findings: {len(critical_or_high)}",
        "",
        "## Action Summary",
    ]
    if action_counts:
        for action, count in sorted(action_counts.items()):
            lines.append(f"- {action}: {count}")
    else:
        lines.append("- No blockers found.")

    lines.extend(
        [
            "",
            "## Request Findings",
            "| Risk | Action | Row | Request | Type | Flag | Evidence | Next step |",
            "|---|---|---:|---|---|---|---|---|",
        ]
    )
    for finding in findings:
        request = finding.request
        lines.append(
            "| {risk} | {action} | {row} | {request_id} | {request_type} | {flag} | {evidence} | {next_step} |".format(
                risk=finding.risk,
                action=finding.action,
                row=request.row_number,
                request_id=request.request_id,
                request_type=request.request_type or "unspecified",
                flag=finding.flag,
                evidence=finding.evidence,
                next_step=finding.next_step,
            )
        )

    lines.extend(["", "## Owner Routing"])
    for request_id, owners in sorted(owner_map.items()):
        lines.append(f"- {request_id}: {', '.join(sorted(owners))}")

    lines.extend(["", "## Top Flags"])
    if counts:
        for flag, count in counts.most_common():
            lines.append(f"- {flag}: {count}")
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Guardrails",
            "- This is privacy-operations workflow support, not legal advice.",
            "- Do not disclose or delete data until identity, authority, and exception checks are complete.",
            "- Redact secrets, credentials, full payment data, and unrelated personal data from prompts and fixtures.",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--requests", required=True, type=Path, help="CSV or JSON DSAR request intake export.")
    parser.add_argument("--systems", required=True, type=Path, help="CSV or JSON data-system inventory export.")
    parser.add_argument("--policy", type=Path, help="Optional policy JSON with SLA and exception terms.")
    parser.add_argument("--today", type=parse_date, default=date.today(), help="Review date, YYYY-MM-DD.")
    args = parser.parse_args(argv)

    if args.today is None:
        raise SystemExit("--today must be a valid date.")

    policy = load_policy(args.policy)
    requests = parse_requests(args.requests)
    systems = parse_systems(args.systems)
    findings = analyze(requests, systems, policy, args.today)
    print(render(requests, systems, findings))
    return 2 if any(finding.risk in {"critical", "high"} for finding in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
