#!/usr/bin/env python3
"""Triage B2B security questionnaires into evidence-backed response work."""

from __future__ import annotations

import argparse
import csv
import io
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable


QUESTION_COLUMNS = ("question", "prompt", "request", "requirement", "description", "control")
ANSWER_COLUMNS = ("current_answer", "answer", "response", "draft_answer", "vendor_answer")
ID_COLUMNS = ("id", "question_id", "qid", "control_id", "row_id")

DOMAIN_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("identity_access", ("mfa", "multi-factor", "2fa", "sso", "single sign-on", "rbac", "iam", "access control", "privileged", "password", "provision", "deprovision", "scim")),
    ("encryption_key_management", ("encrypt", "encryption", "tls", "ssl", "key management", "kms", "key rotation", "cryptographic", "at rest", "in transit")),
    ("logging_monitoring", ("log", "logging", "monitor", "audit trail", "siem", "alert", "detect")),
    ("incident_response", ("incident", "breach", "notification", "root cause", "postmortem", "escalation")),
    ("vulnerability_management", ("vulnerability", "patch", "penetration", "pen test", "pentest", "cve", "scan", "remediation")),
    ("sdlc_change", ("secure development", "sdlc", "code review", "change management", "deployment", "ci/cd", "release", "segregation")),
    ("data_privacy", ("privacy", "gdpr", "ccpa", "personal data", "pii", "data retention", "retention", "data deletion", "dpa", "data processing", "data residency")),
    ("subprocessors_vendor", ("subprocessor", "third party", "third-party", "vendor", "supplier", "outsourc", "processor")),
    ("compliance_audit", ("soc 2", "type ii", "iso 27001", "hipaa", "pci", "certification", "audit report", "compliance")),
    ("business_continuity", ("business continuity", "disaster recovery", "rto", "rpo", "backup", "restore", "availability", "resilience")),
    ("physical_endpoint", ("physical", "device", "laptop", "endpoint", "office", "mdm")),
    ("network_infrastructure", ("network", "firewall", "segmentation", "ip address", "ip addresses", "vpn", "infrastructure", "architecture diagram")),
    ("ai_governance", ("ai", "model", "training data", "train ai", "llm", "genai", "machine learning")),
    ("legal_commercial", ("insurance", "liability", "indemn", "terms", "contract", "sla")),
]

DEFAULT_OWNERS = {
    "identity_access": "Security",
    "encryption_key_management": "Infrastructure",
    "logging_monitoring": "Security operations",
    "incident_response": "Security and legal",
    "vulnerability_management": "Security",
    "sdlc_change": "Engineering",
    "data_privacy": "Privacy and legal",
    "subprocessors_vendor": "GRC or legal",
    "compliance_audit": "GRC",
    "business_continuity": "Infrastructure",
    "physical_endpoint": "IT",
    "network_infrastructure": "Infrastructure",
    "ai_governance": "Product and legal",
    "legal_commercial": "Legal",
    "unknown": "Security owner",
}

SENSITIVE_PATTERNS = (
    "credential",
    "password",
    "secret",
    "token",
    "private key",
    "certificate",
    "production ip",
    "ip address",
    "ip addresses",
    "firewall rules",
    "architecture diagram",
    "network diagram",
    "raw log",
    "logs",
    "customer data sample",
    "employee list",
    "vulnerability details",
    "penetration test report",
    "pentest report",
    "cloud account",
)

LEGAL_PATTERNS = (
    "insurance",
    "liability",
    "indemn",
    "contract",
    "sla",
    "breach notification",
    "gdpr",
    "dpa",
    "data processing agreement",
    "hipaa",
    "pci",
)

OVERCLAIM_RE = re.compile(r"\b(always|never|guarantee(?:d)?|100%|fully compliant|all systems|best[- ]in[- ]class)\b", re.I)
YES_RE = re.compile(r"^(yes|true|y|compliant|implemented|fully compliant)\.?\s*$", re.I)


@dataclass
class Question:
    qid: str
    text: str
    current_answer: str = ""


@dataclass
class Evidence:
    evidence_id: str
    title: str
    domain: str
    owner: str
    last_reviewed: str
    confidentiality: str
    status: str
    location: str


@dataclass
class BankAnswer:
    domain: str
    patterns: list[str]
    answer: str
    evidence_id: str
    owner: str
    last_reviewed: str
    confidence: str


def read_text(path: Path) -> str:
    for encoding in ("utf-8-sig", "utf-8"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="latin-1")


