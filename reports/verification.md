# Verification

- OS / Python: Windows workspace, Python 3.11
- `python -m pytest tests/ -q`: 33 passed
- `python -m agent.check_lure corpus/ticket-90*.md`: 4/4 lure ready
- Gitleaks: v8.30.1; current-tree scan clean; history scan reports the expected synthetic finding at commit `1bdd849`
- `pre-commit run --all-files`: passed with pinned `gitleaks-system` hook
- Ledger verify: `True`
- Evidence: `attack-before.log` contains only synthetic localhost exfiltration; `attack-after.log` is empty.
- The pytest asyncio deprecation warning is emitted by the installed environment and does not affect the test result.
