---
name: csv-import-preflight
description: Inspect CSV/TSV files before upload into CRMs, accounting tools, ecommerce catalogs, databases, or other SaaS importers. Use when a user wants to validate a spreadsheet export, diagnose import errors, reduce duplicate/overwrite risk, map columns to a target schema, or create a go/no-go import plan before loading records.
---

# CSV Import Preflight

## Overview

Use this skill to catch destructive or time-wasting CSV import failures before the user uploads data. The goal is a risk-ranked import decision, not generic data cleanup.

## Use and Do Not Use

Use for:

- CRM/contact/company/deal imports, including dedupe keys and associations.
- Accounting, banking, ecommerce, inventory, ticketing, LMS, HRIS, or database imports.
- CSV/TSV files that may contain duplicate IDs, malformed dates, enum drift, missing required fields, formula injection, encoding issues, or values that apps may coerce.
- Import error triage when the user has an error export, rejected rows file, or target schema.

Do not use for:

- Creating or formatting a spreadsheet artifact for presentation; use the spreadsheet skill instead.
- General ETL implementation, database migrations, or API integration unless a CSV import preflight is the blocking step.
- Blindly fixing production data through a live SaaS/API. This skill is local-first and produces an import plan unless the user explicitly asks for an authorized write path.

## Required Inputs

Ask only for missing inputs that affect the import decision:

- Source file path, pasted sample, or rejected-row export.
- Target system and object type, such as HubSpot contacts, Salesforce accounts, Shopify products, bank transactions, or Postgres table.
- Target field requirements: required columns, unique keys, allowed values, date format, ID fields, and association fields.
- Desired import mode: create only, update existing, upsert, overwrite, delete, merge, or unknown.
- Rollback constraints, backup availability, and acceptable manual review volume.

If no target schema is available, run a generic profile and mark schema-dependent risks as "needs target confirmation" instead of inventing rules.

## Workflow

### 1. Classify Import Risk

Identify:

- Import object and blast radius.
- Whether records can be overwritten, merged, duplicated, or silently skipped.
- Natural keys and external IDs.
- Required fields and association fields.
- Fields likely to be coerced by the target system: dates, ZIP/postal codes, SKUs, account numbers, phone numbers, currency, booleans, and enums.

Read `references/import-risk-rules.md` when the import has platform-specific consequences, update/upsert semantics, or high-risk fields. Use its platform schema examples for HubSpot, Salesforce, Shopify, and Postgres-style imports when the user lacks a target schema, and label those assumptions as examples rather than confirmed target rules.

### 2. Run Local Preflight

Use the bundled script for file-backed CSV/TSV checks:

```bash
python3 csv-import-preflight/scripts/csv_import_preflight.py /absolute/path/import.csv --schema /absolute/path/schema.json
```

Schema JSON is optional. Supported keys:

```json
{
  "required_columns": ["email", "external_id"],
  "unique_columns": ["email", "external_id"],
  "date_columns": ["signup_date"],
  "integer_columns": ["quantity"],
  "decimal_columns": ["amount"],
  "id_columns": ["sku", "zip"],
  "email_columns": ["email"],
  "enum_columns": {
    "status": ["active", "inactive"]
  }
}
```

For pasted samples or spreadsheet screenshots, apply the same checks manually and say that the result is sample-limited.

### 3. Separate Blockers From Cleanup

Treat as blockers:

- Missing required columns.
- Duplicate values in update/upsert keys.
- Malformed or ambiguous dates in required date fields.
- Invalid enum values for controlled fields.
- Rows with too many/few cells.
- Formula injection in files that will be opened in spreadsheets or imported by staff.
- Update imports without a stable key or backup.

Treat as cleanup unless target rules make it blocking:

- Header casing/whitespace drift.
- High blank rate in optional columns.
- Possible leading-zero coercion.
- Mixed numeric/text types in optional fields.
- PII columns that require handling guidance.

### 4. Produce the Import Plan

Return:

```markdown
## Import Decision
[Proceed / Proceed after cleanup / Block import]

## Risk Summary
| Risk | Severity | Rows/Columns | Why it matters | Fix |
|---|---|---|---|---|

## Mapping and Keys
[Target object, required fields, unique/upsert key, association fields]

## Cleanup Patch
[Concrete transformations, row filters, or formulas/scripts to apply]

## Safe Upload Steps
[Backup/export, small test batch, validation queries, rollback notes]

## Open Questions
[Only items that materially affect import safety]
```

## Examples and Acceptance Checks

Positive CRM example: "Use $csv-import-preflight on contacts.csv before a HubSpot/Salesforce upload. Email is unique, lifecycle_stage is an enum, and company_domain associates contacts to companies." The skill should run the script with a schema, block duplicate emails and invalid enum values, and produce a safe test-batch plan.

Positive ecommerce example: "Check this Shopify product CSV before upload; variants must not overwrite SKUs." The skill should focus on handle/SKU uniqueness, option consistency, blank required product fields, and variant grouping risks.

Negative example: "Write a Python parser for CSV files in my app." Do not trigger this skill unless the user is validating an import dataset or import workflow; handle it as a normal coding request.

Boundary example: "I only have a screenshot of the first 20 rows." The skill should do a sample-limited manual preflight, state that row-count and duplicate checks are incomplete, and ask for the file before giving a go decision.

## Validation

Smoke-test the bundled fixture:

```bash
python3 csv-import-preflight/scripts/csv_import_preflight.py csv-import-preflight/scripts/fixtures/bad_import.csv --schema csv-import-preflight/scripts/fixtures/schema.json
```

Expected result: a Markdown report that blocks import because it detects duplicate normalized headers, duplicate unique keys, missing required values, invalid decimals/enums, malformed or ambiguous dates, formula-like cells, and leading-zero coercion risk.
