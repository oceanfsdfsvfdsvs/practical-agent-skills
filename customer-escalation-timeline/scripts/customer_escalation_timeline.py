#!/usr/bin/env python3
"""Build a customer escalation timeline report from local exports."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path


THIN_NOTE_HINTS = {"investigating", "waiting", "checking", "looking into it", "pending", "follow up"}
FOLLOWUP_TYPES = {"customer_followup", "customer_message", "reply_from_customer"}
HANDOFF_TYPES = {"handoff", "escalation", "reassignment", "transfer"}
WORK_TYPES = {"internal_note", "troubleshooting", "agent_reply", "status_update", "resolution"}
QUEUE_HINTS = {"queue", "unassigned", "triage", "inbox", "backlog"}
LEGAL_CHURN_HINTS = {"legal", "lawsuit", "cancel", "churn", "refund", "1 star", "one star", "angry", "tweet"}


@dataclass(frozen=True)
class Ticket:
    ticket_id: str
    customer_id: str
    account: str
    subject: str
    status: str
    severity: str
    priority: str
    created_at: datetime | None
    first_response_at: datetime | None
    escalated_at: datetime | None
    sla_due_at: datetime | None
    resolved_at: datetime | None
    assigned_team: str
    assignee: str
    product_area: str
    root_cause: str
    sentiment: str
    renewal_date: date | None
    arr: Decimal
    row_number: int


@dataclass(frozen=True)
class Event:
    ticket_id: str
    event_time: datetime | None
    event_type: str
    actor: str
    channel: str
    team: str
    owner: str
    message: str
    next_step: str
    due_at: datetime | None
    linked_item: str
    row_number: int


@dataclass(frozen=True)
class Account:
    customer_id: str
    account: str
    revenue_tier: str
    renewal_date: date | None
    arr: Decimal
    health_score: int | None
    csm: str
    ae: str
    past_escalations_90d: int


@dataclass(frozen=True)
class Finding:
    risk: str
    action: str
    ticket_id: str
    evidence: tuple[str, ...]
    next_step: str


def normalized(value: object) -> str:
    return " ".join(str(value or "").strip().lower().split())


def parse_datetime(value: object) -> datetime | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    raw = raw.replace("Z", "+00:00")
    for fmt in (
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%m/%d/%Y %H:%M",
        "%m/%d/%Y",
    ):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError:
        return None
    return parsed.replace(tzinfo=None)


def parse_date(value: object) -> date | None:
    parsed = parse_datetime(value)
    return parsed.date() if parsed else None


def parse_decimal(value: object) -> Decimal:
    raw = str(value or "").strip().replace(",", "").replace("$", "")
    if not raw:
        return Decimal("0")
    try:
        return Decimal(raw)
    except InvalidOperation:
        return Decimal("0")


def parse_int(value: object) -> int | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    try:
        return int(float(raw))
    except ValueError:
        return None


def load_rows(path: Path, keys: tuple[str, ...]) -> list[dict[str, object]]:
    if not path.exists():
        raise SystemExit(f"Input not found: {path}")
    if path.suffix.lower() == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            for key in keys + ("rows", "items"):
                if isinstance(payload.get(key), list):
                    return list(payload[key])
            raise SystemExit(f"JSON input must contain one of: {', '.join(keys + ('rows', 'items'))}.")
        if isinstance(payload, list):
            return list(payload)
        raise SystemExit("JSON input must be a list or an object containing rows.")
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def clean_row(row: dict[str, object]) -> dict[str, object]:
    return {str(key).strip().lower(): value for key, value in row.items()}


def parse_tickets(path: Path) -> list[Ticket]:
    tickets: list[Ticket] = []
    for offset, raw in enumerate(load_rows(path, ("tickets",)), start=2):
        row = clean_row(dict(raw))
        tickets.append(
            Ticket(
                ticket_id=str(row.get("ticket_id") or row.get("id") or "").strip(),
                customer_id=str(row.get("customer_id") or row.get("customer") or "").strip(),
                account=str(row.get("account") or row.get("account_name") or row.get("company") or "").strip(),
                subject=str(row.get("subject") or row.get("title") or "").strip(),
                status=str(row.get("status") or "").strip(),
                severity=str(row.get("severity") or "").strip(),
                priority=str(row.get("priority") or "").strip(),
                created_at=parse_datetime(row.get("created_at") or row.get("opened_at")),
                first_response_at=parse_datetime(row.get("first_response_at") or row.get("first_reply_at")),
                escalated_at=parse_datetime(row.get("escalated_at") or row.get("escalation_at")),
                sla_due_at=parse_datetime(row.get("sla_due_at") or row.get("response_due_at")),
                resolved_at=parse_datetime(row.get("resolved_at") or row.get("closed_at")),
                assigned_team=str(row.get("assigned_team") or row.get("team") or "").strip(),
                assignee=str(row.get("assignee") or row.get("owner") or "").strip(),
                product_area=str(row.get("product_area") or row.get("category") or "").strip(),
                root_cause=str(row.get("root_cause") or row.get("root_cause_tag") or "").strip(),
                sentiment=str(row.get("sentiment") or "").strip(),
                renewal_date=parse_date(row.get("renewal_date")),
                arr=parse_decimal(row.get("arr") or row.get("annual_value")),
                row_number=offset,
            )
        )
    if not tickets:
        raise SystemExit("No ticket rows found.")
    missing_ids = [str(item.row_number) for item in tickets if not item.ticket_id]
    if missing_ids:
        raise SystemExit(f"Ticket rows missing ticket_id: {', '.join(missing_ids)}")
    return tickets


def parse_events(path: Path) -> list[Event]:
    events: list[Event] = []
    for offset, raw in enumerate(load_rows(path, ("events", "messages", "timeline")), start=2):
        row = clean_row(dict(raw))
        events.append(
            Event(
                ticket_id=str(row.get("ticket_id") or row.get("id") or "").strip(),
                event_time=parse_datetime(row.get("event_time") or row.get("timestamp") or row.get("created_at")),
                event_type=str(row.get("event_type") or row.get("type") or "").strip(),
                actor=str(row.get("actor") or row.get("author") or "").strip(),
                channel=str(row.get("channel") or row.get("source") or "").strip(),
                team=str(row.get("team") or "").strip(),
                owner=str(row.get("owner") or row.get("assignee") or "").strip(),
                message=str(row.get("message") or row.get("summary") or row.get("body") or "").strip(),
                next_step=str(row.get("next_step") or row.get("next_action") or "").strip(),
                due_at=parse_datetime(row.get("due_at") or row.get("next_due_at")),
                linked_item=str(row.get("linked_item") or row.get("linked_issue") or row.get("url") or "").strip(),
                row_number=offset,
            )
        )
    return events


def parse_accounts(path: Path | None) -> dict[str, Account]:
    if path is None:
        return {}
    accounts: dict[str, Account] = {}
    for raw in load_rows(path, ("accounts", "customers")):
        row = clean_row(dict(raw))
        customer_id = str(row.get("customer_id") or row.get("id") or row.get("customer") or "").strip()
        if not customer_id:
            continue
        accounts[customer_id] = Account(
            customer_id=customer_id,
            account=str(row.get("account") or row.get("account_name") or row.get("company") or "").strip(),
            revenue_tier=str(row.get("revenue_tier") or row.get("tier") or row.get("plan") or "").strip(),
            renewal_date=parse_date(row.get("renewal_date")),
            arr=parse_decimal(row.get("arr") or row.get("annual_value")),
            health_score=parse_int(row.get("health_score") or row.get("health")),
            csm=str(row.get("csm") or "").strip(),
            ae=str(row.get("ae") or row.get("account_executive") or "").strip(),
            past_escalations_90d=parse_int(row.get("past_escalations_90d") or row.get("recent_escalations")) or 0,
        )
    return accounts


def fmt_dt(value: datetime | None) -> str:
    return value.strftime("%Y-%m-%d %H:%M") if value else "unknown"


def fmt_date(value: date | None) -> str:
    return value.isoformat() if value else "unknown"


def event_sort_key(event: Event) -> tuple[datetime, int]:
    return (event.event_time or datetime.min, event.row_number)


def last_event(events: list[Event], types: set[str] | None = None) -> Event | None:
    candidates = [item for item in events if types is None or normalized(item.event_type) in types]
    if not candidates:
        return None
    return sorted(candidates, key=event_sort_key)[-1]


def has_queue_owner(ticket: Ticket) -> bool:
    owner_text = normalized(f"{ticket.assignee} {ticket.assigned_team}")
    return not ticket.assignee.strip() or any(hint in owner_text for hint in QUEUE_HINTS)


def account_context(ticket: Ticket, account: Account | None, today: date) -> tuple[list[str], str]:
    evidence: list[str] = []
    tier = normalized(account.revenue_tier if account else "")
    renewal = account.renewal_date if account and account.renewal_date else ticket.renewal_date
    arr = account.arr if account and account.arr else ticket.arr
    health = account.health_score if account else None
    past_escalations = account.past_escalations_90d if account else 0

    if tier in {"enterprise", "vip", "strategic"} or arr >= Decimal("50000"):
        evidence.append("vip_or_high_value_account")
    if renewal and 0 <= (renewal - today).days <= 45:
        evidence.append("renewal_window")
    if health is not None and health <= 60:
        evidence.append("low_health_account")
    if past_escalations >= 2:
        evidence.append("repeat_escalations_90d")
    if any(hint in normalized(f"{ticket.sentiment} {ticket.subject}") for hint in LEGAL_CHURN_HINTS):
        evidence.append("churn_or_reputation_signal")

    detail = []
    if account:
        detail.append(f"tier={account.revenue_tier or 'unknown'}")
        detail.append(f"renewal={fmt_date(renewal)}")
        detail.append(f"ARR={arr:.0f}")
        if health is not None:
            detail.append(f"health={health}")
        if past_escalations:
            detail.append(f"past escalations 90d={past_escalations}")
    return evidence, "; ".join(detail) if detail else "account context unavailable"


def classify_ticket(
    ticket: Ticket,
    events: list[Event],
    account: Account | None,
    now: datetime,
    update_hours: int,
    stale_hours: int,
) -> tuple[list[Finding], dict[str, str]]:
    findings: list[Finding] = []
    sorted_events = sorted(events, key=event_sort_key)
    today = now.date()
    account_evidence, account_detail = account_context(ticket, account, today)
    ticket_text = normalized(" ".join([ticket.subject, ticket.status, ticket.severity, ticket.priority, ticket.sentiment]))
    high_context = bool(account_evidence) or "sev 1" in ticket_text or "sev 2" in ticket_text or "high" in ticket_text

    handoff_events = [item for item in sorted_events if normalized(item.event_type) in HANDOFF_TYPES]
    last_handoff = handoff_events[-1] if handoff_events else None
    current_owner = ticket.assignee or (last_handoff.owner if last_handoff else "") or ticket.assigned_team or "unassigned"

    if ticket.escalated_at or handoff_events:
        handoff_owner = last_handoff.owner if last_handoff else ticket.assignee
        if has_queue_owner(ticket) or not handoff_owner:
            evidence = ["escalated_without_accepted_owner", *account_evidence]
            risk = "critical" if high_context else "high"
            findings.append(
                Finding(
                    risk=risk,
                    action="owner_acceptance_required",
                    ticket_id=ticket.ticket_id,
                    evidence=tuple(evidence),
                    next_step="Assign a named owner and require explicit acceptance before relying on the handoff.",
                )
            )

    last_customer = last_event(sorted_events, FOLLOWUP_TYPES)
    last_work = last_event(sorted_events, WORK_TYPES)
    if ticket.status.lower() not in {"resolved", "closed", "done"}:
        update_due = False
        evidence = []
        if last_customer and (last_work is None or event_sort_key(last_customer) > event_sort_key(last_work)):
            update_due = True
            evidence.append("customer_followup_after_last_agent_update")
        elif last_work and last_work.event_time and now - last_work.event_time > timedelta(hours=update_hours):
            update_due = True
            evidence.append(f"last_agent_update_over_{update_hours}h")
        if last_handoff and not last_handoff.next_step:
            evidence.append("handoff_missing_next_step")
        if update_due:
            risk = "critical" if high_context else "high"
            findings.append(
                Finding(
                    risk=risk,
                    action="customer_update_due",
                    ticket_id=ticket.ticket_id,
                    evidence=tuple([*evidence, *account_evidence]),
                    next_step="Send or schedule a customer-facing update with current owner, next action, and expected timing.",
                )
            )

    stale_sources = [item for item in sorted_events if item.due_at and item.due_at < now and normalized(item.event_type) != "resolution"]
    if stale_sources:
        evidence = [f"next_step_due_passed:{fmt_dt(stale_sources[-1].due_at)}", *account_evidence]
        findings.append(
            Finding(
                risk="high" if high_context else "medium",
                action="sla_or_queue_breach_review",
                ticket_id=ticket.ticket_id,
                evidence=tuple(evidence),
                next_step="Review the stage where the ticket stalled and update owner, due time, and delay reason.",
            )
        )

    if ticket.sla_due_at:
        if ticket.sla_due_at < now and ticket.status.lower() not in {"resolved", "closed", "done"}:
            findings.append(
                Finding(
                    risk="critical" if high_context else "high",
                    action="sla_or_queue_breach_review",
                    ticket_id=ticket.ticket_id,
                    evidence=tuple(["sla_due_time_passed", *account_evidence]),
                    next_step="Record the breached stage and assign owner for recovery communication.",
                )
            )
        elif ticket.sla_due_at <= now + timedelta(hours=1) and ticket.status.lower() not in {"resolved", "closed", "done"}:
            findings.append(
                Finding(
                    risk="critical" if has_queue_owner(ticket) or high_context else "high",
                    action="sla_or_queue_breach_review",
                    ticket_id=ticket.ticket_id,
                    evidence=tuple(["sla_due_within_1h", *account_evidence]),
                    next_step="Confirm owner and customer update before the SLA timer expires.",
                )
            )

    for handoff in handoff_events:
        handoff_text = normalized(f"{handoff.message} {handoff.next_step} {handoff.linked_item}")
        missing_packet = False
        evidence = []
        if len(handoff_text) < 90 or any(hint == handoff_text for hint in THIN_NOTE_HINTS):
            missing_packet = True
            evidence.append("thin_handoff_note")
        if not handoff.next_step:
            missing_packet = True
            evidence.append("missing_next_step")
        if not handoff.linked_item and any(word in ticket_text for word in ("bug", "checkout", "export", "billing", "pricing")):
            missing_packet = True
            evidence.append("missing_linked_issue_or_record")
        if missing_packet:
            findings.append(
                Finding(
                    risk="high" if high_context else "medium",
                    action="handoff_packet_required",
                    ticket_id=ticket.ticket_id,
                    evidence=tuple([*evidence, *account_evidence]),
                    next_step="Create a handoff packet with problem, tried steps, confirmed facts, next owner, due time, and links.",
                )
            )
            break

    teams = {normalized(item.team) for item in sorted_events if item.team}
    channels = {normalized(item.channel) for item in sorted_events if item.channel}
    if len(teams) >= 3 or len(channels) >= 3:
        findings.append(
            Finding(
                risk="medium",
                action="handoff_packet_required",
                ticket_id=ticket.ticket_id,
                evidence=("fragmented_channels_or_teams",),
                next_step="Consolidate the timeline into one handoff packet before the next team takes action.",
            )
        )

    customer_after_resolution = (
        ticket.resolved_at
        and any(item.event_time and item.event_time > ticket.resolved_at for item in sorted_events if normalized(item.event_type) in FOLLOWUP_TYPES)
    )
    if customer_after_resolution or (ticket.status.lower() in {"resolved", "closed", "done"} and not ticket.root_cause):
        evidence = []
        if customer_after_resolution:
            evidence.append("repeat_contact_or_fix_validation")
        if not ticket.root_cause:
            evidence.append("missing_root_cause_tag")
        findings.append(
            Finding(
                risk="high" if customer_after_resolution else "medium",
                action="root_cause_followup",
                ticket_id=ticket.ticket_id,
                evidence=tuple(evidence),
                next_step="Check post-fix repeat contacts, link the problem/root-cause record, and update closure evidence.",
            )
        )

    packet = {
        "owner": current_owner,
        "problem": ticket.subject or "unknown problem",
        "tried": summarize_tried(sorted_events),
        "next": summarize_next(sorted_events),
        "due": summarize_due(sorted_events, ticket),
        "account": account_detail,
    }
    if not findings:
        findings.append(
            Finding(
                risk="low",
                action="ready_for_review",
                ticket_id=ticket.ticket_id,
                evidence=("owner_next_step_and_timeline_present",),
                next_step="Review packet for tone and store evidence in the system of record.",
            )
        )
    return findings, packet


def summarize_tried(events: list[Event]) -> str:
    for event in reversed(events):
        text = normalized(f"{event.event_type} {event.message}")
        if normalized(event.event_type) in {"troubleshooting", "resolution"} or "tried" in text or "tested" in text:
            return event.message[:120] or "not documented"
    return "not documented"


def summarize_next(events: list[Event]) -> str:
    for event in reversed(events):
        if event.next_step:
            return event.next_step[:120]
    return "not documented"


def summarize_due(events: list[Event], ticket: Ticket) -> str:
    due_dates = [event.due_at for event in events if event.due_at]
    if due_dates:
        return fmt_dt(sorted(due_dates)[-1])
    if ticket.sla_due_at:
        return fmt_dt(ticket.sla_due_at)
    return "unknown"


def risk_sort_key(finding: Finding) -> tuple[int, str, str]:
    order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    return (order.get(finding.risk, 9), finding.ticket_id, finding.action)


def render(
    tickets: list[Ticket],
    findings: list[Finding],
    packets: dict[str, dict[str, str]],
    events_by_ticket: dict[str, list[Event]],
    now: datetime,
) -> str:
    critical = sum(1 for item in findings if item.risk == "critical")
    high = sum(1 for item in findings if item.risk == "high")
    medium = sum(1 for item in findings if item.risk == "medium")

    if critical or high:
        decision = f"Hold closure - {critical} critical, {high} high, {medium} medium findings across {len(tickets)} tickets."
    elif medium:
        decision = f"Secondary review required - {medium} medium findings across {len(tickets)} tickets."
    else:
        decision = f"Ready for review - {len(tickets)} tickets have usable owner and timeline evidence."

    lines = [
        "## Escalation Timeline Decision",
        decision,
        "",
        f"Review time: {fmt_dt(now)}",
        "",
        "## Handoff Packet",
        "| Ticket | Customer | Severity | Current owner | Problem | Tried/confirmed | Next step | Due |",
        "|---|---|---|---|---|---|---|---|",
    ]
    ticket_map = {ticket.ticket_id: ticket for ticket in tickets}
    for ticket in tickets:
        packet = packets[ticket.ticket_id]
        customer = ticket.account or ticket.customer_id or "unknown"
        severity = ticket.severity or ticket.priority or "unknown"
        lines.append(
            "| {ticket} | {customer} | {severity} | {owner} | {problem} | {tried} | {next_step} | {due} |".format(
                ticket=ticket.ticket_id,
                customer=escape(customer),
                severity=escape(severity),
                owner=escape(packet["owner"]),
                problem=escape(packet["problem"]),
                tried=escape(packet["tried"]),
                next_step=escape(packet["next"]),
                due=escape(packet["due"]),
            )
        )

    lines.extend(
        [
            "",
            "## Timeline Findings",
            "| Risk | Action | Ticket | Evidence | Reviewer next step |",
            "|---|---|---|---|---|",
        ]
    )
    for finding in sorted(findings, key=risk_sort_key):
        lines.append(
            "| {risk} | {action} | {ticket} | {evidence} | {next_step} |".format(
                risk=finding.risk,
                action=finding.action,
                ticket=finding.ticket_id,
                evidence=escape(", ".join(finding.evidence)),
                next_step=escape(finding.next_step),
            )
        )

    lines.extend(
        [
            "",
            "## Controls Checked",
            "- SLA clock and queue stall state.",
            "- Named owner and owner acceptance.",
            "- Customer update recency and follow-up drift.",
            "- Handoff completeness: problem, tried steps, evidence, next step, due time, linked item.",
            "- Account context: VIP, renewal, ARR, health, and repeat escalations when supplied.",
            "- Root-cause tag, repeat contact, and post-fix validation.",
            "",
            "## Closure Gate",
        ]
    )
    blocking = [item for item in sorted(findings, key=risk_sort_key) if item.risk in {"critical", "high"}]
    if blocking:
        for item in blocking:
            ticket = ticket_map.get(item.ticket_id)
            label = ticket.account if ticket else item.ticket_id
            lines.append(f"- {item.ticket_id} ({label}): resolve `{item.action}` - {item.next_step}")
    else:
        lines.append("- No critical or high closure blockers found in supplied exports.")

    missing_event_tickets = [ticket.ticket_id for ticket in tickets if not events_by_ticket.get(ticket.ticket_id)]
    lines.extend(["", "## Open Questions"])
    if missing_event_tickets:
        lines.append(f"- Event history is missing for: {', '.join(missing_event_tickets)}.")
    if any(item.action == "owner_acceptance_required" for item in findings):
        lines.append("- Who is the named accepting owner for each unaccepted escalation?")
    if any(item.action == "customer_update_due" for item in findings):
        lines.append("- What customer-facing update should be sent, and by when?")
    if any(item.action == "root_cause_followup" for item in findings):
        lines.append("- Which root-cause tag and post-fix repeat-contact check should be recorded?")
    if lines[-1] == "## Open Questions":
        lines.append("- None from the supplied exports.")

    return "\n".join(lines) + "\n"


def escape(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a customer escalation timeline report.")
    parser.add_argument("--tickets", required=True, type=Path, help="CSV or JSON support ticket export.")
    parser.add_argument("--events", required=True, type=Path, help="CSV or JSON event/conversation export.")
    parser.add_argument("--accounts", type=Path, help="Optional CSV or JSON account context export.")
    parser.add_argument("--now", default=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), help="Review timestamp.")
    parser.add_argument("--update-hours", type=int, default=4, help="Customer update staleness threshold.")
    parser.add_argument("--stale-hours", type=int, default=24, help="General stale next-step threshold.")
    parser.add_argument("--output", type=Path, help="Optional Markdown output path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    now = parse_datetime(args.now)
    if now is None:
        raise SystemExit(f"Could not parse --now value: {args.now}")

    tickets = parse_tickets(args.tickets)
    events = parse_events(args.events)
    accounts = parse_accounts(args.accounts)

    events_by_ticket: dict[str, list[Event]] = {ticket.ticket_id: [] for ticket in tickets}
    for event in events:
        if event.ticket_id in events_by_ticket:
            events_by_ticket[event.ticket_id].append(event)

    findings: list[Finding] = []
    packets: dict[str, dict[str, str]] = {}
    for ticket in tickets:
        ticket_findings, packet = classify_ticket(
            ticket,
            events_by_ticket.get(ticket.ticket_id, []),
            accounts.get(ticket.customer_id),
            now,
            args.update_hours,
            args.stale_hours,
        )
        findings.extend(ticket_findings)
        packets[ticket.ticket_id] = packet

    report = render(tickets, findings, packets, events_by_ticket, now)
    if args.output:
        args.output.write_text(report, encoding="utf-8")
    sys.stdout.write(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
