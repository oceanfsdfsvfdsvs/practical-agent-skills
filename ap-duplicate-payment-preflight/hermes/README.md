# Hermes Notes

Hermes native skill packaging is blocked for runtime verification in this workspace because the current local Hermes skill spec was not confirmed during creation.

Use this directory as a portable source package:

1. Copy `ap-duplicate-payment-preflight/` into the Hermes-compatible skills or tools location.
2. Configure Hermes to call `scripts/ap_duplicate_payment_preflight.py` with explicit input paths.
3. Run the fixture command from `SKILL.md` and compare the Markdown report to `examples/sample-report.md`.

Status: `blocked-for-runtime-verification`. No native `handler.js` or `skill.yaml` is claimed here until the Hermes spec is verified.
