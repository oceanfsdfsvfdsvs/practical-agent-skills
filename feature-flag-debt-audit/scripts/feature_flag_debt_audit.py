#!/usr/bin/env python3
"""Audit feature flag debt from a local flag export and source tree."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable


SCAN_EXTENSIONS = {
    ".c",
    ".cc",
    ".cs",
    ".go",
    ".java",
    ".js",
    ".jsx",
    ".json",
    ".kt",
    ".md",
    ".php",
    ".py",
    ".rb",
    ".rs",
    ".swift",
    ".ts",
    ".tsx",
    ".yaml",
    ".yml",
}

PERMANENT_HINTS = (
    "kill",
    "ops",
    "guard",
    "perm",
    "permanent",
    "entitlement",
    "billing",
    "auth",
    "security",
    "migration",
)


@dataclass(frozen=True)
class Flag:
    key: str
    name: str
    status: str
    kind: str
    owner: str
    created_at: str
    last_seen: str
    expires_at: str
    permanent: bool
    description: str


@dataclass(frozen=True)
class Finding:
    flag: Flag
    action: str
    risk: str
    evidence: list[str]
    references: list[str]
    next_step: str


def parse_date(value: str) -> date | None:
    value = value.strip()
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized).date()
    except ValueError:
        pass
    for fmt in ("%Y/%m/%d",):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def normalize_bool(value: object) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "permanent"}


def read_flags(path: Path) -> list[Flag]:
    if not path.exists():
        raise SystemExit(f"Flag export not found: {path}")
    if path.suffix.lower() == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        rows = payload.get("flags", payload) if isinstance(payload, dict) else payload
        if not isinstance(rows, list):
            raise SystemExit("JSON export must be a list or an object with a 'flags' list.")
    else:
        with path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))

    flags: list[Flag] = []
    for row in rows:
        lowered = {str(k).strip().lower(): v for k, v in dict(row).items()}
        key = str(lowered.get("key") or lowered.get("flag") or lowered.get("name") or "").strip()
        if not key:
            continue
        flags.append(
            Flag(
                key=key,
                name=str(lowered.get("name") or key).strip(),
                status=str(lowered.get("status") or lowered.get("state") or "").strip().lower(),
                kind=str(lowered.get("kind") or lowered.get("type") or "").strip().lower(),
                owner=str(lowered.get("owner") or lowered.get("team") or "").strip(),
                created_at=str(lowered.get("created_at") or lowered.get("created") or "").strip(),
                last_seen=str(lowered.get("last_seen") or lowered.get("last_evaluated") or "").strip(),
                expires_at=str(lowered.get("expires_at") or lowered.get("expiry") or "").strip(),
                permanent=normalize_bool(lowered.get("permanent")),
                description=str(lowered.get("description") or "").strip(),
            )
        )
    if not flags:
        raise SystemExit("No flags with a key/name column were found.")
    return flags


def iter_source_files(root: Path) -> Iterable[Path]:
    if not root.exists():
        raise SystemExit(f"Code directory not found: {root}")
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in SCAN_EXTENSIONS:
            if any(part in {".git", "node_modules", "__pycache__", ".venv"} for part in path.parts):
                continue
            yield path


def scan_references(code_dir: Path, flags: list[Flag]) -> dict[str, list[str]]:
    patterns = {flag.key: re.compile(re.escape(flag.key)) for flag in flags}
    references = {flag.key: [] for flag in flags}
    for path in iter_source_files(code_dir):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        rel = path.relative_to(code_dir)
        for key, pattern in patterns.items():
            count = len(pattern.findall(text))
            if count:
                references[key].append(f"{rel}:{count}")
    return references


def classify(flag: Flag, refs: list[str], today: date, stale_days: int) -> Finding:
    evidence: list[str] = []
    status = flag.status
    kind = flag.kind
    key_text = f"{flag.key} {flag.name} {flag.description} {kind}".lower()
    last_seen = parse_date(flag.last_seen)
    expires_at = parse_date(flag.expires_at)
    stale = False
    expired = False

    if expires_at and expires_at < today:
        expired = True
        evidence.append(f"expired on {expires_at.isoformat()}")
    if last_seen:
        age = (today - last_seen).days
        if age >= stale_days:
            stale = True
            evidence.append(f"last seen {age} days ago")
    else:
        evidence.append("missing last-seen signal")

    if status in {"archived", "deprecated", "inactive", "complete", "completed", "launched"}:
        evidence.append(f"status={status}")
    if refs:
        evidence.append(f"{sum(int(item.rsplit(':', 1)[1]) for item in refs)} code references")
    else:
        evidence.append("no code references found")
    if not flag.owner:
        evidence.append("missing owner")

    permanent_signal = flag.permanent or any(hint in key_text for hint in PERMANENT_HINTS)
    high_path_signal = any(hint in key_text for hint in ("billing", "auth", "security", "migration"))

    if permanent_signal or kind in {"ops", "kill_switch", "entitlement"}:
        return Finding(
            flag=flag,
            action="keep_permanent",
            risk="high",
            evidence=evidence + ["permanent or guardrail signal"],
            references=refs,
            next_step="Keep until owner explicitly approves removal and rollback coverage is documented.",
        )

    if expired and (stale or status in {"archived", "deprecated", "inactive", "complete", "completed", "launched"}):
        if high_path_signal or len(refs) > 3 or not flag.owner:
            return Finding(
                flag=flag,
                action="owner_review",
                risk="medium" if not high_path_signal else "high",
                evidence=evidence,
                references=refs,
                next_step="Assign owner, confirm permanent branch, then split cleanup into a small PR.",
            )
        return Finding(
            flag=flag,
            action="delete_candidate",
            risk="low",
            evidence=evidence,
            references=refs,
            next_step="Create cleanup PR with tests and flag restore plan.",
        )

    if stale and status not in {"active", "enabled"}:
        return Finding(
            flag=flag,
            action="owner_review",
            risk="medium",
            evidence=evidence,
            references=refs,
            next_step="Confirm rollout state and owner before deleting code or remote config.",
        )

    return Finding(
        flag=flag,
        action="instrument_first",
        risk="medium",
        evidence=evidence,
        references=refs,
        next_step="Collect reliable evaluation telemetry before cleanup.",
    )


def render(findings: list[Finding], stale_days: int) -> str:
    delete_count = sum(1 for item in findings if item.action == "delete_candidate")
    review_count = sum(1 for item in findings if item.action == "owner_review")
    permanent_count = sum(1 for item in findings if item.action == "keep_permanent")
    if delete_count:
        decision = f"Delete candidates found: {delete_count}; owner review: {review_count}; permanent guardrails: {permanent_count}."
    elif review_count:
        decision = f"Owner review needed: {review_count}; no low-risk delete candidates today."
    else:
        decision = "No safe delete today; instrument or keep current guardrails."

    lines = [
        "## Flag Debt Decision",
        "",
        decision,
        "",
        f"Stale policy: {stale_days} days since last-seen/evaluation.",
        "",
        "## Cleanup Candidates",
        "",
        "| Flag | Action | Risk | Evidence | Owner | Next step |",
        "|---|---|---|---|---|---|",
    ]
    for item in findings:
        evidence = "; ".join(item.evidence)
        owner = item.flag.owner or "unassigned"
        lines.append(
            f"| `{item.flag.key}` | `{item.action}` | `{item.risk}` | {evidence} | {owner} | {item.next_step} |"
        )

    lines.extend(["", "## Guardrails", ""])
    guarded = [item for item in findings if item.action == "keep_permanent" or item.risk == "high"]
    if guarded:
        for item in guarded:
            lines.append(f"- `{item.flag.key}`: {item.next_step}")
    else:
        lines.append("- No permanent guardrails detected in this sample.")

    lines.extend(["", "## Code References", ""])
    for item in findings:
        if item.references:
            refs = ", ".join(item.references)
        else:
            refs = "none"
        lines.append(f"- `{item.flag.key}`: {refs}")

    lines.extend(["", "## Cleanup Tickets", ""])
    for item in findings:
        if item.action not in {"delete_candidate", "owner_review"}:
            continue
        lines.extend(
            [
                f"### `{item.flag.key}`",
                "",
                f"- Owner: {item.flag.owner or 'assign before delete'}",
                f"- Decision: {item.action}",
                f"- Evidence: {'; '.join(item.evidence)}",
                f"- Verification: run affected tests, confirm production branch behavior, and keep flag restore instructions.",
                f"- Rollback: restore flag config and revert cleanup PR if behavior changes.",
                "",
            ]
        )

    lines.extend(
        [
            "## Verification Plan",
            "",
            "- Run unit and integration tests covering referenced files.",
            "- Confirm the desired permanent branch with the feature owner.",
            "- Check dashboards or flag evaluation telemetry after cleanup.",
            "- Keep each cleanup PR small enough to review independently.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--flags", required=True, type=Path, help="CSV or JSON flag export path.")
    parser.add_argument("--code-dir", required=True, type=Path, help="Source directory to scan.")
    parser.add_argument("--stale-days", type=int, default=90, help="Days without last-seen before stale.")
    parser.add_argument("--today", default=date.today().isoformat(), help="Override today's date as YYYY-MM-DD.")
    parser.add_argument("--output", type=Path, help="Optional Markdown output path.")
    args = parser.parse_args()

    today = parse_date(args.today)
    if today is None:
        raise SystemExit("--today must be a valid date such as 2026-05-12.")
    flags = read_flags(args.flags)
    references = scan_references(args.code_dir, flags)
    findings = [classify(flag, references.get(flag.key, []), today, args.stale_days) for flag in flags]
    report = render(findings, args.stale_days)

    if args.output:
        args.output.write_text(report, encoding="utf-8")
    else:
        sys.stdout.write(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
