import pytest
from httpx import AsyncClient


async def _create_cliente(client, headers, payload):
    response = await client.post("/clientes", json=payload, headers=headers)
    assert response.status_code == 201
    return response.json()


def _build_webhook_payload(card_id: str, email: str, event_id: str = "evt_123") -> dict:
    return {
        "event_id": event_id,
        "card_id": card_id,
        "cliente_email": email,
        "timestamp": "2026-05-18T12:00:00Z",
    }


@pytest.mark.asyncio
async def test_webhook_prioridade_alta_patrimonio_igual_limite(
    client: AsyncClient, headers, valid_cliente_payload
):
    valid_cliente_payload["valor_patrimonio"] = 200000
    create_response = await _create_cliente(client, headers, valid_cliente_payload)
    card_id = create_response["data"]["createCard"]["card"]["id"]

    webhook_payload = _build_webhook_payload(
        card_id, valid_cliente_payload["cliente_email"]
    )
    response = await client.post(
        "/webhooks/pipefy/card-updated", json=webhook_payload, headers=headers
    )

    assert response.status_code == 200
    fields = response.json()["data"]["updateFieldsValues"]["card"]["fields"]
    prioridades = [f["value"] for f in fields if f["name"] == "Prioridade"]
    assert prioridades[0] == "prioridade_alta"


@pytest.mark.asyncio
async def test_webhook_prioridade_alta_patrimonio_acima_limite(
    client: AsyncClient, headers, valid_cliente_payload
):
    valid_cliente_payload["valor_patrimonio"] = 500000
    create_response = await _create_cliente(client, headers, valid_cliente_payload)
    card_id = create_response["data"]["createCard"]["card"]["id"]

    webhook_payload = _build_webhook_payload(
        card_id, valid_cliente_payload["cliente_email"]
    )
    response = await client.post(
        "/webhooks/pipefy/card-updated", json=webhook_payload, headers=headers
    )

    assert response.status_code == 200
    fields = response.json()["data"]["updateFieldsValues"]["card"]["fields"]
    prioridades = [f["value"] for f in fields if f["name"] == "Prioridade"]
    assert prioridades[0] == "prioridade_alta"


@pytest.mark.asyncio
async def test_webhook_prioridade_normal_patrimonio_abaixo_limite(
    client: AsyncClient, headers, valid_cliente_payload
):
    valid_cliente_payload["valor_patrimonio"] = 199999
    create_response = await _create_cliente(client, headers, valid_cliente_payload)
    card_id = create_response["data"]["createCard"]["card"]["id"]

    webhook_payload = _build_webhook_payload(
        card_id, valid_cliente_payload["cliente_email"]
    )
    response = await client.post(
        "/webhooks/pipefy/card-updated", json=webhook_payload, headers=headers
    )

    assert response.status_code == 200
    fields = response.json()["data"]["updateFieldsValues"]["card"]["fields"]
    prioridades = [f["value"] for f in fields if f["name"] == "Prioridade"]
    assert prioridades[0] == "prioridade_normal"


@pytest.mark.asyncio
async def test_webhook_atualiza_status_para_processado(
    client: AsyncClient, headers, valid_cliente_payload, db_session
):
    create_response = await _create_cliente(client, headers, valid_cliente_payload)
    card_id = create_response["data"]["createCard"]["card"]["id"]

    webhook_payload = _build_webhook_payload(
        card_id, valid_cliente_payload["cliente_email"]
    )
    await client.post(
        "/webhooks/pipefy/card-updated", json=webhook_payload, headers=headers
    )

    from sqlalchemy import select
    from app.models.cliente import Cliente

    result = await db_session.execute(
        select(Cliente).where(Cliente.email == valid_cliente_payload["cliente_email"])
    )
    cliente = result.scalar_one_or_none()

    assert cliente.status == "Processado"
    assert cliente.prioridade is not None


@pytest.mark.asyncio
async def test_webhook_event_id_duplicado_retorna_409(
    client: AsyncClient, headers, valid_cliente_payload
):
    create_response = await _create_cliente(client, headers, valid_cliente_payload)
    card_id = create_response["data"]["createCard"]["card"]["id"]

    webhook_payload = _build_webhook_payload(
        card_id, valid_cliente_payload["cliente_email"]
    )
    await client.post(
        "/webhooks/pipefy/card-updated", json=webhook_payload, headers=headers
    )
    response = await client.post(
        "/webhooks/pipefy/card-updated", json=webhook_payload, headers=headers
    )

    assert response.status_code == 409
    body = response.json()
    assert body["detail"]["error"] == "conflict"
    assert webhook_payload["event_id"] in body["detail"]["message"]


@pytest.mark.asyncio
async def test_webhook_cliente_nao_encontrado_retorna_404(client: AsyncClient, headers):
    webhook_payload = _build_webhook_payload(
        "card_inexistente", "naoexiste@example.com"
    )
    response = await client.post(
        "/webhooks/pipefy/card-updated", json=webhook_payload, headers=headers
    )

    assert response.status_code == 404
    body = response.json()
    assert body["detail"]["error"] == "not_found"
    assert "naoexiste@example.com" in body["detail"]["message"]


@pytest.mark.asyncio
async def test_webhook_card_id_invalido_retorna_404(
    client: AsyncClient, headers, valid_cliente_payload
):
    await _create_cliente(client, headers, valid_cliente_payload)

    webhook_payload = _build_webhook_payload(
        "card_inexistente", valid_cliente_payload["cliente_email"]
    )
    response = await client.post(
        "/webhooks/pipefy/card-updated", json=webhook_payload, headers=headers
    )

    assert response.status_code == 404
    body = response.json()
    assert body["detail"]["error"] == "not_found"
    assert "card_inexistente" in body["detail"]["message"]


@pytest.mark.asyncio
async def test_webhook_sem_api_key_retorna_401(client: AsyncClient):
    webhook_payload = _build_webhook_payload("card_qualquer", "email@example.com")
    response = await client.post("/webhooks/pipefy/card-updated", json=webhook_payload)

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_webhook_persiste_evento_no_banco(
    client: AsyncClient, headers, valid_cliente_payload, db_session
):
    create_response = await _create_cliente(client, headers, valid_cliente_payload)
    card_id = create_response["data"]["createCard"]["card"]["id"]

    webhook_payload = _build_webhook_payload(
        card_id, valid_cliente_payload["cliente_email"]
    )
    await client.post(
        "/webhooks/pipefy/card-updated", json=webhook_payload, headers=headers
    )

    from sqlalchemy import select
    from app.models.webhook_event import WebhookEvent

    result = await db_session.execute(
        select(WebhookEvent).where(WebhookEvent.event_id == webhook_payload["event_id"])
    )
    event = result.scalar_one_or_none()

    assert event is not None
    assert event.card_id == card_id
    assert event.cliente_email == valid_cliente_payload["cliente_email"]
