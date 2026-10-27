from enum import StrEnum


class Currency(StrEnum):
    RUB = "rub"
    USD = "usd"
    EUR = "eur"


class State(StrEnum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
