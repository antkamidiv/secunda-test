from enum import StrEnum


class Currency(StrEnum):
    RUB = "rub"
    USD = "usd"
    EUR = "eur"


class State(StrEnum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class Queues(StrEnum):
    WORK = "payments.new"
    STAGE_1 = "retry.stage_1"
    STAGE_2 = "retry.stage_2"
    STAGE_3 = "retry.stage_3"
    DLQ = "dlq"


class Exchanges(StrEnum):
    WORK = "payments"
    RETRY = "retry"
    DLX = "dlx"
