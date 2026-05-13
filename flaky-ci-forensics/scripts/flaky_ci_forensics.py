#!/usr/bin/env python3
"""Analyze flaky CI failures from local JUnit XML, CI logs, and history CSV."""

from __future__ import annotations

import argparse
import csv
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path


BUCKET_PATTERNS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("timeout_or_wait", ("timeout", "timed out", "waiting for", "event loop", "sleep", "poll")),
    ("network_or_external_service", ("econnreset", "dns", "http 500", "http 502", "http 503", "429", "rate limit", "sandbox", "webhook")),
    ("order_or_state_leak", ("dirty", "state leak", "global mock", "fails in suite", "passes alone", "order dependent")),
    ("parallelism_or_race", ("race", "worker", "parallel", "port already", "duplicate key", "lock", "shared temp")),
    ("clock_locale_or_randomness", ("timezone", "dst", "locale", "random", "seed", "date boundary")),
    ("resource_or_runner", ("oom", "out of memory", "disk full", "browser crash", "runner", "image", "cpu")),
    ("selector_or_ui_sync", ("selector", "detached", "stale element", "hydration", "click intercepted", "testid", "aria")),
    ("assertion_or_product_regression", ("assertionerror", "expected", "actual", "snapshot", "compile", "typeerror")),
)

RISKY_COVERAGE = ("auth", "billing", "payment", "permission", "migration", "security", "delete", "compliance")


@dataclass
class History:
    runs: int = 0
    failures: int = 0
    rerun_passes: int = 0
    first_seen: str = ""
    last_seen: str = ""
    owner: str = ""

    @property
    def failure_rate(self) -> float:
        return self.failures / self.runs if self.runs else 0.0


@dataclass
class Failure:
    test: str
    classname: str
    kind: str
    message: str
    details: str
    bucket: str = "unknown_needs_instrumentation"
    confidence: str = "low"
    evidence: list[str] = field(default_factory=list)
    action: str = "Instrument then rerun"
    owner: str = ""


def read_text(path: Path | None) -> str:
    if not path:
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def parse_junit(path: Path | None) -> list[Failure]:
    if not path:
        return []
    tree = ET.parse(path)
    root = tree.getroot()
    failures: list[Failure] = []
    for testcase in root.iter("testcase"):
        classname = testcase.attrib.get("classname", "")
        name = testcase.attrib.get("name", "unknown_test")
        test_id = f"{classname}::{name}" if classname else name
        for tag in ("failure", "error"):
            node = testcase.find(tag)
            if node is None:
                continue
            message = node.attrib.get("message", "").strip()
            details = (node.text or "").strip()
            failures.append(Failure(test=test_id, classname=classname, kind=tag, message=message, details=details))
    return failures


def parse_history(path: Path | None) -> dict[str, History]:
    if not path:
        return {}
    rows: dict[str, History] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            test = (row.get("test") or "").strip()
            if not test:
                continue
            rows[test] = History(
                runs=parse_int(row.get("runs")),
                failures=parse_int(row.get("failures")),
                rerun_passes=parse_int(row.get("rerun_passes")),
                first_seen=(row.get("first_seen") or "").strip(),
                last_seen=(row.get("last_seen") or "").strip(),
                owner=(row.get("owner") or "").strip(),
            )
    return rows


def parse_int(value: str | None) -> int:
    try:
        return int((value or "0").strip())
    except ValueError:
        return 0


def classify(text: str) -> tuple[str, list[str]]:
    normalized = text.lower()
    hits: list[tuple[str, str]] = []
    for bucket, patterns in BUCKET_PATTERNS:
        for pattern in patterns:
            if pattern in normalized:
                hits.append((bucket, pattern))
                break
    if not hits:
        return "unknown_needs_instrumentation", []
    priority = {bucket: index for index, (bucket, _) in enumerate(BUCKET_PATTERNS)}
    hits.sort(key=lambda item: priority[item[0]])
    return hits[0][0], [f"{bucket}:{pattern}" for bucket, pattern in hits[:4]]


def log_context(log_text: str, test: str) -> str:
    if not log_text:
        return ""
    terms = {test, test.split("::")[-1]}
    lines = log_text.splitlines()
    matches: list[str] = []
    for index, line in enumerate(lines):
        if any(term and term in line for term in terms):
            start = max(0, index - 2)
            end = min(len(lines), index + 3)
            matches.extend(lines[start:end])
    if not matches:
        return ""
    return "\n".join(dict.fromkeys(matches))[:2000]


