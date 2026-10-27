from faststream.rabbit import RabbitBroker, RabbitExchange, RabbitQueue

from app.enums import Exchanges, Queues
from app.settings import settings


async def bootstrap():
    # Retry queue
    retry_settings = {
        Queues.STAGE_1: 30000,  # 30 sec
        Queues.STAGE_2: 300000,  # 5 min
        Queues.STAGE_3: 600000,  # 10 min
    }
    retry_exchange = await broker.declare_exchange(RabbitExchange(name=Exchanges.RETRY))
    for name, ttl in retry_settings.items():
        queue = await broker.declare_queue(
            RabbitQueue(
                name=name,
                arguments={
                    "x-dead-letter-exchange": Exchanges.WORK,
                    "x-dead-letter-routing-key": Queues.WORK,
                    "x-message-ttl": ttl,
                },
            )
        )
        await queue.bind(retry_exchange, name)

    # Dead letter queue
    dlx = await broker.declare_exchange(RabbitExchange(name=Exchanges.DLX))
    dlq = await broker.declare_queue(
        RabbitQueue(
            name=Queues.DLQ,
            arguments={"x-max-length": 1000},
        )
    )
    await dlq.bind(dlx, dlq.name)


broker = RabbitBroker(url=settings.rabbitmq_url, virtualhost=settings.rabbitmq_vhost)


# Business logic queue
payment_exchange = RabbitExchange(name=Exchanges.WORK)

payment_queue = RabbitQueue(
    name=Queues.WORK,
    arguments={
        "x-dead-letter-exchange": Exchanges.DLX,
        "x-dead-letter-routing-key": Queues.DLQ,
    },
)
