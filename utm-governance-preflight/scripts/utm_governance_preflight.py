#!/usr/bin/env python3
"""Audit campaign links for UTM governance issues before launch."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import parse_qsl, urlparse


DEFAULT_REQUIRED = ("utm_source", "utm_medium", "utm_campaign")
COMMON_SOURCES = {"facebook", "linkedin", "google", "newsletter", "instagram", "tiktok", "youtube"}
COMMON_MEDIA = {"cpc", "paid-social", "organic-social", "email", "affiliate", "display", "referral", "event"}
DEFAULT_SENSITIVE = {
    "fired",
    "budget-cut",
    "desperation",
    "competitor-extermination",
    "please-convert",
}


@dataclass(frozen=True)
class LinkRow:
    row_number: int
    link_id: str
    owner: str
    channel: str
    url: str


@dataclass(frozen=True)
class Finding:
    row: LinkRow
    risk: str
    severity: str
    evidence: str
    next_step: str


def normalized_text(value: object) -> str:
    return " ".join(str(value or "").strip().lower().split())


def slug_text(value: object) -> str:
    return normalized_text(value).replace("_", "-")


def load_json(path: Path) -> dict[str, object]:
    if not path.exists():
        raise SystemExit(f"Policy file not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Policy file is not valid JSON: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit("Policy JSON must be an object.")
    return payload


def load_rows(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        raise SystemExit(f"Links file not found: {path}")
    if path.suffix.lower() == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            return [dict(item) for item in payload]
        if isinstance(payload, dict):
            for key in ("rows", "links", "campaigns", "urls"):
                if isinstance(payload.get(key), list):
                    return [dict(item) for item in payload[key]]
        raise SystemExit(f"JSON input must be a list or contain rows/links/campaigns/urls: {path}")
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def clean_row(raw: dict[str, object]) -> dict[str, object]:
    return {normalized_text(key).replace(" ", "_"): value for key, value in raw.items()}


def first(row: dict[str, object], *keys: str) -> str:
    for key in keys:
        if row.get(key) not in (None, ""):
            return str(row.get(key)).strip()
    return ""


def load_links(path: Path) -> list[LinkRow]:
    links: list[LinkRow] = []
    for offset, raw in enumerate(load_rows(path), start=2):
        row = clean_row(raw)
        url = first(row, "url", "link", "campaign_url", "landing_url")
        if not url:
            continue
        links.append(
            LinkRow(
                row_number=offset,
                link_id=first(row, "link_id", "id", "campaign_id", "name") or f"row-{offset}",
                owner=first(row, "owner", "team", "requester"),
                channel=first(row, "channel", "platform", "source_channel"),
                url=url,
            )
        )
    if not links:
        raise SystemExit("No link rows found. Include a url/link/campaign_url field.")
    return links


def as_slug_set(policy: dict[str, object], key: str, defaults: set[str] | tuple[str, ...]) -> set[str]:
    values = policy.get(key, defaults)
    if not isinstance(values, list | tuple | set):
        return set(defaults)
    return {slug_text(value) for value in values if str(value).strip()}


def as_alias_map(policy: dict[str, object], key: str) -> dict[str, str]:
    values = policy.get(key, {})
    if not isinstance(values, dict):
        return {}
    return {slug_text(alias): slug_text(canonical) for alias, canonical in values.items()}


def find_params(url: str) -> dict[str, str]:
    parsed = urlparse(url)
    params: dict[str, str] = {}
    for key, value in parse_qsl(parsed.query, keep_blank_values=True):
        normalized_key = normalized_text(key)
        if normalized_key.startswith("utm_"):
            params[normalized_key] = value.strip()
    return params


def unsafe_value(value: str) -> bool:
    return bool(re.search(r"[\s]", value)) or value != value.strip()


def audit_link(
    row: LinkRow,
    policy: dict[str, object],
    required: tuple[str, ...],
    allowed_sources: set[str],
    source_aliases: dict[str, str],
    allowed_media: set[str],
    medium_aliases: dict[str, str],
    sensitive_terms: set[str],
    campaign_pattern: re.Pattern[str] | None,
) -> list[Finding]:
    findings: list[Finding] = []
    params = find_params(row.url)

    for key in required:
        if not params.get(key):
            findings.append(
                Finding(
                    row=row,
                    risk="missing_required_utm",
                    severity="block",
                    evidence=f"{key} is missing or blank",
                    next_step=f"Add {key} before launch.",
                )
            )

    source_raw = params.get("utm_source", "")
    medium_raw = params.get("utm_medium", "")
    campaign_raw = params.get("utm_campaign", "")
    source_slug = slug_text(source_raw)
    medium_slug = slug_text(medium_raw)
    campaign_slug = slug_text(campaign_raw)

    if source_slug and source_slug in allowed_media and medium_slug in (allowed_sources | set(source_aliases)):
        findings.append(
            Finding(
                row=row,
                risk="source_medium_swapped",
                severity="block",
                evidence=f"utm_source={source_raw} looks like a medium while utm_medium={medium_raw} looks like a source",
                next_step="Swap source and medium, then re-check channel grouping.",
            )
        )

    if source_slug in source_aliases:
        findings.append(
            Finding(
                row=row,
                risk="alias_to_canonical_source",
                severity="review",
                evidence=f"utm_source={source_raw} should be {source_aliases[source_slug]}",
                next_step="Replace source alias with the canonical source value.",
            )
        )
    elif source_slug and source_slug not in allowed_sources:
        findings.append(
            Finding(
                row=row,
                risk="unknown_source",
                severity="review",
                evidence=f"utm_source={source_raw} is outside the approved source list",
                next_step="Map this source to an approved canonical value or update policy intentionally.",
            )
        )

    if medium_slug in medium_aliases:
        findings.append(
            Finding(
                row=row,
                risk="alias_to_canonical_medium",
                severity="review",
                evidence=f"utm_medium={medium_raw} should be {medium_aliases[medium_slug]}",
                next_step="Replace medium alias with the canonical medium value.",
            )
        )
    elif medium_slug and medium_slug not in allowed_media:
        findings.append(
            Finding(
                row=row,
                risk="unknown_medium",
                severity="review",
                evidence=f"utm_medium={medium_raw} is outside the approved medium list",
                next_step="Use a closed-list medium value that matches reporting rules.",
            )
        )

    for key, value in sorted(params.items()):
        if not value:
            continue
        if value != value.lower():
            findings.append(
                Finding(
                    row=row,
                    risk="mixed_case_utm_value",
                    severity="review",
                    evidence=f"{key}={value} contains uppercase characters",
                    next_step="Lowercase UTM values to prevent case-sensitive report fragmentation.",
                )
            )
        if unsafe_value(value):
            findings.append(
                Finding(
                    row=row,
                    risk="unsafe_utm_characters",
                    severity="review",
                    evidence=f"{key}={value} contains spaces or surrounding whitespace",
                    next_step="Use hyphenated slug values with no spaces.",
                )
            )
        value_slug = slug_text(value)
        for term in sensitive_terms:
            if term and term in value_slug:
                findings.append(
                    Finding(
                        row=row,
                        risk="sensitive_internal_term",
                        severity="block",
                        evidence=f"{key} contains internal/sensitive term matching '{term}'",
                        next_step="Rename public UTM values so they do not leak private strategy or pressure.",
                    )
                )

    if campaign_raw and campaign_pattern and not campaign_pattern.match(campaign_slug):
        findings.append(
            Finding(
                row=row,
                risk="campaign_format_violation",
                severity="review",
                evidence=f"utm_campaign={campaign_raw} does not match {policy.get('campaign_pattern')}",
                next_step="Rebuild campaign name from the approved structured slots.",
            )
        )

    return findings


def render_report(links: list[LinkRow], findings: list[Finding]) -> str:
    has_block = any(finding.severity == "block" for finding in findings)
    has_review = any(finding.severity == "review" for finding in findings)
    decision = "Block launch" if has_block else "Fix before launch" if has_review else "Pass"

    lines = [
        "## UTM Governance Decision",
        decision,
        "",
        "## Summary",
        f"- Links reviewed: {len(links)}",
        f"- Block findings: {sum(1 for finding in findings if finding.severity == 'block')}",
        f"- Review findings: {sum(1 for finding in findings if finding.severity == 'review')}",
        "",
        "## Findings",
    ]

    if not findings:
        lines.append("No UTM governance findings.")
    else:
        lines.extend(
            [
                "| Severity | Risk | Row | Link | Owner | Evidence | Next step |",
                "|---|---|---:|---|---|---|---|",
            ]
        )
        for finding in findings:
            lines.append(
                "| {severity} | {risk} | {row} | {link} | {owner} | {evidence} | {next_step} |".format(
                    severity=finding.severity,
                    risk=finding.risk,
                    row=finding.row.row_number,
                    link=finding.row.link_id,
                    owner=finding.row.owner or "unknown",
                    evidence=finding.evidence.replace("|", "\\|"),
                    next_step=finding.next_step.replace("|", "\\|"),
                )
            )

    lines.extend(
        [
            "",
            "## Launch Gate",
            "- Resolve all `block` findings before links go live.",
            "- Review aliases and unknown values with marketing ops before changing reporting policy.",
            "- Keep canonical source and medium lists near the link creation workflow, not only in a wiki.",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--links", required=True, type=Path, help="CSV or JSON campaign link export.")
    parser.add_argument("--policy", type=Path, help="JSON policy with allowed sources, media, and naming rules.")
    args = parser.parse_args(argv)

    policy = load_json(args.policy) if args.policy else {}
    required = tuple(str(value) for value in policy.get("required_parameters", DEFAULT_REQUIRED))
    allowed_sources = as_slug_set(policy, "allowed_sources", COMMON_SOURCES)
    source_aliases = as_alias_map(policy, "source_aliases")
    allowed_media = as_slug_set(policy, "allowed_media", COMMON_MEDIA)
    medium_aliases = as_alias_map(policy, "medium_aliases")
    sensitive_terms = as_slug_set(policy, "sensitive_terms", DEFAULT_SENSITIVE)

    pattern_value = str(policy.get("campaign_pattern", "")).strip()
    try:
        campaign_pattern = re.compile(pattern_value) if pattern_value else None
    except re.error as exc:
        raise SystemExit(f"Invalid campaign_pattern in policy: {exc}") from exc

    links = load_links(args.links)
    findings: list[Finding] = []
    for row in links:
        findings.extend(
            audit_link(
                row,
                policy,
                required,
                allowed_sources,
                source_aliases,
                allowed_media,
                medium_aliases,
                sensitive_terms,
                campaign_pattern,
            )
        )

    print(render_report(links, findings))
    if any(finding.severity == "block" for finding in findings):
        return 2
    if findings:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