def enrich(failure: Failure, history: History | None, log_text: str) -> None:
    combined = "\n".join([failure.test, failure.message, failure.details, log_context(log_text, failure.test)])
    bucket, pattern_hits = classify(combined)
    structured_failure = "\n".join([failure.message, failure.details]).lower()
    if (
        any(term in structured_failure for term in ("assertionerror", "expected", "actual", "snapshot"))
        and not (history and history.rerun_passes)
    ):
        bucket = "assertion_or_product_regression"
        pattern_hits = ["assertion_or_product_regression:structured_junit_failure"]
    failure.bucket = bucket
    failure.evidence.extend(pattern_hits)
    if history:
        failure.owner = history.owner
        if history.failures:
            failure.evidence.append(f"{history.failures}/{history.runs} historical failures")
        if history.rerun_passes:
            failure.evidence.append(f"{history.rerun_passes} rerun passes")
    retry_pass = bool(re.search(r"retry.*passed|passed.*retry|without code changes", combined, flags=re.IGNORECASE))
    if retry_pass:
        failure.evidence.append("retry passed without code changes")
    if bucket == "assertion_or_product_regression" and not (history and history.rerun_passes):
        failure.confidence = "regression_likely"
        failure.action = "Fix now"
    elif history and history.rerun_passes >= max(2, history.failures // 2):
        failure.confidence = "high"
        failure.action = action_for_flake(failure)
    elif retry_pass or bucket in {"timeout_or_wait", "network_or_external_service", "selector_or_ui_sync", "parallelism_or_race"}:
        failure.confidence = "medium"
        failure.action = action_for_flake(failure)
    else:
        failure.confidence = "low"
        failure.action = "Instrument then rerun"


def action_for_flake(failure: Failure) -> str:
    lower_name = failure.test.lower()
    if any(term in lower_name for term in RISKY_COVERAGE):
        return "Do not quarantine; fix or instrument with owner"
    if failure.bucket in {"network_or_external_service", "resource_or_runner"} and failure.confidence != "high":
        return "Rerun once only"
    if failure.confidence == "high":
        return "Quarantine with owner and expiry, then fix"
    return "Instrument then rerun"


def overall_decision(failures: list[Failure]) -> str:
    if not failures:
        return "Instrument then rerun"
    if any(f.action == "Fix now" for f in failures):
        return "Fix now"
    if any(f.action.startswith("Do not quarantine") for f in failures):
        return "Do not quarantine"
    if any(f.action.startswith("Quarantine") for f in failures):
        return "Quarantine with owner and expiry"
    if all(f.action == "Rerun once only" for f in failures):
        return "Rerun once only"
    return "Instrument then rerun"


def estimate_cost(histories: dict[str, History], avg_job_minutes: float, runs_per_day: float) -> tuple[float, float]:
    if not histories or avg_job_minutes <= 0 or runs_per_day <= 0:
        return 0.0, 0.0
    failure_rates = [history.failure_rate for history in histories.values() if history.runs]
    if not failure_rates:
        return 0.0, 0.0
    average_failure_rate = sum(failure_rates) / len(failure_rates)
    wasted_ci_minutes = average_failure_rate * runs_per_day * avg_job_minutes
    developer_minutes = wasted_ci_minutes * 0.35
    return wasted_ci_minutes, developer_minutes


def likely_fix(bucket: str) -> str:
    return {
        "timeout_or_wait": "Replace fixed sleeps with readiness checks and add timestamped trace artifacts.",
        "network_or_external_service": "Stub or contract-test the external dependency; keep one integration canary outside the blocking path.",
        "order_or_state_leak": "Reset shared state and run the failing test in randomized order to isolate pollution.",
        "parallelism_or_race": "Allocate per-worker resources and remove shared mutable setup.",
        "clock_locale_or_randomness": "Freeze time, persist random seed, and pin locale/timezone in CI.",
        "resource_or_runner": "Capture runner metadata, memory, CPU, browser version, and image digest.",
        "selector_or_ui_sync": "Use stable roles/test IDs and wait for application readiness instead of DOM presence alone.",
        "assertion_or_product_regression": "Debug the product or test expectation as a deterministic regression.",
        "unknown_needs_instrumentation": "Add screenshots, traces, seed, retry metadata, and runner details before rerunning.",
    }.get(bucket, "Add targeted instrumentation before changing behavior.")


def render_report(failures: list[Failure], histories: dict[str, History], avg_job_minutes: float, runs_per_day: float) -> str:
    wasted_ci, developer_minutes = estimate_cost(histories, avg_job_minutes, runs_per_day)
    lines = [
        "## CI Decision",
        overall_decision(failures),
        "",
        "## Failure Cluster",
        "| Test | Bucket | Flake confidence | Evidence | Owner | Action |",
        "|---|---|---|---|---|---|",
    ]
    if failures:
        for failure in failures:
            evidence = "; ".join(failure.evidence) if failure.evidence else "limited evidence"
            owner = failure.owner or "unassigned"
            lines.append(f"| `{failure.test}` | `{failure.bucket}` | {failure.confidence} | {evidence} | {owner} | {failure.action} |")
    else:
        lines.append("| No failing test parsed | `unknown_needs_instrumentation` | low | Provide JUnit XML or log excerpt | unassigned | Instrument then rerun |")

    lines.extend(
        [
            "",
            "## Cost And Frequency",
            f"- Average job minutes: {avg_job_minutes:g}" if avg_job_minutes else "- Average job minutes: not provided",
            f"- Runs per day: {runs_per_day:g}" if runs_per_day else "- Runs per day: not provided",
            f"- Estimated wasted CI minutes/day: {wasted_ci:.1f}" if wasted_ci else "- Estimated wasted CI minutes/day: not enough history/cost data",
            f"- Developer interruption estimate/day: {developer_minutes:.1f} minutes" if developer_minutes else "- Developer interruption estimate/day: not enough history/cost data",
            "",
            "## Likely Root Cause",
        ]
    )
    seen_buckets: set[str] = set()
    for failure in failures:
        if failure.bucket in seen_buckets:
            continue
        seen_buckets.add(failure.bucket)
        lines.append(f"- `{failure.bucket}`: {likely_fix(failure.bucket)}")
    if not seen_buckets:
        lines.append("- Unknown: add structured artifacts before changing test behavior.")

    lines.extend(["", "## Minimal Fix Plan"])
    for index, bucket in enumerate(seen_buckets or {"unknown_needs_instrumentation"}, start=1):
        lines.append(f"{index}. {likely_fix(bucket)}")

    lines.extend(
        [
            "",
            "## Instrumentation To Add",
            "- Persist retry number, commit SHA, runner image, worker ID, seed, timezone, browser/runtime version, and artifact links.",
            "- Attach JUnit XML, trace/screenshot/log snippets, and whether a retry passed without code changes.",
            "",
            "## Guardrails",
            "- Do not quarantine deterministic assertion failures without owner approval.",
            "- Quarantine entries need an owner, expiry date, and tracking issue.",
            "- Avoid blanket retries that hide release-blocking failures.",
        ]
    )
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze flaky CI failures from local artifacts.")
    parser.add_argument("--junit", type=Path, help="JUnit XML report path")
    parser.add_argument("--log", type=Path, help="CI log path")
    parser.add_argument("--history", type=Path, help="Optional test history CSV")
    parser.add_argument("--avg-job-minutes", type=float, default=0.0, help="Average CI job duration in minutes")
    parser.add_argument("--runs-per-day", type=float, default=0.0, help="Approximate number of CI runs per day")
    parser.add_argument("--output", type=Path, help="Optional Markdown output path")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.junit and not args.log:
        parser.error("provide --junit, --log, or both")

    try:
        failures = parse_junit(args.junit)
        histories = parse_history(args.history)
        log_text = read_text(args.log)
    except (OSError, ET.ParseError, csv.Error) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if not failures and log_text:
        failures = [Failure(test="log_excerpt", classname="", kind="log", message="", details=log_text[:2000])]

    for failure in failures:
        history = histories.get(failure.test)
        enrich(failure, history, log_text)

    report = render_report(failures, histories, args.avg_job_minutes, args.runs_per_day)
    if args.output:
        args.output.write_text(report + "\n", encoding="utf-8")
    else:
        print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
