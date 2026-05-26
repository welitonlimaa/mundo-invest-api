from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator


class WebhookPayload(BaseModel):
    event_id: str
    card_id: str
    cliente_email: EmailStr
    timestamp: datetime

    @field_validator("event_id", "card_id")
    @classmethod
    def must_not_be_blank(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("não pode ser vazio")
        return value.strip()
