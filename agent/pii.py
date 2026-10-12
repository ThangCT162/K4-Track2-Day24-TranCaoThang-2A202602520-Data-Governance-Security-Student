"""PII detection and redaction for the synthetic Vietnamese test set."""
from __future__ import annotations

import re

_PATTERNS = (
    ("EMAIL", re.compile(r"(?<![\w.+-])[A-Za-z0-9][A-Za-z0-9._%+-]*@[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?![\w.-])")),
    ("VN_CCCD", re.compile(r"(?<!\d)\d{12}(?!\d)")),
    ("VN_PHONE", re.compile(r"(?<!\d)(?:\+?84|0)(?:[ .-]?\d){8,10}(?!\d)")),
    ("VN_BANK_ACCOUNT", re.compile(r"(?i)(?:(?:stk|số tài khoản|so tai khoan)\s*[:#-]?\s*)\d{8,16}|(?<!\d)\d{8,16}(?!\d)")),
)


def detect(text: str) -> list[dict]:
    found = []
    for entity_type, pattern in _PATTERNS:
        for match in pattern.finditer(text):
            if entity_type == "VN_BANK_ACCOUNT":
                digits = re.search(r"\d{8,16}$", match.group(0))
                start = match.end() - len(digits.group(0)) if digits else match.start()
                found.append({"type": entity_type, "start": start, "end": match.end()})
            else:
                found.append({"type": entity_type, "start": match.start(), "end": match.end()})
    found.sort(key=lambda item: (item["start"], -(item["end"] - item["start"])))
    result, last_end = [], -1
    for entity in found:
        if entity["start"] >= last_end:
            result.append(entity)
            last_end = entity["end"]
    return result


def redact(text: str) -> str:
    for entity in sorted(detect(text), key=lambda item: item["start"], reverse=True):
        text = text[:entity["start"]] + f"[REDACTED_{entity['type']}]" + text[entity["end"]:]
    return text
