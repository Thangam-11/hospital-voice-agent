"""add activity logs

Revision ID: 9b4e9726ebc2
Revises:
Create Date: 2026-08-17 10:57:35.432255
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9b4e9726ebc2"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create activity_logs table."""

    op.create_table(
        "activity_logs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("entity_type", sa.String(length=50), nullable=False),
        sa.Column("entity_id", sa.UUID(), nullable=True),
        sa.Column("patient_id", sa.UUID(), nullable=True),
        sa.Column("appointment_id", sa.UUID(), nullable=True),
        sa.Column("actor_type", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["appointment_id"],
            ["appointments.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["patient_id"],
            ["patients.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_activity_logs_appointment_id",
        "activity_logs",
        ["appointment_id"],
        unique=False,
    )

    op.create_index(
        "ix_activity_logs_created_at",
        "activity_logs",
        ["created_at"],
        unique=False,
    )

    op.create_index(
        "ix_activity_logs_entity_id",
        "activity_logs",
        ["entity_id"],
        unique=False,
    )

    op.create_index(
        "ix_activity_logs_entity_type",
        "activity_logs",
        ["entity_type"],
        unique=False,
    )

    op.create_index(
        "ix_activity_logs_event_type",
        "activity_logs",
        ["event_type"],
        unique=False,
    )

    op.create_index(
        "ix_activity_logs_patient_id",
        "activity_logs",
        ["patient_id"],
        unique=False,
    )


def downgrade() -> None:
    """Remove activity_logs table."""

    op.drop_index(
        "ix_activity_logs_appointment_id",
        table_name="activity_logs",
    )

    op.drop_index(
        "ix_activity_logs_created_at",
        table_name="activity_logs",
    )

    op.drop_index(
        "ix_activity_logs_entity_id",
        table_name="activity_logs",
    )

    op.drop_index(
        "ix_activity_logs_entity_type",
        table_name="activity_logs",
    )

    op.drop_index(
        "ix_activity_logs_event_type",
        table_name="activity_logs",
    )

    op.drop_index(
        "ix_activity_logs_patient_id",
        table_name="activity_logs",
    )

    op.drop_table("activity_logs")