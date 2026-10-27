from typing import Annotated

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from idemptx import idempotent
from idemptx.backend import AsyncRedisBackend
from pydantic import UUID7
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.database import get_session
from app.dependicies import check_api_key_header
from app.settings import settings

idempotency_backend = AsyncRedisBackend(aioredis.from_url(settings.redis_url))

router = APIRouter(prefix="/payments", dependencies=[Depends(check_api_key_header)])


@router.post("")
@idempotent(storage_backend=idempotency_backend, key_ttl=86400)
async def create_payment(
    request: Request,
    payment_info: schemas.PaymentCreateRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> JSONResponse:

    payment = models.Payment(**payment_info.model_dump(exclude_unset=True))

    async with session.begin():
        session.add(payment)
        await session.flush()
        outbox_event = models.OutboxEvent(
            id=payment.public_id,
            aggregatetype="payments.new",
            aggregateid=str(payment.id),
            payload=schemas.PyamentDetailResponse.model_validate(payment).model_dump(mode="json"),
        )
        session.add(outbox_event)
        await session.flush()
        await session.delete(outbox_event)

    payment_created = schemas.PaymentCreatedResponse.model_validate(payment)

    return JSONResponse(content=payment_created.model_dump(mode="json"), status_code=status.HTTP_202_ACCEPTED)


@router.get("/{payment_id}")
async def get_payment_info(
    payment_id: UUID7, session: Annotated[AsyncSession, Depends(get_session)]
) -> schemas.PyamentDetailResponse:
    query = select(models.Payment).filter(models.Payment.public_id == payment_id)
    payment = (await session.scalars(query)).first()
    if payment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No data for payment with ID {payment_id}")

    response = schemas.PyamentDetailResponse.model_validate(payment)

    return response