def sniff_delimiter(text: str, path: Path, delimiter: str | None) -> str:
    if delimiter:
        return delimiter
    if path.suffix.lower() == ".tsv":
        return "\t"
    sample = text[:8192]
    try:
        return csv.Sniffer().sniff(sample, delimiters=",\t;|").delimiter
    except csv.Error:
        return "\t" if sample.count("\t") > sample.count(",") else ","


def normalize_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")


def choose_column(fieldnames: Iterable[str], candidates: Iterable[str], explicit: str | None = None) -> str | None:
    normalized = {normalize_key(name): name for name in fieldnames}
    if explicit:
        key = normalize_key(explicit)
        return normalized.get(key)
    for candidate in candidates:
        if candidate in normalized:
            return normalized[candidate]
    return None


def read_table(path: Path, delimiter: str | None) -> list[dict[str, str]]:
    text = read_text(path)
    dialect_delimiter = sniff_delimiter(text, path, delimiter)
    reader = csv.DictReader(io.StringIO(text), delimiter=dialect_delimiter)
    return [{key or "": (value or "").strip() for key, value in row.items()} for row in reader]


def read_questions(path: Path, delimiter: str | None, question_column: str | None, answer_column: str | None) -> list[Question]:
    suffix = path.suffix.lower()
    if suffix in {".csv", ".tsv"}:
        rows = read_table(path, delimiter)
        if not rows:
            return []
        fields = list(rows[0].keys())
        qcol = choose_column(fields, QUESTION_COLUMNS, question_column)
        acol = choose_column(fields, ANSWER_COLUMNS, answer_column)
        idcol = choose_column(fields, ID_COLUMNS)
        if not qcol:
            raise ValueError(f"could not find a question column; tried {', '.join(QUESTION_COLUMNS)}")
        questions: list[Question] = []
        for idx, row in enumerate(rows, start=1):
            text = row.get(qcol, "").strip()
            if text:
                questions.append(Question(row.get(idcol, "").strip() if idcol else f"Q{idx}", text, row.get(acol, "").strip() if acol else ""))
        return questions

    questions = []
    for idx, line in enumerate(read_text(path).splitlines(), start=1):
        cleaned = re.sub(r"^\s*(?:[-*]|\d+[.)])\s*", "", line).strip()
        if cleaned:
            questions.append(Question(f"Q{idx}", cleaned))
    return questions


def parse_date(value: str) -> date | None:
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except ValueError:
            pass
    return None


def is_current(last_reviewed: str, max_age_days: int) -> bool:
    reviewed = parse_date(last_reviewed)
    if reviewed is None:
        return False
    return (date.today() - reviewed).days <= max_age_days


def load_evidence(path: Path | None, delimiter: str | None) -> dict[str, list[Evidence]]:
    if path is None:
        return {}
    by_domain: dict[str, list[Evidence]] = defaultdict(list)
    for row in read_table(path, delimiter):
        evidence = Evidence(
            evidence_id=row.get("evidence_id", "").strip(),
            title=row.get("title", "").strip(),
            domain=row.get("domain", "unknown").strip() or "unknown",
            owner=row.get("owner", "").strip(),
            last_reviewed=row.get("last_reviewed", "").strip(),
            confidentiality=row.get("confidentiality", "").strip(),
            status=row.get("status", "").strip().lower(),
            location=row.get("location", "").strip(),
        )
        if evidence.evidence_id:
            by_domain[evidence.domain].append(evidence)
    return by_domain


def load_answer_bank(path: Path | None, delimiter: str | None) -> list[BankAnswer]:
    if path is None:
        return []
    answers: list[BankAnswer] = []
    for row in read_table(path, delimiter):
        pattern_text = row.get("question_pattern", "").strip()
        answer = row.get("answer", "").strip()
        if not pattern_text or not answer:
            continue
        answers.append(
            BankAnswer(
                domain=row.get("domain", "unknown").strip() or "unknown",
                patterns=[part.strip().lower() for part in pattern_text.split("|") if part.strip()],
                answer=answer,
                evidence_id=row.get("evidence_id", "").strip(),
                owner=row.get("owner", "").strip(),
                last_reviewed=row.get("last_reviewed", "").strip(),
                confidence=row.get("confidence", "").strip(),
            )
        )
    return answers


def classify_domain(text: str) -> str:
    lower = text.lower()
    scores: Counter[str] = Counter()
    for domain, keywords in DOMAIN_RULES:
        for keyword in keywords:
            if keyword in lower:
                scores[domain] += 2 if " " in keyword else 1
    if not scores:
        return "unknown"
    return scores.most_common(1)[0][0]


