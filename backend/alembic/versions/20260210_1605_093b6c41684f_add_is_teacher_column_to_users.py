"""add_is_teacher_column_to_users

Revision ID: 093b6c41684f
Revises: 004_phase2_usage_tracking
Create Date: 2026-02-10 16:05:46.397753+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '093b6c41684f'
down_revision: Union[str, None] = '004_phase2_usage_tracking'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add is_teacher column to users table
    op.add_column('users', sa.Column('is_teacher', sa.Boolean(), server_default='false', nullable=False))


def downgrade() -> None:
    # Remove is_teacher column from users table
    op.drop_column('users', 'is_teacher')
