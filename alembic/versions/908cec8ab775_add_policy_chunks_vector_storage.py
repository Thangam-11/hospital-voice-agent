"""add policy chunks vector storage

Revision ID: 908cec8ab775
Revises: aaab4128296f
Create Date: 2026-08-25 10:43:06.511216
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = "908cec8ab775"
down_revision: Union[str, Sequence[str], None] = "aaab4128296f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create policy_chunks table."""

    op.create_table(
        "policy_chunks",

        sa.Column(
            "id",
            sa.UUID(),
            nullable=False,
        ),

        sa.Column(
            "content",
            sa.Text(),
            nullable=False,
        ),

        sa.Column(
            "embedding",
            Vector(768),
            nullable=False,
        ),

        sa.Column(
            "source",
            sa.String(length=255),
            nullable=False,
        ),

        sa.Column(
            "document_type",
            sa.String(length=100),
            nullable=False,
        ),

        sa.Column(
            "section",
            sa.String(length=255),
            nullable=True,
        ),

        sa.Column(
            "chunk_id",
            sa.String(length=255),
            nullable=False,
        ),

        sa.Column(
            "chunk_number",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "metadata",
            postgresql.JSONB(),
            nullable=False,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),

        sa.PrimaryKeyConstraint("id"),

        sa.UniqueConstraint("chunk_id"),
    )


def downgrade() -> None:
    """Drop policy_chunks table."""

    op.drop_table("policy_chunks")