from __future__ import annotations

from enum import IntEnum


class RegState(IntEnum):
    ASK_STUDENT_ID = 1
    CONFIRM_STUDENT_ID = 2
    ASK_ECLASS_PASSWORD = 3


class EclassState(IntEnum):
    ASK_PASSWORD = 10
