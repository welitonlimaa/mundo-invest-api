import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_cliente_success(client: AsyncClient, headers, valid_cliente_payload):
    response = await client.post("/clientes", json=valid_cliente_payload, headers=headers)

    assert response.status_code == 201
    body = response.json()
    assert "data" in body
    assert "createCard" in body["data"]
    card = body["data"]["createCard"]["card"]
    assert "id" in card
    assert card["id"].isdigit()


@pytest.mark.asyncio
async def test_create_cliente_persists_in_database(
    client: AsyncClient, headers, valid_cliente_payload, db_session
):
    await client.post("/clientes", json=valid_cliente_payload, headers=headers)

    from sqlalchemy import select
    from app.models.cliente import Cliente

    result = await db_session.execute(
        select(Cliente).where(Cliente.email == valid_cliente_payload["cliente_email"])
    )
    cliente = result.scalar_one_or_none()

    assert cliente is not None
    assert cliente.nome == valid_cliente_payload["cliente_nome"]
    assert cliente.status == "Aguardando Análise"
    assert cliente.pipefy_card_id is not None
    assert float(cliente.valor_patrimonio) == valid_cliente_payload["valor_patrimonio"]


@pytest.mark.asyncio
async def test_create_cliente_duplicate_email_returns_409(
    client: AsyncClient, headers, valid_cliente_payload
):
    await client.post("/clientes", json=valid_cliente_payload, headers=headers)
    response = await client.post("/clientes", json=valid_cliente_payload, headers=headers)

    assert response.status_code == 409
    body = response.json()
    assert body["detail"]["error"] == "conflict"
    assert valid_cliente_payload["cliente_email"] in body["detail"]["message"]


@pytest.mark.asyncio
async def test_create_cliente_invalid_email_returns_422(client: AsyncClient, headers):
    response = await client.post(
        "/clientes",
        json={
            "cliente_nome": "João Silva",
            "cliente_email": "email-invalido",
            "tipo_solicitacao": "Atualização cadastral",
            "valor_patrimonio": 250000,
        },
        headers=headers,
    )

    assert response.status_code == 422
    body = response.json()
    assert body["error"] == "validation_error"
    assert "cliente_email" in body["message"]


@pytest.mark.asyncio
async def test_create_cliente_missing_required_field_returns_422(client: AsyncClient, headers):
    response = await client.post(
        "/clientes",
        json={
            "cliente_nome": "João Silva",
            "cliente_email": "joao@example.com",
            "valor_patrimonio": 250000,
        },
        headers=headers,
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_cliente_without_api_key_returns_401(
    client: AsyncClient, valid_cliente_payload
):
    response = await client.post("/clientes", json=valid_cliente_payload)

    assert response.status_code == 401
    body = response.json()
    assert body["error"] == "unauthorized"


@pytest.mark.asyncio
async def test_create_cliente_invalid_patrimonio_returns_422(client: AsyncClient, headers):
    response = await client.post(
        "/clientes",
        json={
            "cliente_nome": "João Silva",
            "cliente_email": "joao@example.com",
            "tipo_solicitacao": "Cadastral",
            "valor_patrimonio": -1000,
        },
        headers=headers,
    )

    assert response.status_code == 422
