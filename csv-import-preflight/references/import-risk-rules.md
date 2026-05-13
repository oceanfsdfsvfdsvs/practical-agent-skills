# Import Risk Rules

Use this reference when an import can create duplicates, overwrite existing records, corrupt identifiers, or require a rollback plan.

## Severity Rubric

| Severity | Meaning | Typical Action |
|---|---|---|
| High | Import may create destructive writes, broken associations, duplicate records, rejected required rows, or silent data corruption. | Block import until fixed or run a tiny test batch after backup. |
| Medium | Import may create manual cleanup, partial rejects, incorrect segmentation, or reporting drift. | Clean before full upload; test representative rows. |
| Low | Import may be acceptable but needs documentation or operator awareness. | Proceed with notes and validation checks. |

## Common Failure Modes

- Duplicate or unstable upsert keys: email, external ID, SKU, account number, transaction ID, or handle values repeat after trimming/case normalization.
- Header drift: duplicate headers after trimming/case folding; target systems may bind to the wrong column or reject one silently.
- Date ambiguity: `01/02/2026` can mean January 2 or February 1; invalid leap days and impossible month/day pairs should block required date fields.
- Identifier coercion: ZIP codes, SKUs, phone numbers, account numbers, and external IDs may lose leading zeros or become scientific notation if opened in a spreadsheet.
- Controlled vocabulary drift: enum values differ by casing, spacing, spelling, localization, or inactive states.
- Association ambiguity: company/contact/deal/product relations require stable parent keys; display names alone are usually unsafe.
- Update mode without backup: upsert, overwrite, merge, and delete imports need export snapshots and a rollback path.
- Formula injection: values beginning with `=`, `+`, `-`, or `@` can execute when opened in spreadsheet tools; treat as high risk if staff will review the CSV in Excel/Sheets.
- Row shape errors: inconsistent cell counts can shift data into wrong fields.
- Partial import trap: platforms may import valid rows and reject invalid rows, leaving the dataset split unless a reconciliation plan exists.

## Platform-Oriented Focus

CRM imports:

- Confirm object type, unique key, duplicate handling, owner fields, lifecycle/stage enums, association keys, and whether blank fields overwrite existing data.
- For contacts/companies, prefer stable IDs or verified domains over display names for associations.

Accounting and banking imports:

- Confirm sign conventions, date format, decimal separator, currency, transaction ID uniqueness, and whether duplicate prevention is available.
- Never infer missing money direction from description text without user confirmation.

Ecommerce catalog imports:

- Confirm handle/SKU uniqueness, variant grouping, option names, image URLs, inventory policy, publish status, and whether blank fields clear existing values.
- Test one product with variants before a full catalog upload.

Database imports:

- Confirm primary keys, foreign keys, nullability, enum/check constraints, encoding, delimiter, quote escaping, and transaction/rollback strategy.
- Prefer loading into a staging table and validating counts before merging into production tables.

## Platform Schema Starters

Use these as scaffolds when the user does not yet have an official target schema. Do not treat them as authoritative without target confirmation.

HubSpot contact import:

```json
{
  "required_columns": ["email"],
  "unique_columns": ["email"],
  "email_columns": ["email"],
  "date_columns": ["create_date", "last_activity_date"],
  "enum_columns": {
    "lifecyclestage": ["subscriber", "lead", "marketingqualifiedlead", "salesqualifiedlead", "opportunity", "customer", "evangelist", "other"]
  },
  "id_columns": ["record_id", "company_domain"]
}
```

Salesforce account/contact import:

```json
{
  "required_columns": ["external_id"],
  "unique_columns": ["external_id"],
  "email_columns": ["email"],
  "date_columns": ["created_date", "last_modified_date"],
  "id_columns": ["external_id", "account_id", "owner_id"],
  "enum_columns": {
    "status": ["active", "inactive"]
  }
}
```

Shopify product import:

```json
{
  "required_columns": ["handle", "title"],
  "unique_columns": ["handle", "variant_sku"],
  "decimal_columns": ["variant_price", "variant_compare_at_price"],
  "integer_columns": ["variant_inventory_qty"],
  "id_columns": ["handle", "variant_sku", "variant_barcode"],
  "enum_columns": {
    "published": ["true", "false"],
    "variant_inventory_policy": ["deny", "continue"]
  }
}
```

Postgres staging import:

```json
{
  "required_columns": ["id"],
  "unique_columns": ["id"],
  "date_columns": ["created_at", "updated_at"],
  "integer_columns": ["quantity"],
  "decimal_columns": ["amount"],
  "id_columns": ["id", "external_id", "account_id"]
}
```

## Safe Upload Checklist

1. Export or snapshot current target records.
2. Save the exact source file, cleaned file, schema/mapping, and script report.
3. Run a small test batch that covers normal rows, edge dates, duplicates, blanks, associations, and variants.
4. Compare created/updated/skipped counts against expectations.
5. Validate a sample in the target UI and, when available, with an export/query.
6. Only then run the full import; keep rejected rows and reconcile them immediately.
