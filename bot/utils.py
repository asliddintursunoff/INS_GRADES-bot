from __future__ import annotations

import re
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional, Tuple

STUDENT_ID_RE = re.compile(r"^[Uu]\d{7}$")


def normalize_student_id(s: str) -> str:
    s = s.strip()
    if not s:
        return s
    return s[0].upper() + s[1:]


def is_valid_student_id(s: str) -> bool:
    return bool(STUDENT_ID_RE.match(s.strip()))


def parse_due_dt(due_str: str, tz_name: str) -> Optional[datetime]:
    try:
        tz = ZoneInfo(tz_name)
        # due_date format: "YYYY-MM-DD HH:MM"
        dt = datetime.strptime(due_str.strip(), "%Y-%m-%d %H:%M")
        return dt.replace(tzinfo=tz)
    except Exception:
        return None


def format_time_left(now: datetime, due: datetime) -> str:
    delta = due - now
    total = int(delta.total_seconds())
    if total <= 0:
        return "overdue"

    days = total // 86400
    rem = total % 86400
    hours = rem // 3600
    rem = rem % 3600
    mins = rem // 60

    parts = []
    if days:
        parts.append(f"{days}d")
    if hours or days:
        parts.append(f"{hours}h")
    parts.append(f"{mins}m")
    return " ".join(parts)


def safe_str(x) -> str:
    return "" if x is None else str(x)
