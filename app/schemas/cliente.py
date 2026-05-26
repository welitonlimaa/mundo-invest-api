from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator


class ClienteCreate(BaseModel):
    cliente_nome: str
    cliente_email: EmailStr
    tipo_solicitacao: str
    valor_patrimonio: float

    @field_validator("cliente_nome", "tipo_solicitacao")
    @classmethod
    def must_not_be_blank(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("não pode ser vazio")
        return value.strip()

    @field_validator("valor_patrimonio")
    @classmethod
    def must_be_positive(cls, value: float) -> float:
        if value <= 0:
            raise ValueError("deve ser maior que zero")
        return value


class ClienteResponse(BaseModel):
    id: str
    nome: str
    email: str
    tipo_solicitacao: str
    valor_patrimonio: float
    status: str
    prioridade: str | None
    pipefy_card_id: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
