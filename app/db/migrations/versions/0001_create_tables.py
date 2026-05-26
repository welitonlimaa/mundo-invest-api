from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "clientes",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("nome", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("tipo_solicitacao", sa.String(255), nullable=False),
        sa.Column("valor_patrimonio", sa.Numeric(15, 2), nullable=False),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("prioridade", sa.String(50), nullable=True),
        sa.Column("pipefy_card_id", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_clientes_email", "clientes", ["email"], unique=True)

    op.create_table(
        "webhook_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("event_id", sa.String(255), nullable=False),
        sa.Column("card_id", sa.String(50), nullable=False),
        sa.Column("cliente_email", sa.String(255), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_webhook_events_event_id", "webhook_events", ["event_id"], unique=True
    )
    op.create_index(
        "ix_webhook_events_cliente_email", "webhook_events", ["cliente_email"]
    )


def downgrade() -> None:
    op.drop_index("ix_webhook_events_cliente_email", table_name="webhook_events")
    op.drop_index("ix_webhook_events_event_id", table_name="webhook_events")
    op.drop_table("webhook_events")
    op.drop_index("ix_clientes_email", table_name="clientes")
    op.drop_table("clientes")
