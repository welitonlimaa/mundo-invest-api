from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    env: str = "local"
    database_url: str

    pipefy_pipe_id: str
    pipefy_field_id_nome_cliente: str
    pipefy_field_id_email_cliente: str
    pipefy_field_id_tipo_solicitacao: str
    pipefy_field_id_valor_patrimonio: str
    pipefy_field_id_status: str
    pipefy_field_id_prioridade: str

    api_key: str


settings = Settings()
