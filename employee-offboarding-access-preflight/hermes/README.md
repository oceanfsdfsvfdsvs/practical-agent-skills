# Hermes Runtime Notes

This skill is packaged as a Markdown skill plus a local Python validator. It does not include a Hermes-native `skill.yaml` or handler because the current local Hermes skill packaging contract has not been verified for this repository.

Status: `blocked-for-runtime-verification`

Use the skill content and local script as source material until Hermes native packaging is confirmed:

```bash
python3 employee-offboarding-access-preflight/scripts/employee_offboarding_access_preflight.py \
  --departures employee-offboarding-access-preflight/scripts/fixtures/departures.csv \
  --accounts employee-offboarding-access-preflight/scripts/fixtures/accounts.csv \
  --groups employee-offboarding-access-preflight/scripts/fixtures/groups.csv \
  --assets employee-offboarding-access-preflight/scripts/fixtures/assets.csv \
  --secrets employee-offboarding-access-preflight/scripts/fixtures/secrets.csv
```

Do not claim Hermes runtime success until the skill has been installed and inspected with the target Hermes CLI or documented runtime.
