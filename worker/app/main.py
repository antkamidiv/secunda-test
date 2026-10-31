import asyncio

from faststream import AckPolicy, FastStream
from faststream.exceptions import RejectMessage

from app.broker import bootstrap, broker, payment_exchange, payment_queue
from app.cache import cache
from app.database import pool
from app.entities import Payment, PaymentError
from app.enums import Exchanges, Queues
from app.schemas import PaymentModel
from app.webhook import session_manager

app = FastStream(broker)


@app.on_startup
async def on_startup_app():
    cache.create()
    await pool.create()


@app.after_startup
async def after_startup_app():
    await bootstrap()


@app.on_shutdown
async def on_shutdown_app():
    await asyncio.gather(pool.close(), cache.close(), session_manager.close(), return_exceptions=True)


@broker.subscriber(exchange=payment_exchange, queue=payment_queue, ack_policy=AckPolicy.NACK_ON_ERROR)
async def handle_payment(payment_info: PaymentModel):
    payment = Payment(**payment_info.model_dump(exclude={"retry_queue"}))

    try:
        # Deduplication
        if not await payment.allowed():
            return
        # Processing
        await payment.process()
    except PaymentError:
        #  Dead letter queue
        if payment_info.exhausted:
            await payment.set_failed()
            raise RejectMessage()
        await retry(payment_info)  # Go to retry payment
    else:
        await payment.post_process()


async def retry(payment_info: PaymentModel):
    match payment_info.retry_queue:
        case None:
            retry = Queues.STAGE_1
        case Queues.STAGE_1:
            retry = Queues.STAGE_2
        case Queues.STAGE_2:
            retry = Queues.STAGE_3
        case _:
            return

    requeued_payment = payment_info.model_copy(update={"retry_queue": retry})

    await broker.publish(
        message=requeued_payment.model_dump(mode="json"),
        exchange=Exchanges.RETRY,
        routing_key=retry,
    )
