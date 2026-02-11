"""add_completed_sections_to_chapter_progress

Revision ID: b3e7bc65b356
Revises: 093b6c41684f
Create Date: 2026-02-10 16:17:26.030503+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'b3e7bc65b356'
down_revision: Union[str, None] = '093b6c41684f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add completed_sections column to chapter_progress table
    # Using JSONB type for PostgreSQL
    op.add_column(
        'chapter_progress',
        sa.Column(
            'completed_sections',
            postgresql.JSONB,
            nullable=False,
            server_default='{}'
        )
    )


def downgrade() -> None:
    # Remove completed_sections column
    op.drop_column('chapter_progress', 'completed_sections')
