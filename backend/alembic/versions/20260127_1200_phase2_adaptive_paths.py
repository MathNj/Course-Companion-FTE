"""Phase 2: Add adaptive_paths table

Revision ID: 002_phase2_adaptive_paths
Revises: f951f945330e
Create Date: 2026-01-27

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_phase2_adaptive_paths'
down_revision = 'f951f945330e'
branch_labels = None
depends_on = None


def upgrade():
    # Create adaptive_paths table
    op.create_table(
        'adaptive_paths',
        sa.Column('path_id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('student_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('generated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), server_default=sa.text('now() + interval \'24 hours\''), nullable=False),
        sa.Column('recommendations_json', postgresql.JSONB(), nullable=False),
        sa.Column('reasoning', sa.Text(), nullable=False),
        sa.Column('tokens_input', sa.Integer(), nullable=False),
        sa.Column('tokens_output', sa.Integer(), nullable=False),
        sa.Column('cost_usd', sa.Numeric(precision=10, scale=6), nullable=False),
        sa.Column('status', sa.String(length=20), server_default=sa.text('\'active\''), nullable=False),
        sa.Column('followed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['student_id'], ['students.student_id'], name=op.f('fk_adaptive_paths_student_id'), ondelete='cascade'),
        sa.CheckConstraint("status IN ('active', 'expired', 'superseded')", name='adaptive_paths_status_check'),
        sa.CheckConstraint('expires_at > generated_at', name='valid_expiration')
    )

    # Create indexes
    op.create_index('idx_adaptive_paths_student_id', 'adaptive_paths', ['student_id'])
    op.create_index('idx_adaptive_paths_generated_at', 'adaptive_paths', [sa.text('generated_at DESC')])
    op.create_index('idx_adaptive_paths_status', 'adaptive_paths', ['status'])
    op.create_index('idx_adaptive_paths_expires_at', 'adaptive_paths', ['expires_at'])
    op.create_index('idx_adaptive_paths_student_active', 'adaptive_paths', ['student_id', 'status', 'expires_at'])


def downgrade():
    # Drop indexes
    op.drop_index('idx_adaptive_paths_student_active', table_name='adaptive_paths')
    op.drop_index('idx_adaptive_paths_expires_at', table_name='adaptive_paths')
    op.drop_index('idx_adaptive_paths_status', table_name='adaptive_paths')
    op.drop_index('idx_adaptive_paths_generated_at', table_name='adaptive_paths')
    op.drop_index('idx_adaptive_paths_student_id', table_name='adaptive_paths')

    # Drop table
    op.drop_table('adaptive_paths')
