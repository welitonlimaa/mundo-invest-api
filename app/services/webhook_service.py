from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.pipefy_client import simulate_update_fields_values
from app.core.exceptions import NotFoundError, WebhookEventAlreadyProcessedError
from app.models.cliente import Cliente
from app.models.webhook_event import WebhookEvent
from app.schemas.webhook import WebhookPayload

PATRIMONIO_PRIORIDADE_ALTA = 200_000
PRIORIDADE_ALTA = "prioridade_alta"
PRIORIDADE_NORMAL = "prioridade_normal"
STATUS_PROCESSADO = "Processado"


def _calcular_prioridade(valor_patrimonio: float) -> str:
    if valor_patrimonio >= PATRIMONIO_PRIORIDADE_ALTA:
        return PRIORIDADE_ALTA
    return PRIORIDADE_NORMAL


async def process_webhook(payload: WebhookPayload, db: AsyncSession) -> dict:
    event_result = await db.execute(
        select(WebhookEvent).where(WebhookEvent.event_id == payload.event_id)
    )
    if event_result.scalar_one_or_none():
        raise WebhookEventAlreadyProcessedError(payload.event_id)

    cliente_result = await db.execute(
        select(Cliente).where(Cliente.email == payload.cliente_email)
    )
    cliente = cliente_result.scalar_one_or_none()

    if not cliente:
        raise NotFoundError(
            f"Cliente com e-mail '{payload.cliente_email}' não encontrado"
        )

    if cliente.pipefy_card_id != payload.card_id:
        raise NotFoundError(
            f"Card '{payload.card_id}' não encontrado para o cliente '{payload.cliente_email}'"
        )

    prioridade = _calcular_prioridade(float(cliente.valor_patrimonio))

    pipefy_response = simulate_update_fields_values(
        card_id=payload.card_id,
        status=STATUS_PROCESSADO,
        prioridade=prioridade,
    )

    now = datetime.now(timezone.utc)

    cliente.status = STATUS_PROCESSADO
    cliente.prioridade = prioridade
    cliente.updated_at = now

    webhook_event = WebhookEvent(
        event_id=payload.event_id,
        card_id=payload.card_id,
        cliente_email=payload.cliente_email,
        received_at=now,
        processed_at=now,
    )

    db.add(webhook_event)
    await db.flush()

    return pipefy_response
