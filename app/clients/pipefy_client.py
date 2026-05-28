import logging
import random

from app.core.config import settings

logger = logging.getLogger(__name__)

CREATE_CARD_MUTATION = """
mutation CreateCard($input: CreateCardInput!) {
  createCard(input: $input) {
    card {
      id
    }
  }
}
"""

UPDATE_FIELDS_VALUES_MUTATION = """
mutation UpdateFieldsValues($input: UpdateFieldsValuesInput!) {
  updateFieldsValues(input: $input) {
    success
  }
}
"""


def build_create_card_variables(
    nome: str,
    email: str,
    tipo_solicitacao: str,
    valor_patrimonio: float,
) -> dict:
    return {
        "input": {
            "pipe_id": settings.pipefy_pipe_id,
            "fields_attributes": [
                {
                    "field_id": settings.pipefy_field_id_nome_cliente,
                    "field_value": nome,
                },
                {
                    "field_id": settings.pipefy_field_id_email_cliente,
                    "field_value": email,
                },
                {
                    "field_id": settings.pipefy_field_id_tipo_solicitacao,
                    "field_value": tipo_solicitacao,
                },
                {
                    "field_id": settings.pipefy_field_id_valor_patrimonio,
                    "field_value": str(valor_patrimonio),
                },
            ],
        }
    }


def build_update_fields_values_variables(
    card_id: str,
    status: str,
    prioridade: str,
) -> dict:

    return {
        "input": {
            "nodeId": card_id,
            "values": [
                {
                    "fieldId": settings.pipefy_field_id_status,
                    "value": status,
                },
                {
                    "fieldId": settings.pipefy_field_id_prioridade,
                    "value": prioridade,
                },
            ],
        }
    }


def simulate_create_card(
    nome: str,
    email: str,
    tipo_solicitacao: str,
    valor_patrimonio: float,
) -> dict:
    variables = build_create_card_variables(
        nome,
        email,
        tipo_solicitacao,
        valor_patrimonio,
    )

    logger.info(
        "Pipefy GraphQL mutation",
        extra={
            "mutation": CREATE_CARD_MUTATION.strip(),
            "variables": variables,
        },
    )

    card_id = str(random.randint(100_000_000, 999_999_999))

    return {
        "data": {
            "createCard": {
                "card": {
                    "id": card_id,
                }
            }
        }
    }


def simulate_update_fields_values(
    card_id: str,
    status: str,
    prioridade: str,
) -> dict:
    variables = build_update_fields_values_variables(card_id, status, prioridade)

    logger.info(
        "Pipefy GraphQL mutation",
        extra={
            "mutation": UPDATE_FIELDS_VALUES_MUTATION.strip(),
            "variables": variables,
        },
    )

    return {
        "data": {
            "updateFieldsValues": {
                "success": True,
            }
        }
    }
