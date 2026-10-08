"""create file processing table

Revision ID: 1215e69c91f9
Revises: 85c79ef1d7e1
Create Date: 2026-08-26 13:52:33.146880
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "1215e69c91f9"
down_revision: Union[str, Sequence[str], None] = "85c79ef1d7e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "file_processing",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "input_file_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "output_file_id",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "operation",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "options",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=30),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["input_file_id"],
            ["files.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["output_file_id"],
            ["files.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_file_processing_id",
        "file_processing",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_file_processing_id",
        table_name="file_processing",
    )

    op.drop_table("file_processing")