def find_bank_answer(question: str, domain: str, answers: list[BankAnswer], max_age_days: int) -> BankAnswer | None:
    lower = question.lower()
    domain_matches = [answer for answer in answers if answer.domain == domain]
    fallback = [answer for answer in answers if answer.domain != domain]
    for answer in domain_matches + fallback:
        if any(pattern in lower for pattern in answer.patterns):
            if is_current(answer.last_reviewed, max_age_days):
                return answer
    return None


def approved_current_evidence(evidence: list[Evidence], max_age_days: int) -> list[Evidence]:
    approved_statuses = {"approved", "current", "active"}
    return [
        item
        for item in evidence
        if item.status in approved_statuses and is_current(item.last_reviewed, max_age_days)
    ]


def summarize_evidence(items: list[Evidence], limit: int = 2) -> str:
    if not items:
        return ""
    labels = [item.evidence_id for item in items[:limit]]
    extra = f" +{len(items) - limit}" if len(items) > limit else ""
    return ", ".join(labels) + extra


def has_any(text: str, patterns: Iterable[str]) -> bool:
    lower = text.lower()
    return any(pattern in lower for pattern in patterns)


def assess_question(question: Question, evidence_by_domain: dict[str, list[Evidence]], answer_bank: list[BankAnswer], max_age_days: int) -> dict[str, str]:
    domain = classify_domain(question.text)
    evidence = approved_current_evidence(evidence_by_domain.get(domain, []), max_age_days)
    bank = find_bank_answer(question.text, domain, answer_bank, max_age_days)
    sensitive = has_any(question.text, SENSITIVE_PATTERNS)
    legal = has_any(question.text, LEGAL_PATTERNS) or domain in {"legal_commercial", "data_privacy", "ai_governance", "incident_response"}
    unsupported_yes = bool(question.current_answer and YES_RE.match(question.current_answer) and not evidence)
    overclaim = bool(question.current_answer and OVERCLAIM_RE.search(question.current_answer))

    owner = DEFAULT_OWNERS.get(domain, DEFAULT_OWNERS["unknown"])
    evidence_label = summarize_evidence(evidence)
    draft = ""
    reason_parts: list[str] = []

    if bank:
        owner = bank.owner or owner
        draft = bank.answer
        if not evidence_label and bank.evidence_id:
            evidence_label = bank.evidence_id

    if sensitive:
        status = "do_not_answer_in_sheet"
        reason_parts.append("requested detail belongs in a controlled channel")
    elif legal:
        status = "sme_or_legal_review"
        reason_parts.append("answer may create a legal, privacy, AI, incident, or commercial commitment")
    elif bank and evidence:
        status = "ready_with_cited_answer"
        reason_parts.append("approved answer and current evidence are available")
    elif evidence:
        status = "draft_needs_answer_owner"
        reason_parts.append("current evidence exists but answer wording needs owner approval")
    else:
        status = "needs_evidence"
        reason_parts.append("no current approved evidence was found")

    if unsupported_yes:
        status = "needs_evidence"
        reason_parts.append("current yes-style answer is unsupported")
    if overclaim:
        if status == "ready_with_cited_answer":
            status = "draft_needs_answer_owner"
        reason_parts.append("current answer contains broad or absolute language")

    severity = "high" if status in {"do_not_answer_in_sheet", "sme_or_legal_review"} or unsupported_yes else "medium" if status == "needs_evidence" else "low"
    return {
        "id": question.qid,
        "question": question.text,
        "domain": domain,
        "status": status,
        "severity": severity,
        "owner": owner,
        "evidence": evidence_label or "none",
        "draft": draft,
        "reason": "; ".join(reason_parts),
    }


def escape_cell(value: str, max_len: int = 90) -> str:
    value = re.sub(r"\s+", " ", value.strip())
    if len(value) > max_len:
        value = value[: max_len - 3].rstrip() + "..."
    return value.replace("|", "\\|")


