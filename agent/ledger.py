"""Append-only JSONL ledger with a tamper-evident SHA-256 hash chain."""
from __future__ import annotations

from pathlib import Path
import hashlib
import json


def _digest(record: dict) -> str:
    payload = json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def append(entry: dict, path: Path) -> dict:
    required = ("ts", "agent_id", "run_id", "tool", "args_hash", "classification", "decision", "reason")
    if any(key not in entry for key in required):
        raise ValueError("ledger entry missing required field")
    path.parent.mkdir(parents=True, exist_ok=True)
    previous = "0" * 64
    if path.exists() and path.stat().st_size:
        previous = json.loads(path.read_text(encoding="utf-8").splitlines()[-1])["hash"]
    record = dict(entry, prev_hash=previous)
    record["hash"] = _digest(record)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    return record


def verify(path: Path) -> bool:
    if not path.exists():
        return False
    previous = "0" * 64
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            record = json.loads(line)
            if not record.get("reason") or record.get("prev_hash") != previous:
                return False
            saved = record.pop("hash", None)
            if saved != _digest(record):
                return False
            previous = saved
    except (OSError, ValueError, KeyError, json.JSONDecodeError):
        return False
    return True
