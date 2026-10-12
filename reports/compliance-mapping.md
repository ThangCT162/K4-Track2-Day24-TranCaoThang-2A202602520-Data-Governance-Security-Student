# Compliance mapping

| Source / requirement | Implemented control | Evidence | Limitation |
|---|---|---|---|
| Luật 91/2025/QH15 | PII minimization, redaction and access decisions | `agent/pii.py`, `agent/policy.py`, `reports/ledger.jsonl` | Specific article not asserted without authoritative text verification |
| NĐ 356/2025/NĐ-CP | Purpose/scope/expiry checks and audit trail | `agent/policy.py`, `agent/ledger.py`, `tests/test_obo.py` | Mock principal is not production authentication |
| Luật AI 134/2025/QH15 | Prompt-injection containment and human-auditable decisions | `agent/runner.py`, `injection-corpus.md`, `reports/attack-after.log` | Legal applicability and article mapping require source verification |
| OWASP ASI01, ASI03, ASI04 | Untrusted instruction containment, least privilege and egress denial | `agent/runner.py`, `agent/policy.py`, `reports/ledger.jsonl`, `tests/` | Local mock does not provide immutable production logging |

This table maps technical evidence to control themes; it is not a legal conclusion.
