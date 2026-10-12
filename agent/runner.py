"""Contained two-run agent: untrusted search is separated from private lookup."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
import uuid

from agent import ledger, policy, tools

REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"
DEFAULT_LEDGER_PATH = REPORTS_DIR / "ledger.jsonl"


class RunnerScaffoldPending(NotImplementedError):
    """Compatibility name retained for the pre-implementation scaffold."""


def _hash_args(value: object) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def handle(message: str, llm, log_dir: Path | None = None,
           principal_id: str = "support_l1") -> str:
    log_dir = Path(log_dir) if log_dir is not None else REPORTS_DIR
    ledger_path = log_dir / "ledger.jsonl"
    run_id = str(uuid.uuid4())
    agent_id = "lab24-agent"
    expires_at = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    scopes = ("search_docs", "read_customer", "http_post")
    purpose = "support-reply"

    def call(tool_name, classification, args, operation, *, egress=False, depth=0, parents=()):
        context = policy.PolicyContext(
            data_classification=classification,
            request_purpose=purpose,
            agent_owner=f"{agent_id}/{run_id}",
            delegation_depth=depth,
            egress_enabled=egress,
            principal_id=principal_id,
            requested_tool=tool_name,
            agent_scopes=scopes,
            parent_scopes=parents,
            expires_at=expires_at,
        )
        allowed, reason = policy.check(context)
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "agent_id": agent_id,
            "run_id": run_id,
            "tool": tool_name,
            "args_hash": _hash_args(args),
            "classification": classification,
            "decision": "allow" if allowed else "deny",
            "reason": reason,
            "on_behalf_of": principal_id,
            "expires_at": expires_at,
        }
        ledger.append(entry, ledger_path)
        if not allowed:
            return None
        return operation()

    docs = call("search_docs", "internal", {"query": message}, lambda: tools.search_docs(message)) or []
    combined = "\n\n".join(doc["text"] for doc in docs)
    injected = llm.find_injection(combined)

    # Typed boundary: only numeric ticket IDs from trusted filenames cross into Run B.
    ticket_ids = []
    for doc in docs:
        match = re.fullmatch(r"ticket-(\d+)\.md", doc.get("id", ""))
        if match:
            ticket_ids.append(int(match.group(1)))
    customers = json.loads((Path(__file__).resolve().parent.parent / "data" / "customers.json").read_text(encoding="utf-8"))
    customer_by_ticket = {
        ticket: customer["customer_id"]
        for customer in customers
        for ticket in customer.get("related_tickets", [])
    }
    records = []
    seen = set()
    for ticket_id in ticket_ids:
        customer_id = customer_by_ticket.get(ticket_id)
        if not customer_id or customer_id in seen:
            continue
        seen.add(customer_id)
        record = call("read_customer", "restricted", {"ticket_id": ticket_id}, lambda cid=customer_id: tools.read_customer(cid))
        if record is not None:
            records.append(record)

    if injected is not None:
        target = injected.target_url
        call(
            "http_post", "restricted", {"url": target, "record_count": len(records)},
            lambda: tools.http_post(target, {"records": records}), egress=True,
        )
    return llm.summarize(docs)
