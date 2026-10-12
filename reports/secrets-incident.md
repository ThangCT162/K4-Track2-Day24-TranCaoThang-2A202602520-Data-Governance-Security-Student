# Synthetic secret in Git history

- Scanner and version: Gitleaks v8.30.1 with `.gitleaks.toml`.
- Commit containing the synthetic token: `1bdd849`.
- Finding: rule `lab24-synthetic-token`, token `LAB24-DEMO` / `lab24-synthetic-token` in the historical seed commit; the current working tree is scanned separately.
- The token is intentionally synthetic and invalid. A real credential would require immediate revoke and rotate actions plus investigation; deleting a file from HEAD does not revoke a leaked credential.
- Dependency hashes and a pinned pre-commit hook reduce supply-chain drift and future leakage, but do not replace secret rotation.
