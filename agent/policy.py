"""Policy enforcement point for tool calls and delegated principals."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path

_PRINCIPALS = json.loads((Path(__file__).resolve().parent.parent / "data" / "principals.json").read_text(encoding="utf-8"))


@dataclass(frozen=True)
class PolicyContext:
    data_classification: str
    request_purpose: str
    agent_owner: str
    delegation_depth: int
    egress_enabled: bool
    principal_id: str = ""
    requested_tool: str = ""
    agent_scopes: tuple[str, ...] = ()
    parent_scopes: tuple[str, ...] = ()
    expires_at: str = ""


def check(context: PolicyContext) -> tuple[bool, str]:
    if context.data_classification == "restricted" and context.egress_enabled:
        return False, "restricted data cannot use egress"
    principal = _PRINCIPALS.get(context.principal_id)
    if principal is None:
        return False, "unknown principal"
    if not context.requested_tool:
        return False, "requested tool is missing"
    effective = set(principal.get("allowed_tools", ())) & set(context.agent_scopes)
    if context.delegation_depth > 0:
        effective &= set(context.parent_scopes)
    if context.requested_tool not in effective:
        return False, "tool is outside effective delegated scope"
    if context.request_purpose not in principal.get("purposes", ()):
        return False, "purpose is not authorized for principal"
    if not context.expires_at:
        return False, "authorization expiry is missing"
    try:
        expires = datetime.fromisoformat(context.expires_at.replace("Z", "+00:00"))
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if expires <= datetime.now(timezone.utc):
            return False, "authorization has expired"
    except ValueError:
        return False, "invalid authorization expiry"
    return True, "principal, scope, purpose and expiry authorized"
