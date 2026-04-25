from enum import StrEnum


class TaskStatusName(StrEnum):
    ASSIGNED = "ASSIGNED"
    COMPLETED = "COMPLETED"
    SKIPPED = "SKIPPED"


class TaskTypeName(StrEnum):
    CARDS_DELIVERY = "CARDS_DELIVERY"
