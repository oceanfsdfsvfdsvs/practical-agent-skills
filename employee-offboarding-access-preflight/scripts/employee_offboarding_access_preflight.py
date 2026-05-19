#!/usr/bin/env python3
"""Find lingering access before offboarding or role-change closure."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path


DEPARTED_STATUS = {"terminated", "departed", "left", "former", "inactive", "offboarded"}
PENDING_STATUS = {"notice", "leaving", "resigned", "pending termination", "pending_termination"}
TRANSFER_TYPES = {"role_change", "transfer", "internal_transfer", "department_change"}
ACTIVE_ACCOUNT = {"active", "enabled", "assigned", "paid", "provisioned", "invited"}
INACTIVE_ACCOUNT = {"disabled", "suspended", "inactive", "deleted", "deprovisioned", "revoked"}
TRUTHY = {"true", "yes", "y", "1", "admin", "privileged", "sensitive"}
FALSY = {"false", "no", "n", "0", "none", "not_applicable", "n/a"}
DIRECT_LOGIN_HINTS = {"direct", "direct-login", "local", "password", "native", "non-sso", "non_sso"}
PRIVILEGED_WORDS = {"admin", "owner", "root", "super admin", "billing", "prod", "production", "poweruser", "security"}
SECRET_ACTIVE = {"active", "enabled", "valid", "unrotated", "live"}
ASSET_ASSIGNED = {"assigned", "issued", "not_returned", "missing", "active"}


@dataclass(frozen=True)
class Departure:
    email: str
    name: str
    status: str
    termination_date: date | None
    last_working_day: date | None
    separation_type: str
    role: str
    department: str
    manager: str
    risk_level: str
    row_number: int


@dataclass(frozen=True)
class Finding:
    risk: str
    action: str
    source: str
    person: str
    system: str
    evidence: tuple[str, ...]
    next_step: str


def normalized_text(value: object) -> str:
    return " ".join(str(value or "").strip().lower().split())


def display_text(value: object) -> str:
    return str(value or "").strip()


def parse_boolish(value: object) -> bool | None:
    text = normalized_text(value).replace(" ", "_")
    if text in TRUTHY:
        return True
    if text in FALSY:
        return False
    if not text or text == "unknown":
        return None
    return None


def parse_date(value: object) -> date | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    if "T" in raw:
        raw = raw.split("T", 1)[0]
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    return None


def load_rows(path: Path | None, keys: tuple[str, ...]) -> list[dict[str, object]]:
    if path is None:
        return []
    if not path.exists():
        raise SystemExit(f"Input file not found: {path}")
    if path.suffix.lower() == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            return [dict(item) for item in payload]
        if isinstance(payload, dict):
            for key in (*keys, "rows", "items"):
                if isinstance(payload.get(key), list):
                    return [dict(item) for item in payload[key]]
        raise SystemExit(f"JSON input must be a list or contain a row list: {path}")
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def clean_row(raw: dict[str, object]) -> dict[str, object]:
    return {normalized_text(key).replace(" ", "_"): value for key, value in raw.items()}


def first(row: dict[str, object], *keys: str) -> object:
    for key in keys:
        if row.get(key) not in (None, ""):
            return row.get(key)
    return ""


def normalize_email(value: object) -> str:
    return normalized_text(value)


def load_departures(path: Path) -> dict[str, Departure]:
    departures: dict[str, Departure] = {}
    for offset, raw in enumerate(load_rows(path, ("departures", "employees")), start=2):
        row = clean_row(raw)
        email = normalize_email(first(row, "email", "work_email", "user_email", "account_email"))
        if not email:
            continue
        status = normalized_text(first(row, "employment_status", "status", "employee_status"))
        termination_date = parse_date(first(row, "termination_date", "departed_date", "offboarded_at"))
        last_working_day = parse_date(first(row, "last_working_day", "last_day", "ldw")) or termination_date
        departures[email] = Departure(
            email=email,
            name=display_text(first(row, "name", "full_name", "display_name")) or email,
            status=status,
            termination_date=termination_date,
            last_working_day=last_working_day,
            separation_type=normalized_text(first(row, "separation_type", "departure_type", "event_type")),
            role=display_text(first(row, "role", "title", "job_title")),
            department=display_text(first(row, "department", "team", "org")),
            manager=display_text(first(row, "manager", "owner")),
            risk_level=normalized_text(first(row, "risk_level", "risk", "sensitivity")),
            row_number=offset,
        )
    if not departures:
        raise SystemExit("No departure rows found. Required field: email.")
    return departures


def is_active_status(status: str) -> bool:
    if not status:
        return True
    if status in INACTIVE_ACCOUNT:
        return False
    if status in ACTIVE_ACCOUNT:
        return True
    return status not in INACTIVE_ACCOUNT


def person_state(dep: Departure, today: date) -> str:
    event_date = dep.last_working_day or dep.termination_date
    if dep.status in DEPARTED_STATUS:
        return "departed"
    if dep.separation_type in TRANSFER_TYPES:
        return "transfer"
    if event_date and event_date <= today:
        return "departed"
    if dep.status in PENDING_STATUS or event_date:
        return "pending"
    return "unknown"


def is_privileged(row: dict[str, object]) -> bool:
    explicit = parse_boolish(first(row, "privileged", "is_privileged", "admin"))
    if explicit is not None:
        return explicit
    role = normalized_text(first(row, "role", "permission", "access_level", "group"))
    return any(word in role for word in PRIVILEGED_WORDS)


def is_direct_login(row: dict[str, object]) -> bool:
    access_type = normalized_text(first(row, "access_type", "login_type", "auth_type")).replace(" ", "-")
    sso_managed = parse_boolish(first(row, "sso_managed", "sso", "saml", "idp_managed"))
    if access_type in DIRECT_LOGIN_HINTS:
        return True
    if sso_managed is False:
        return True
    return False


def person_label(dep: Departure) -> str:
    return f"{dep.name} <{dep.email}>"


def risk_rank(risk: str) -> int:
    return {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(risk, 4)


def finding_for_account(row: dict[str, object], row_number: int, dep: Departure, state: str) -> list[Finding]:
    app = display_text(first(row, "app", "application", "system", "tool", "vendor")) or "account"
    status = normalized_text(first(row, "account_status", "status", "license_status", "state"))
    active = is_active_status(status)
    privileged = is_privileged(row)
    direct_login = is_direct_login(row)
    session_revoked = parse_boolish(first(row, "session_revoked", "sessions_revoked", "force_logout"))
    mfa_revoked = parse_boolish(first(row, "mfa_revoked", "recovery_revoked", "authenticators_revoked"))
    findings: list[Finding] = []

    if state == "departed" and active:
        evidence = ["active_account_after_departure"]
        if privileged:
            evidence.append("privileged_access_after_departure")
        if direct_login:
            evidence.append("shadow_saas_or_direct_login")
        if session_revoked is False:
            evidence.append("session_not_revoked")
        if mfa_revoked is False:
            evidence.append("mfa_or_recovery_not_revoked")
        risk = "critical" if privileged or direct_login or session_revoked is False or mfa_revoked is False else "high"
        findings.append(
            Finding(
                risk=risk,
                action="revoke_now",
                source=f"accounts row {row_number}",
                person=person_label(dep),
                system=app,
                evidence=tuple(evidence),
                next_step="Disable or remove access, revoke sessions/MFA, and archive reviewer evidence.",
            )
        )
    elif state == "transfer" and active and privileged:
        findings.append(
            Finding(
                risk="high",
                action="secondary_verification",
                source=f"accounts row {row_number}",
                person=person_label(dep),
                system=app,
                evidence=("old_role_privileged_access_on_transfer",),
                next_step="Confirm the new role still requires this access or remove old-role entitlement.",
            )
        )
    elif state == "pending" and active and (privileged or direct_login):
        evidence = ["pending_departure_sensitive_access"]
        if direct_login:
            evidence.append("shadow_saas_or_direct_login")
        findings.append(
            Finding(
                risk="medium",
                action="secondary_verification",
                source=f"accounts row {row_number}",
                person=person_label(dep),
                system=app,
                evidence=tuple(evidence),
                next_step="Schedule exact revocation time and owner before the last working moment.",
            )
        )
    elif state == "departed" and not active and (session_revoked is False or mfa_revoked is False):
        findings.append(
            Finding(
                risk="medium",
                action="secondary_verification",
                source=f"accounts row {row_number}",
                person=person_label(dep),
                system=app,
                evidence=("account_inactive_but_session_or_mfa_gap",),
                next_step="Confirm sessions, device tokens, MFA, and recovery methods were revoked.",
            )
        )
    return findings


def finding_for_group(row: dict[str, object], row_number: int, dep: Departure, state: str) -> list[Finding]:
    system = display_text(first(row, "system", "app", "application")) or "group"
    group = display_text(first(row, "group", "group_name", "role")) or "membership"
    privileged = is_privileged(row)
    sensitive = parse_boolish(first(row, "contains_sensitive_data", "sensitive", "confidential")) is True
    if state not in {"departed", "transfer"}:
        return []
    if not privileged and not sensitive:
        return []
    evidence = ["sensitive_group_membership_after_departure" if state == "departed" else "old_role_group_membership_on_transfer"]
    if privileged:
        evidence.append("privileged_group_membership")
    if sensitive:
        evidence.append("sensitive_data_group")
    return [
        Finding(
            risk="critical" if state == "departed" and privileged else "high",
            action="revoke_now",
            source=f"groups row {row_number}",
            person=person_label(dep),
            system=f"{system}:{group}",
            evidence=tuple(evidence),
            next_step="Remove group membership or record an approved exception with owner and expiry.",
        )
    ]


def finding_for_asset(row: dict[str, object], row_number: int, dep: Departure, state: str) -> list[Finding]:
    if state not in {"departed", "pending"}:
        return []
    status = normalized_text(first(row, "status", "asset_status", "state"))
    wipe_status = normalized_text(first(row, "wipe_status", "mdm_status", "lock_status"))
    returned_at = parse_date(first(row, "returned_at", "return_date", "recovered_at"))
    sensitive = parse_boolish(first(row, "contains_sensitive_data", "sensitive")) is True
    assigned = status in ASSET_ASSIGNED or (not returned_at and status not in {"returned", "recovered", "retired"})
    wipe_gap = wipe_status in {"not_wiped", "wipe_failed", "unknown", ""}
    if state == "departed" and (assigned or (sensitive and wipe_gap)):
        asset = display_text(first(row, "asset_id", "serial", "device_id")) or "asset"
        evidence = []
        if assigned:
            evidence.append("device_not_returned")
        if sensitive and wipe_gap:
            evidence.append("wipe_not_confirmed")
        return [
            Finding(
                risk="high",
                action="recover_or_wipe_device",
                source=f"assets row {row_number}",
                person=person_label(dep),
                system=asset,
                evidence=tuple(evidence),
                next_step="Recover, lock, or wipe the device and preserve MDM or asset-ticket evidence.",
            )
        ]
    if state == "pending" and sensitive and assigned:
        return [
            Finding(
                risk="medium",
                action="secondary_verification",
                source=f"assets row {row_number}",
                person=person_label(dep),
                system=display_text(first(row, "asset_id", "serial", "device_id")) or "asset",
                evidence=("pending_departure_asset_return_needed",),
                next_step="Schedule asset return, lock, or wipe action before last working day.",
            )
        ]
    return []


def finding_for_secret(row: dict[str, object], row_number: int, dep: Departure, state: str) -> list[Finding]:
    if state not in {"departed", "transfer", "pending"}:
        return []
    status = normalized_text(first(row, "status", "secret_status", "state"))
    rotated_at = parse_date(first(row, "rotated_at", "rotation_date", "last_rotated_at"))
    active = status in SECRET_ACTIVE or (not rotated_at and status not in {"revoked", "disabled", "rotated", "deleted"})
    privileged = is_privileged(row)
    shared = parse_boolish(first(row, "shared", "shared_credential")) is True
    if not active:
        return []
    system = display_text(first(row, "system", "app", "application")) or "secret"
    secret_type = display_text(first(row, "secret_type", "type", "credential_type")) or "credential"
    evidence = ["active_secret_owned_by_departing_person" if state == "departed" else "secret_owner_transfer_needed"]
    if privileged:
        evidence.append("privileged_secret")
    if shared:
        evidence.append("shared_credential")
    return [
        Finding(
            risk="critical" if state == "departed" and (privileged or shared) else "high",
            action="rotate_or_reassign_secret",
            source=f"secrets row {row_number}",
            person=person_label(dep),
            system=f"{system}:{secret_type}",
            evidence=tuple(evidence),
            next_step="Rotate or reassign the credential, update dependent systems, and record the new owner.",
        )
    ]


def collect_findings(args: argparse.Namespace) -> list[Finding]:
    today = args.today
    departures = load_departures(args.departures)
    findings: list[Finding] = []

    for dep in departures.values():
        state = person_state(dep, today)
        if state == "unknown":
            findings.append(
                Finding(
                    risk="high",
                    action="secondary_verification",
                    source=f"departures row {dep.row_number}",
                    person=person_label(dep),
                    system="HR roster",
                    evidence=("missing_or_ambiguous_departure_status",),
                    next_step="Confirm employment status, last working day, and revocation deadline.",
                )
            )
        elif state == "departed" and not (dep.termination_date or dep.last_working_day):
            findings.append(
                Finding(
                    risk="high",
                    action="secondary_verification",
                    source=f"departures row {dep.row_number}",
                    person=person_label(dep),
                    system="HR roster",
                    evidence=("missing_termination_date",),
                    next_step="Record termination date before closing the access review.",
                )
            )

    for offset, raw in enumerate(load_rows(args.accounts, ("accounts", "users")), start=2):
        row = clean_row(raw)
        email = normalize_email(first(row, "email", "user_email", "account_email", "login"))
        dep = departures.get(email)
        if dep:
            findings.extend(finding_for_account(row, offset, dep, person_state(dep, today)))

    for offset, raw in enumerate(load_rows(args.groups, ("groups", "memberships")), start=2):
        row = clean_row(raw)
        email = normalize_email(first(row, "email", "user_email", "account_email", "member_email"))
        dep = departures.get(email)
        if dep:
            findings.extend(finding_for_group(row, offset, dep, person_state(dep, today)))

    for offset, raw in enumerate(load_rows(args.assets, ("assets", "devices")), start=2):
        row = clean_row(raw)
        email = normalize_email(first(row, "email", "user_email", "owner_email", "assignee_email"))
        dep = departures.get(email)
        if dep:
            findings.extend(finding_for_asset(row, offset, dep, person_state(dep, today)))

    for offset, raw in enumerate(load_rows(args.secrets, ("secrets", "credentials")), start=2):
        row = clean_row(raw)
        email = normalize_email(first(row, "owner_email", "email", "user_email", "account_email"))
        dep = departures.get(email)
        if dep:
            findings.extend(finding_for_secret(row, offset, dep, person_state(dep, today)))

    return sorted(findings, key=lambda item: (risk_rank(item.risk), item.person, item.system, item.source))


def render_report(findings: list[Finding]) -> str:
    critical_high = [item for item in findings if item.risk in {"critical", "high"}]
    if critical_high:
        decision = (
            f"Hold closure - {len(critical_high)} critical/high findings require revocation, "
            "rotation, recovery, or evidence before the offboarding review can close."
        )
    elif findings:
        decision = "Secondary verification required - no critical/high findings, but evidence gaps remain."
    else:
        decision = "Evidence complete - no material offboarding access gaps found in supplied exports."

    lines = [
        "## Offboarding Access Decision",
        decision,
        "",
        "## Departure Findings",
        "| Risk | Action | Source | Person | System | Evidence | Reviewer next step |",
        "|---|---|---|---|---|---|---|",
    ]
    if findings:
        for item in findings:
            lines.append(
                "| {risk} | {action} | {source} | {person} | {system} | {evidence} | {next_step} |".format(
                    risk=item.risk,
                    action=item.action,
                    source=item.source,
                    person=item.person,
                    system=item.system,
                    evidence=", ".join(item.evidence),
                    next_step=item.next_step,
                )
            )
    else:
        lines.append("| low | document_complete | supplied exports | all scoped people | all scoped systems | no_findings | Archive evidence and perform scheduled post-departure scan. |")

    controls = (
        "HR trigger, IdP/account disablement, session/MFA revocation, SSO/direct-login coverage, "
        "groups, secrets, devices, ownership transfer."
    )
    lines.extend(
        [
            "",
            "## Controls Checked",
            controls,
            "",
            "## Closure Gate",
        ]
    )
    if critical_high:
        lines.append("- Resolve all `critical` and `high` rows before marking the ticket complete.")
    if any(item.action == "rotate_or_reassign_secret" for item in findings):
        lines.append("- Rotate or reassign every active secret, API key, token, or shared credential owned by a departing person.")
    if any(item.action == "recover_or_wipe_device" for item in findings):
        lines.append("- Recover, lock, or wipe outstanding devices and archive MDM or asset-ticket evidence.")
    if any("shadow_saas_or_direct_login" in item.evidence for item in findings):
        lines.append("- Disable direct-login SaaS accounts separately from IdP-controlled accounts.")
    if not critical_high:
        lines.append("- Archive reviewer evidence in the HR/ITSM/GRC system outside the prompt transcript.")
    lines.extend(
        [
            "",
            "## Open Questions",
            "- Are any findings approved exceptions with owner, expiry, and compensating control evidence?",
            "- Was a post-departure scan scheduled for direct-login SaaS, secrets, and devices?",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--departures", required=True, type=Path, help="HR departure roster CSV or JSON.")
    parser.add_argument("--accounts", type=Path, help="Account/SaaS/IdP export CSV or JSON.")
    parser.add_argument("--groups", type=Path, help="Group membership export CSV or JSON.")
    parser.add_argument("--assets", type=Path, help="Device/badge/asset export CSV or JSON.")
    parser.add_argument("--secrets", type=Path, help="Secret-owner or credential inventory CSV or JSON.")
    parser.add_argument("--today", type=lambda value: datetime.strptime(value, "%Y-%m-%d").date(), default=date.today())
    parser.add_argument("--output", type=Path, help="Optional Markdown output path.")
    args = parser.parse_args()

    report = render_report(collect_findings(args))
    if args.output:
        args.output.write_text(report, encoding="utf-8")
    else:
        sys.stdout.write(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
