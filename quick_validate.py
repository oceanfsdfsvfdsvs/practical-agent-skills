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
