from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.pipefy_client import simulate_create_card
from app.core.exceptions import ClienteAlreadyExistsError
from app.models.cliente import Cliente
from app.schemas.cliente import ClienteCreate


async def create_cliente(payload: ClienteCreate, db: AsyncSession) -> tuple[Cliente, dict]:
    result = await db.execute(select(Cliente).where(Cliente.email == payload.cliente_email))
    existing = result.scalar_one_or_none()

    if existing:
        raise ClienteAlreadyExistsError(payload.cliente_email)

    pipefy_response = simulate_create_card(
        nome=payload.cliente_nome,
        email=payload.cliente_email,
        tipo_solicitacao=payload.tipo_solicitacao,
        valor_patrimonio=payload.valor_patrimonio,
    )

    card_id = pipefy_response["data"]["createCard"]["card"]["id"]
    now = datetime.now(timezone.utc)

    cliente = Cliente(
        nome=payload.cliente_nome,
        email=payload.cliente_email,
        tipo_solicitacao=payload.tipo_solicitacao,
        valor_patrimonio=payload.valor_patrimonio,
        status="Aguardando Análise",
        pipefy_card_id=card_id,
        created_at=now,
        updated_at=now,
    )

    db.add(cliente)
    await db.flush()

    return cliente, pipefy_response
