#!/usr/bin/env python3
"""Local CSV/TSV import preflight checks.

The script is intentionally dependency-free so it can run in a Codex workspace
before a user uploads data to a SaaS importer or database staging table.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field as dataclass_field
from datetime import datetime
from pathlib import Path
from typing import Any


FORMULA_PREFIXES = ("=", "+", "-", "@")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
INT_RE = re.compile(r"^[+-]?\d+$")
DECIMAL_RE = re.compile(r"^[+-]?(?:\d+|\d{1,3}(?:,\d{3})+)(?:\.\d+)?$")
ID_NAME_RE = re.compile(r"(id|sku|zip|postal|phone|account|number|code)$", re.I)
PII_NAME_RE = re.compile(r"(email|phone|ssn|tax|dob|birth|address)", re.I)
DATE_FORMATS = (
    "%Y-%m-%d",
    "%Y/%m/%d",
    "%m/%d/%Y",
    "%d/%m/%Y",
    "%m-%d-%Y",
    "%d-%m-%Y",
    "%Y%m%d",
)


@dataclass(order=True)
class Issue:
    sort_key: tuple[int, str, str] = dataclass_field(init=False, repr=False)
    severity: str
    code: str
    message: str
    field: str = ""
    rows: list[int] = dataclass_field(default_factory=list)
    fix: str = ""

    def __post_init__(self) -> None:
        order = {"high": 0, "medium": 1, "low": 2}
        self.sort_key = (order.get(self.severity, 9), self.code, self.field)


def normalize_header(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip()).lower()


def nonblank(value: str | None) -> bool:
    return value is not None and value.strip() != ""


def load_schema(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("schema must be a JSON object")
    return data


def schema_list(schema: dict[str, Any], *names: str) -> list[str]:
    for name in names:
        value = schema.get(name)
        if isinstance(value, list):
            return [str(item) for item in value]
    return []


def open_text(path: Path) -> str:
    for encoding in ("utf-8-sig", "utf-8"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="latin-1")


def sniff_dialect(text: str, delimiter: str | None) -> csv.Dialect:
    sample = text[:8192]
    if delimiter:
        class ManualDialect(csv.excel):
            pass

        ManualDialect.delimiter = delimiter
        return ManualDialect
    try:
        return csv.Sniffer().sniff(sample, delimiters=",\t;|")
    except csv.Error:
        if "\t" in sample and sample.count("\t") >= sample.count(","):
            class TsvDialect(csv.excel_tab):
                pass

            return TsvDialect
        return csv.excel


def read_rows(path: Path, delimiter: str | None) -> tuple[list[str], list[list[str]], csv.Dialect]:
    text = open_text(path)
    dialect = sniff_dialect(text, delimiter)
    rows = list(csv.reader(io.StringIO(text), dialect))
    if not rows:
        return [], [], dialect
    return rows[0], rows[1:], dialect


def parse_date(value: str) -> set[str]:
    matches: set[str] = set()
    for fmt in DATE_FORMATS:
        try:
            datetime.strptime(value, fmt)
            matches.add(fmt)
        except ValueError:
            pass
    return matches


def ambiguous_date(value: str) -> bool:
    parts = re.split(r"[/-]", value.strip())
    if len(parts) != 3:
        return False
    if len(parts[0]) == 4:
        return False
    try:
        first = int(parts[0])
        second = int(parts[1])
    except ValueError:
        return False
    return 1 <= first <= 12 and 1 <= second <= 12 and first != second


def add_issue(
    issues: list[Issue],
    severity: str,
    code: str,
    message: str,
    field: str = "",
    rows: list[int] | None = None,
    fix: str = "",
) -> None:
    issues.append(Issue(severity, code, message, field, rows or [], fix))


def resolve_columns(headers: list[str], wanted: list[str]) -> tuple[list[str], list[str]]:
    exact = set(headers)
    norm_to_header = {normalize_header(header): header for header in headers}
    found: list[str] = []
    missing: list[str] = []
    for name in wanted:
        if name in exact:
            found.append(name)
            continue
        normalized = normalize_header(name)
        if normalized in norm_to_header:
            found.append(norm_to_header[normalized])
        else:
            missing.append(name)
    return found, missing


def cell_values(headers: list[str], rows: list[list[str]], row_index: int) -> dict[str, str]:
    row = rows[row_index]
    return {header: row[pos].strip() if pos < len(row) else "" for pos, header in enumerate(headers)}


def analyze(path: Path, schema: dict[str, Any], delimiter: str | None, max_rows: int) -> dict[str, Any]:
    headers, data_rows, dialect = read_rows(path, delimiter)
    issues: list[Issue] = []
    if not headers:
        add_issue(issues, "high", "empty_file", "No header row was found.", fix="Export a CSV with a single header row.")
        return build_result(path, dialect, headers, data_rows, issues, [], max_rows, schema)

    if len(data_rows) > max_rows:
        add_issue(
            issues,
            "medium",
            "row_limit",
            f"Only the first {max_rows} rows were analyzed out of {len(data_rows)} data rows.",
            fix="Rerun with a higher --max-rows value before a final import decision.",
        )
        data_rows = data_rows[:max_rows]

    blank_headers = [idx + 1 for idx, header in enumerate(headers) if not header.strip()]
    if blank_headers:
        add_issue(
            issues,
            "high",
            "blank_header",
            f"Blank header cells at positions {blank_headers}.",
            fix="Name every column before import.",
        )

    normalized_headers = [normalize_header(header) for header in headers]
    dup_norm = [name for name, count in Counter(normalized_headers).items() if name and count > 1]
    for name in dup_norm:
        variants = [headers[i] for i, normalized in enumerate(normalized_headers) if normalized == name]
        add_issue(
            issues,
            "high",
            "duplicate_header",
            f"Headers collapse to the same target name after trimming/case normalization: {variants}.",
            field=name,
            fix="Rename or remove duplicate columns so the importer binds one source column to one target field.",
        )

    if any(header != header.strip() for header in headers):
        add_issue(
            issues,
            "medium",
            "header_whitespace",
            "One or more headers contain leading/trailing whitespace.",
            fix="Trim header whitespace before mapping fields.",
        )

    expected_len = len(headers)
    for idx, row in enumerate(data_rows, start=2):
        if len(row) != expected_len:
            add_issue(
                issues,
                "high",
                "row_shape",
                f"Row has {len(row)} cells but header has {expected_len}.",
                rows=[idx],
                fix="Repair quoting, delimiters, or missing trailing cells before import.",
            )

    required_cols, missing_required_cols = resolve_columns(
        headers,
        schema_list(schema, "required_columns", "required"),
    )
    for name in missing_required_cols:
        add_issue(
            issues,
            "high",
            "missing_required_column",
            f"Required target column is missing: {name}.",
            field=name,
            fix="Add the column or revise the target mapping.",
        )

    profiles: list[dict[str, Any]] = []
    values_by_column: dict[str, list[tuple[int, str]]] = defaultdict(list)
    for row_idx in range(len(data_rows)):
        row_values = cell_values(headers, data_rows, row_idx)
        for header in headers:
            values_by_column[header].append((row_idx + 2, row_values.get(header, "")))

    leading_zero_fields: set[str] = set()
    for header in headers:
        cells = values_by_column[header]
        non_empty = [(row, value) for row, value in cells if nonblank(value)]
        blanks = len(cells) - len(non_empty)
        distinct = len({value for _, value in non_empty})
        samples = []
        for _, value in non_empty:
            if value not in samples:
                samples.append(value)
            if len(samples) >= 3:
                break
        profiles.append(
            {
                "column": header,
                "non_empty": len(non_empty),
                "blank": blanks,
                "distinct": distinct,
                "sample": samples,
            }
        )

        if PII_NAME_RE.search(header):
            add_issue(
                issues,
                "low",
                "pii_column",
                "Column name suggests personal or regulated data.",
                field=header,
                fix="Confirm handling rules, access limits, and whether a masked test batch is safer.",
            )

        if ID_NAME_RE.search(header):
            leading_zero_rows = [
                row for row, value in non_empty if len(value) > 1 and value.startswith("0") and value.isdigit()
            ][:8]
            if leading_zero_rows:
                leading_zero_fields.add(header)
                add_issue(
                    issues,
                    "medium",
                    "leading_zero_risk",
                    "Identifier-like values contain leading zeros that spreadsheets/importers may coerce.",
                    field=header,
                    rows=leading_zero_rows,
                    fix="Keep this field as text and verify target mapping does not coerce it to a number.",
                )

    id_columns, missing_id_columns = resolve_columns(headers, schema_list(schema, "id_columns", "ids"))
    for name in missing_id_columns:
        add_issue(
            issues,
            "medium",
            "missing_id_column",
            f"Identifier column listed in schema is missing: {name}.",
            field=name,
            fix="Confirm whether this column is required for associations, dedupe, or upsert.",
        )
    for header in id_columns:
        if header in leading_zero_fields:
            continue
        leading_zero_rows = [
            row
            for row, value in values_by_column[header]
            if len(value.strip()) > 1 and value.strip().startswith("0") and value.strip().isdigit()
        ][:8]
        if leading_zero_rows:
            add_issue(
                issues,
                "medium",
                "leading_zero_risk",
                "Schema marks this as an identifier and values contain leading zeros.",
                field=header,
                rows=leading_zero_rows,
                fix="Keep this field as text and verify target mapping does not coerce it to a number.",
            )

    for header in required_cols:
        blank_rows = [row for row, value in values_by_column[header] if not nonblank(value)][:12]
        if blank_rows:
            add_issue(
                issues,
                "high",
                "blank_required_value",
                "Required column contains blank values.",
                field=header,
                rows=blank_rows,
                fix="Fill, remove, or split these rows before import.",
            )

    unique_cols, missing_unique_cols = resolve_columns(headers, schema_list(schema, "unique_columns", "unique"))
    for name in missing_unique_cols:
        add_issue(
            issues,
            "high",
            "missing_unique_column",
            f"Unique/upsert key column is missing: {name}.",
            field=name,
            fix="Add a stable key or change import mode to create-only with an explicit duplicate policy.",
        )
    for header in unique_cols:
        counts: Counter[str] = Counter(
            value.strip().lower() for _, value in values_by_column[header] if nonblank(value)
        )
        duplicates = {value: count for value, count in counts.items() if count > 1}
        if duplicates:
            duplicate_rows: list[int] = []
            duplicate_values = set(duplicates)
            for row, value in values_by_column[header]:
                if value.strip().lower() in duplicate_values:
                    duplicate_rows.append(row)
                if len(duplicate_rows) >= 12:
                    break
            add_issue(
                issues,
                "high",
                "duplicate_unique_key",
                f"Unique/upsert key has duplicate values after trim/case normalization: {list(duplicates)[:5]}.",
                field=header,
                rows=duplicate_rows,
                fix="Deduplicate or choose a different stable key before any update/upsert import.",
            )

    for header in resolve_columns(headers, schema_list(schema, "date_columns", "dates"))[0]:
        bad_rows: list[int] = []
        ambiguous_rows: list[int] = []
        for row, value in values_by_column[header]:
            if not nonblank(value):
                continue
            parsed = parse_date(value.strip())
            if not parsed:
                bad_rows.append(row)
            elif ambiguous_date(value.strip()):
                ambiguous_rows.append(row)
        if bad_rows:
            add_issue(
                issues,
                "high",
                "invalid_date",
                "Date column contains values that did not parse with common import formats.",
                field=header,
                rows=bad_rows[:12],
                fix="Normalize to ISO 8601 (YYYY-MM-DD) unless the target explicitly requires another format.",
            )
        if ambiguous_rows:
            add_issue(
                issues,
                "medium",
                "ambiguous_date",
                "Date column contains values that can be read as either MM/DD/YYYY or DD/MM/YYYY.",
                field=header,
                rows=ambiguous_rows[:12],
                fix="Normalize to ISO 8601 (YYYY-MM-DD) before upload.",
            )

    for header in resolve_columns(headers, schema_list(schema, "integer_columns", "integers"))[0]:
        bad_rows = [
            row for row, value in values_by_column[header] if nonblank(value) and not INT_RE.match(value.strip())
        ][:12]
        if bad_rows:
            add_issue(
                issues,
                "high",
                "invalid_integer",
                "Integer column contains non-integer values.",
                field=header,
                rows=bad_rows,
                fix="Convert or remove invalid values before import.",
            )

    for header in resolve_columns(headers, schema_list(schema, "decimal_columns", "decimals"))[0]:
        bad_rows = [
            row for row, value in values_by_column[header] if nonblank(value) and not DECIMAL_RE.match(value.strip())
        ][:12]
        if bad_rows:
            add_issue(
                issues,
                "high",
                "invalid_decimal",
                "Decimal/currency column contains non-numeric values.",
                field=header,
                rows=bad_rows,
                fix="Normalize numbers and remove currency labels or text before import.",
            )

    enum_columns = schema.get("enum_columns") or schema.get("enums") or {}
    if isinstance(enum_columns, dict):
        for requested_header, allowed in enum_columns.items():
            resolved, missing = resolve_columns(headers, [str(requested_header)])
            if missing:
                add_issue(
                    issues,
                    "high",
                    "missing_enum_column",
                    f"Enum column is missing: {requested_header}.",
                    field=str(requested_header),
                    fix="Add the column or revise the target mapping.",
                )
                continue
            header = resolved[0]
            allowed_norm = {str(value).strip().lower() for value in allowed}
            bad_rows = [
                row
                for row, value in values_by_column[header]
                if nonblank(value) and value.strip().lower() not in allowed_norm
            ][:12]
            if bad_rows:
                add_issue(
                    issues,
                    "high",
                    "invalid_enum",
                    f"Enum column contains values outside allowed set: {list(allowed)[:12]}.",
                    field=header,
                    rows=bad_rows,
                    fix="Map source values to the exact allowed target values before upload.",
                )

    email_cols = resolve_columns(headers, schema_list(schema, "email_columns", "emails"))[0]
    for header in email_cols:
        bad_rows = [
            row for row, value in values_by_column[header] if nonblank(value) and not EMAIL_RE.match(value.strip())
        ][:12]
        if bad_rows:
            add_issue(
                issues,
                "medium",
                "invalid_email",
                "Email column contains values that do not look like email addresses.",
                field=header,
                rows=bad_rows,
                fix="Repair or remove invalid emails before using email as an identity key.",
            )

    formula_rows: list[int] = []
    formula_fields: set[str] = set()
    for header in headers:
        for row, value in values_by_column[header]:
            stripped = value.lstrip()
            if stripped.startswith(FORMULA_PREFIXES):
                formula_rows.append(row)
                formula_fields.add(header)
                if len(formula_rows) >= 12:
                    break
    if formula_rows:
        add_issue(
            issues,
            "high",
            "formula_injection",
            f"Formula-like values found in columns: {sorted(formula_fields)}.",
            rows=formula_rows[:12],
            fix="Escape or neutralize formula-leading cells before the CSV is opened in spreadsheet software.",
        )

    if not schema:
        add_issue(
            issues,
            "medium",
            "missing_target_schema",
            "No target schema was provided, so required fields, unique keys, enums, and import mode were only checked heuristically.",
            fix="Provide target required columns, unique keys, enums, and date/ID fields before a final go/no-go decision.",
        )

    return build_result(path, dialect, headers, data_rows, issues, profiles, max_rows, schema)


def build_result(
    path: Path,
    dialect: csv.Dialect,
    headers: list[str],
    data_rows: list[list[str]],
    issues: list[Issue],
    profiles: list[dict[str, Any]],
    max_rows: int,
    schema: dict[str, Any],
) -> dict[str, Any]:
    issues.sort()
    severity_counts = Counter(issue.severity for issue in issues)
    if severity_counts["high"]:
        decision = "Block import"
    elif severity_counts["medium"]:
        decision = "Proceed after cleanup"
    else:
        decision = "Proceed"
    return {
        "file": str(path),
        "rows_analyzed": len(data_rows),
        "columns": len(headers),
        "delimiter": getattr(dialect, "delimiter", ","),
        "decision": decision,
        "severity_counts": dict(severity_counts),
        "issues": [issue.__dict__ | {"sort_key": None} for issue in issues],
        "profiles": profiles,
        "schema_supplied": bool(schema),
        "max_rows": max_rows,
    }


def rows_text(rows: list[int]) -> str:
    if not rows:
        return ""
    return ", ".join(str(row) for row in rows[:12])


def render_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# CSV Import Preflight Report",
        "",
        f"- File: `{result['file']}`",
        f"- Rows analyzed: {result['rows_analyzed']}",
        f"- Columns: {result['columns']}",
        f"- Delimiter: `{result['delimiter']}`",
        f"- Decision: **{result['decision']}**",
        "",
        "## Issues",
        "",
    ]
    issues = result["issues"]
    if not issues:
        lines.append("No import blockers detected by the available checks.")
    else:
        lines.append("| Severity | Code | Field | Rows | Finding | Fix |")
        lines.append("|---|---|---|---|---|---|")
        for issue in issues:
            lines.append(
                "| {severity} | `{code}` | {field} | {rows} | {message} | {fix} |".format(
                    severity=issue["severity"],
                    code=issue["code"],
                    field=issue["field"] or "-",
                    rows=rows_text(issue["rows"]) or "-",
                    message=issue["message"].replace("|", "\\|"),
                    fix=(issue["fix"] or "-").replace("|", "\\|"),
                )
            )
    lines.extend(["", "## Column Profile", ""])
    if result["profiles"]:
        lines.append("| Column | Non-empty | Blank | Distinct | Sample |")
        lines.append("|---|---:|---:|---:|---|")
        for profile in result["profiles"]:
            sample = ", ".join(f"`{value}`" for value in profile["sample"])
            lines.append(
                f"| {profile['column']} | {profile['non_empty']} | {profile['blank']} | {profile['distinct']} | {sample} |"
            )
    else:
        lines.append("No column profile available.")
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Run local CSV/TSV import preflight checks.")
    parser.add_argument("csv_path", type=Path, help="CSV or TSV file to inspect")
    parser.add_argument("--schema", type=Path, help="Optional target schema JSON")
    parser.add_argument("--delimiter", help="Override delimiter, for example ',' or '\\t'")
    parser.add_argument("--max-rows", type=int, default=20000, help="Maximum data rows to analyze")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    args = parser.parse_args(argv)

    schema = load_schema(args.schema)
    result = analyze(args.csv_path, schema, args.delimiter, args.max_rows)
    if args.format == "json":
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(render_markdown(result))
    return 2 if result["decision"] == "Block import" else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