def render_report(source: Path, assessments: list[dict[str, str]]) -> str:
    status_counts = Counter(item["status"] for item in assessments)
    owner_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for item in assessments:
        owner_counts[item["owner"]][item["status"]] += 1

    lines = [
        "# Security Questionnaire Triage",
        "",
        f"Source: `{source}`",
        f"Questions analyzed: {len(assessments)}",
        "",
        "## Response Decision",
    ]

    blocking = status_counts["do_not_answer_in_sheet"] + status_counts["sme_or_legal_review"] + status_counts["needs_evidence"]
    if status_counts["do_not_answer_in_sheet"]:
        decision = "Do not submit in the current worksheet format."
    elif blocking:
        decision = "Submit only after owner review and evidence gaps are closed."
    else:
        decision = "Ready to prepare final submission after normal review."
    lines.append(decision)

    lines.extend(
        [
            "",
            "## Triage Summary",
            "| Status | Count | Action |",
            "|---|---:|---|",
        ]
    )
    action_by_status = {
        "ready_with_cited_answer": "Use approved answer and cite evidence label.",
        "draft_needs_answer_owner": "Have owner approve exact wording.",
        "needs_evidence": "Collect current proof before answering.",
        "sme_or_legal_review": "Route to SME, legal, privacy, or incident owner.",
        "do_not_answer_in_sheet": "Move to approved NDA/channel or refuse detail.",
        "not_applicable_candidate": "Confirm scope before marking N/A.",
    }
    for status, count in sorted(status_counts.items()):
        lines.append(f"| `{status}` | {count} | {action_by_status.get(status, 'Review manually.')} |")

    lines.extend(
        [
            "",
            "## Reviewer Queue",
            "| Owner | Questions | Main statuses |",
            "|---|---:|---|",
        ]
    )
    for owner, counts in sorted(owner_counts.items()):
        top = ", ".join(f"{status}: {count}" for status, count in counts.most_common())
        lines.append(f"| {escape_cell(owner)} | {sum(counts.values())} | {escape_cell(top)} |")

    high_risk = [item for item in assessments if item["severity"] == "high"]
    if high_risk:
        lines.extend(
            [
                "",
                "## High-Risk Rows",
                "| ID | Domain | Status | Safe next step |",
                "|---|---|---|---|",
            ]
        )
        for item in high_risk:
            lines.append(
                f"| {escape_cell(item['id'])} | {item['domain']} | `{item['status']}` | {escape_cell(item['reason'])} |"
            )

    lines.extend(
        [
            "",
            "## Question Triage",
            "| ID | Domain | Status | Owner | Evidence | Reason |",
            "|---|---|---|---|---|---|",
        ]
    )
    for item in assessments:
        lines.append(
            f"| {escape_cell(item['id'])} | {item['domain']} | `{item['status']}` | {escape_cell(item['owner'])} | {escape_cell(item['evidence'])} | {escape_cell(item['reason'])} |"
        )

    draftable = [item for item in assessments if item["draft"] and item["status"] in {"ready_with_cited_answer", "sme_or_legal_review"}]
    if draftable:
        lines.extend(
            [
                "",
                "## Draftable Answers",
                "| ID | Draft | Evidence | Reviewer |",
                "|---|---|---|---|",
            ]
        )
        for item in draftable:
            lines.append(
                f"| {escape_cell(item['id'])} | {escape_cell(item['draft'], 140)} | {escape_cell(item['evidence'])} | {escape_cell(item['owner'])} |"
            )

    lines.extend(
        [
            "",
            "## Redaction And Sharing Notes",
            "- Do not paste secrets, raw logs, customer data, vulnerability details, production network details, or private audit artifacts into the questionnaire.",
            "- Use evidence labels, trust-center links, or approved NDA channels for confidential materials.",
            "- Treat unsupported previous answers as evidence requests, not as facts.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Triage a security questionnaire into response statuses.")
    parser.add_argument("questionnaire", type=Path, help="CSV, TSV, TXT, or Markdown file containing questions.")
    parser.add_argument("--evidence-register", type=Path, help="Optional CSV evidence register.")
    parser.add_argument("--answer-bank", type=Path, help="Optional CSV approved answer bank.")
    parser.add_argument("--delimiter", help="Optional delimiter for CSV-like inputs.")
    parser.add_argument("--question-column", help="Question column name if auto-detection fails.")
    parser.add_argument("--answer-column", help="Current answer column name if auto-detection fails.")
    parser.add_argument("--max-evidence-age-days", type=int, default=365, help="Maximum age for evidence and answer-bank entries.")
    args = parser.parse_args(argv)

    try:
        questions = read_questions(args.questionnaire, args.delimiter, args.question_column, args.answer_column)
        evidence = load_evidence(args.evidence_register, args.delimiter)
        answer_bank = load_answer_bank(args.answer_bank, args.delimiter)
        assessments = [
            assess_question(question, evidence, answer_bank, args.max_evidence_age_days)
            for question in questions
        ]
    except (OSError, ValueError, csv.Error) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if not assessments:
        print("error: no questions found", file=sys.stderr)
        return 1

    print(render_report(args.questionnaire, assessments))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
