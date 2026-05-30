#!/usr/bin/env python3
"""Run the local smoke checks for generated skills in this workspace."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent


@dataclass(frozen=True)
class Check:
    name: str
    command: list[str]
    expected_returncodes: set[int]
    must_contain: tuple[str, ...] = ()


CHECKS = (
    Check(
        name="chargeback-evidence-pack fixture",
        command=[
            sys.executable,
            "chargeback-evidence-pack/scripts/chargeback_evidence_pack.py",
            "--case",
            "chargeback-evidence-pack/scripts/fixtures/case_product_not_received.json",
            "--evidence-dir",
            "chargeback-evidence-pack/scripts/fixtures/evidence",
            "--today",
            "2026-05-14",
        ],
        expected_returncodes={0},
        must_contain=("Challenge candidate", "customer_communication"),
    ),
    Check(
        name="csv-import-preflight bad import fixture",
        command=[
            sys.executable,
            "csv-import-preflight/scripts/csv_import_preflight.py",
            "csv-import-preflight/scripts/fixtures/bad_import.csv",
            "--schema",
            "csv-import-preflight/scripts/fixtures/schema.json",
        ],
        # Exit 2 is intentional: the fixture should block a risky import.
        expected_returncodes={2},
        must_contain=("Decision: **Block import**", "duplicate_unique_key"),
    ),
    Check(
        name="security-questionnaire-triage fixture",
        command=[
            sys.executable,
            "security-questionnaire-triage/scripts/security_questionnaire_triage.py",
            "security-questionnaire-triage/scripts/fixtures/security_questions.csv",
            "--evidence-register",
            "security-questionnaire-triage/scripts/fixtures/evidence_register.csv",
            "--answer-bank",
            "security-questionnaire-triage/scripts/fixtures/answer_bank.csv",
        ],
        expected_returncodes={0},
        must_contain=("ready_with_cited_answer", "do_not_answer_in_sheet"),
    ),
    Check(
        name="dsar-request-preflight fixture",
        command=[
            sys.executable,
            "dsar-request-preflight/scripts/dsar_request_preflight.py",
            "--requests",
            "dsar-request-preflight/scripts/fixtures/requests.csv",
            "--systems",
            "dsar-request-preflight/scripts/fixtures/systems.csv",
            "--policy",
            "dsar-request-preflight/scripts/fixtures/policy.json",
            "--today",
            "2026-05-30",
        ],
        expected_returncodes={2},
        must_contain=(
            "DSAR Request Decision",
            "Hold fulfillment pending repair",
            "response_deadline_overdue",
            "identity_verification_missing",
            "authorized_agent_proof_missing",
            "deletion_blocked_or_exception_needed",
            "access_export_not_supported",
            "sensitive_or_minor_data_context",
            "missing_received_date",
        ),
    ),
    Check(
        name="flaky-ci-forensics fixture",
        command=[
            sys.executable,
            "flaky-ci-forensics/scripts/flaky_ci_forensics.py",
            "--junit",
            "flaky-ci-forensics/scripts/fixtures/junit.xml",
            "--log",
            "flaky-ci-forensics/scripts/fixtures/ci.log",
            "--history",
            "flaky-ci-forensics/scripts/fixtures/history.csv",
            "--avg-job-minutes",
            "14",
            "--runs-per-day",
            "60",
        ],
        expected_returncodes={0},
        must_contain=("CI Decision", "timeout_or_wait", "network_or_external_service", "Estimated wasted CI minutes/day"),
    ),
    Check(
        name="home-inventory-claim-preflight fixture",
        command=[
            sys.executable,
            "home-inventory-claim-preflight/scripts/home_inventory_claim_preflight.py",
            "--inventory",
            "home-inventory-claim-preflight/scripts/fixtures/contents_inventory.csv",
            "--policy",
            "home-inventory-claim-preflight/scripts/fixtures/policy.json",
        ],
        expected_returncodes={2},
        must_contain=(
            "Contents Claim Decision",
            "Hold packet pending evidence repair",
            "missing_ownership_evidence",
            "policy_sublimit_or_scheduled_property_review",
            "request_replacement_cost_support",
            "business_property_sublimit_review",
        ),
    ),
    Check(
        name="feature-flag-debt-audit fixture",
        command=[
            sys.executable,
            "feature-flag-debt-audit/scripts/feature_flag_debt_audit.py",
            "--flags",
            "feature-flag-debt-audit/scripts/fixtures/flags.csv",
            "--code-dir",
            "feature-flag-debt-audit/scripts/fixtures/sample_app",
            "--stale-days",
            "90",
            "--today",
            "2026-05-12",
        ],
        expected_returncodes={0},
        must_contain=(
            "Flag Debt Decision",
            "checkout_v2",
            "delete_candidate",
            "kill_checkout_payments",
            "keep_permanent",
        ),
    ),
    Check(
        name="ap-duplicate-payment-preflight fixture",
        command=[
            sys.executable,
            "ap-duplicate-payment-preflight/scripts/ap_duplicate_payment_preflight.py",
            "--payments",
            "ap-duplicate-payment-preflight/scripts/fixtures/ap_payments.csv",
            "--date-window-days",
            "14",
        ],
        expected_returncodes={0},
        must_contain=(
            "Payment Run Decision",
            "hold_payment",
            "ap_review",
            "paid_vs_pending_collision",
        ),
    ),
    Check(
        name="contract-renewal-risk-preflight fixture",
        command=[
            sys.executable,
            "contract-renewal-risk-preflight/scripts/contract_renewal_risk_preflight.py",
            "--contracts",
            "contract-renewal-risk-preflight/scripts/fixtures/contracts.csv",
            "--today",
            "2026-05-16",
        ],
        expected_returncodes={0},
        must_contain=(
            "Renewal Portfolio Decision",
            "escalate_missed_window",
            "send_or_escalate_notice",
            "missing_notice_deadline",
            "uncapped_price_increase",
        ),
    ),
    Check(
        name="customer-escalation-timeline fixture",
        command=[
            sys.executable,
            "customer-escalation-timeline/scripts/customer_escalation_timeline.py",
            "--tickets",
            "customer-escalation-timeline/scripts/fixtures/tickets.csv",
            "--events",
            "customer-escalation-timeline/scripts/fixtures/events.csv",
            "--accounts",
            "customer-escalation-timeline/scripts/fixtures/accounts.csv",
            "--now",
            "2026-05-21T09:00:00",
        ],
        expected_returncodes={0},
        must_contain=(
            "Escalation Timeline Decision",
            "owner_acceptance_required",
            "customer_update_due",
            "handoff_packet_required",
            "repeat_contact_or_fix_validation",
        ),
    ),
    Check(
        name="employee-offboarding-access-preflight fixture",
        command=[
            sys.executable,
            "employee-offboarding-access-preflight/scripts/employee_offboarding_access_preflight.py",
            "--departures",
            "employee-offboarding-access-preflight/scripts/fixtures/departures.csv",
            "--accounts",
            "employee-offboarding-access-preflight/scripts/fixtures/accounts.csv",
            "--groups",
            "employee-offboarding-access-preflight/scripts/fixtures/groups.csv",
            "--assets",
            "employee-offboarding-access-preflight/scripts/fixtures/assets.csv",
            "--secrets",
            "employee-offboarding-access-preflight/scripts/fixtures/secrets.csv",
            "--today",
            "2026-05-20",
        ],
        expected_returncodes={0},
        must_contain=(
            "Offboarding Access Decision",
            "revoke_now",
            "rotate_or_reassign_secret",
            "shadow_saas_or_direct_login",
            "privileged_access_after_departure",
        ),
    ),
    Check(
        name="saas-license-rightsize fixture",
        command=[
            sys.executable,
            "saas-license-rightsize/scripts/saas_license_rightsize.py",
            "--licenses",
            "saas-license-rightsize/scripts/fixtures/licenses.csv",
            "--employees",
            "saas-license-rightsize/scripts/fixtures/employees.csv",
            "--usage",
            "saas-license-rightsize/scripts/fixtures/usage.csv",
            "--today",
            "2026-05-17",
        ],
        expected_returncodes={0},
        must_contain=(
            "License Portfolio Decision",
            "Potential annual savings",
            "departed_employee_active_license",
            "reclaim_now",
            "downgrade_review",
        ),
    ),
    Check(
        name="utm-governance-preflight fixture",
        command=[
            sys.executable,
            "utm-governance-preflight/scripts/utm_governance_preflight.py",
            "--links",
            "utm-governance-preflight/scripts/fixtures/campaign_links.csv",
            "--policy",
            "utm-governance-preflight/scripts/fixtures/policy.json",
        ],
        expected_returncodes={2},
        must_contain=(
            "UTM Governance Decision",
            "Block launch",
            "missing_required_utm",
            "source_medium_swapped",
            "sensitive_internal_term",
            "alias_to_canonical_source",
        ),
    ),
    Check(
        name="vendor-bank-change-preflight fixture",
        command=[
            sys.executable,
            "vendor-bank-change-preflight/scripts/vendor_bank_change_preflight.py",
            "--requests",
            "vendor-bank-change-preflight/scripts/fixtures/bank_change_requests.csv",
            "--vendor-master",
            "vendor-bank-change-preflight/scripts/fixtures/vendor_master.csv",
        ],
        expected_returncodes={0},
        must_contain=(
            "Bank Change Decision",
            "hold_change",
            "secondary_verification",
            "lookalike_email_domain",
            "bank_account_reused_by_another_vendor",
        ),
    ),
    Check(
        name="invoice-three-way-match-preflight fixture",
        command=[
            sys.executable,
            "invoice-three-way-match-preflight/scripts/invoice_three_way_match_preflight.py",
            "--invoices",
            "invoice-three-way-match-preflight/scripts/fixtures/invoices.csv",
            "--purchase-orders",
            "invoice-three-way-match-preflight/scripts/fixtures/purchase_orders.csv",
            "--receipts",
            "invoice-three-way-match-preflight/scripts/fixtures/receipts.csv",
        ],
        expected_returncodes={0},
        must_contain=(
            "Three-Way Match Decision",
            "hold_invoice",
            "invoice_quantity_exceeds_received",
            "unit_price_variance",
            "vendor_mismatch",
            "closed_or_cancelled_po",
        ),
    ),
    Check(
        name="medical-bill-dispute-preflight fixture",
        command=[
            sys.executable,
            "medical-bill-dispute-preflight/scripts/medical_bill_dispute_preflight.py",
            "--bills",
            "medical-bill-dispute-preflight/scripts/fixtures/medical_bills.csv",
            "--eob",
            "medical-bill-dispute-preflight/scripts/fixtures/eob.csv",
            "--policy",
            "medical-bill-dispute-preflight/scripts/fixtures/policy.json",
        ],
        expected_returncodes={2},
        must_contain=(
            "Medical Bill Dispute Decision",
            "Hold payment pending reconciliation",
            "balance_exceeds_eob_patient_responsibility",
            "missing_eob_or_unprocessed_insurance",
            "request_itemized_bill",
            "no_surprises_review",
            "appeal_review",
        ),
    ),
    Check(
        name="expense-reimbursement-preflight fixture",
        command=[
            sys.executable,
            "expense-reimbursement-preflight/scripts/expense_reimbursement_preflight.py",
            "--expenses",
            "expense-reimbursement-preflight/scripts/fixtures/expense_report.csv",
            "--policy",
            "expense-reimbursement-preflight/scripts/fixtures/policy.json",
            "--today",
            "2026-05-26",
        ],
        expected_returncodes={2},
        must_contain=(
            "Expense Reimbursement Decision",
            "Hold reimbursement",
            "missing_receipt",
            "duplicate_receipt_or_charge",
            "meal_attendees_missing",
            "mileage_rate_exceeds_policy",
        ),
    ),
    Check(
        name="parcel-claim-preflight fixture",
        command=[
            sys.executable,
            "parcel-claim-preflight/scripts/parcel_claim_preflight.py",
            "--shipments",
            "parcel-claim-preflight/scripts/fixtures/shipments.csv",
            "--evidence-dir",
            "parcel-claim-preflight/scripts/fixtures/evidence",
            "--today",
            "2026-05-31",
        ],
        expected_returncodes={2},
        must_contain=(
            "Parcel Claim Decision",
            "Hold claim pending evidence repair",
            "damage_photos_missing",
            "packaging_photos_missing",
            "original_packaging_unavailable",
            "claim_deadline_passed",
        ),
    ),
)


def run_check(check: Check) -> bool:
    result = subprocess.run(
        check.command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    output = result.stdout
    ok = result.returncode in check.expected_returncodes and all(
        needle in output for needle in check.must_contain
    )
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {check.name} (exit {result.returncode})")
    if not ok:
        print(output.rstrip())
    return ok


def main() -> int:
    passed = 0
    for check in CHECKS:
        if run_check(check):
            passed += 1
    total = len(CHECKS)
    print(f"\n{passed}/{total} checks passed.")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
