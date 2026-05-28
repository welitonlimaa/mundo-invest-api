from app.clients.pipefy_client import (
    build_create_card_variables,
    build_update_fields_values_variables,
    simulate_create_card,
    simulate_update_fields_values,
)
from app.core.config import settings


def test_create_card_variables_structure():
    variables = build_create_card_variables(
        nome="João Silva",
        email="joao@example.com",
        tipo_solicitacao="Atualização cadastral",
        valor_patrimonio=250000,
    )

    assert "input" in variables
    inp = variables["input"]
    assert inp["pipe_id"] == settings.pipefy_pipe_id

    field_ids = [f["field_id"] for f in inp["fields_attributes"]]
    assert settings.pipefy_field_id_nome_cliente in field_ids
    assert settings.pipefy_field_id_email_cliente in field_ids
    assert settings.pipefy_field_id_tipo_solicitacao in field_ids
    assert settings.pipefy_field_id_valor_patrimonio in field_ids


def test_update_fields_values_variables_structure():
    variables = build_update_fields_values_variables(
        card_id="750893428",
        status="Processado",
        prioridade="prioridade_alta",
    )

    assert "input" in variables

    inp = variables["input"]

    assert inp["nodeId"] == "750893428"

    values = inp["values"]

    assert len(values) == 2

    status_field = next(
        v for v in values if v["fieldId"] == settings.pipefy_field_id_status
    )

    prioridade_field = next(
        v for v in values if v["fieldId"] == settings.pipefy_field_id_prioridade
    )

    assert status_field["value"] == "Processado"

    assert prioridade_field["value"] == "prioridade_alta"


def test_simulate_create_card_returns_pipefy_contract():
    result = simulate_create_card(
        nome="João Silva",
        email="joao@example.com",
        tipo_solicitacao="Atualização cadastral",
        valor_patrimonio=250000,
    )

    assert "data" in result
    assert "createCard" in result["data"]
    card = result["data"]["createCard"]["card"]
    assert "id" in card
    assert card["id"].isdigit()


def test_simulate_create_card_generates_numeric_id_in_range():
    ids = [
        simulate_create_card("A", "a@a.com", "tipo", 100)["data"]["createCard"]["card"][
            "id"
        ]
        for _ in range(10)
    ]
    assert all(i.isdigit() for i in ids)
    assert all(100_000_000 <= int(i) <= 999_999_999 for i in ids)
