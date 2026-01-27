"""Phase 2: Add llm_usage_logs and premium_usage_quotas tables

Revision ID: 004_phase2_usage_tracking
Revises: 003_phase2_assessments
Create Date: 2026-01-27

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004_phase2_usage_tracking'
down_revision = '003_phase2_assessments'
branch_labels = None
depends_on = None


def upgrade():
    # Create llm_usage_logs table
    op.create_table(
        'llm_usage_logs',
        sa.Column('log_id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('student_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('feature', sa.String(length=50), nullable=False),
        sa.Column('reference_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('request_timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('model_version', sa.String(length=100), server_default=sa.text('\'claude-sonnet-4-5-20250929\''), nullable=False),
        sa.Column('tokens_input', sa.Integer(), nullable=False),
        sa.Column('tokens_output', sa.Integer(), nullable=False),
        sa.Column('tokens_total', sa.Integer(), server_default=sa.text('tokens_input + tokens_output'), nullable=False),
        sa.Column('cost_usd', sa.Numeric(precision=10, scale=6), nullable=False),
        sa.Column('latency_ms', sa.Integer(), nullable=False),
        sa.Column('success', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('error_code', sa.String(length=50), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['student_id'], ['students.student_id'], name=op.f('fk_llm_usage_logs_student_id'), ondelete='cascade'),
        sa.CheckConstraint("feature IN ('adaptive-path', 'assessment')", name='feature_check'),
        sa.CheckConstraint('tokens_input > 0', name='valid_input_tokens'),
        sa.CheckConstraint('tokens_output > 0', name='valid_output_tokens'),
        sa.CheckConstraint('cost_usd > 0', name='valid_cost'),
        sa.CheckConstraint('latency_ms >= 0', name='valid_latency'),
        sa.CheckConstraint('(success = TRUE AND error_code IS NULL) OR (success = FALSE AND error_code IS NOT NULL)', name='valid_error_state')
    )

    # Create premium_usage_quotas table
    op.create_table(
        'premium_usage_quotas',
        sa.Column('quota_id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('student_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('month', sa.Date(), nullable=False),
        sa.Column('reset_date', sa.Date(), nullable=False),
        sa.Column('adaptive_paths_used', sa.Integer(), server_default=sa.text('0'), nullable=False),
        sa.Column('adaptive_paths_limit', sa.Integer(), server_default=sa.text('10'), nullable=False),
        sa.Column('assessments_used', sa.Integer(), server_default=sa.text('0'), nullable=False),
        sa.Column('assessments_limit', sa.Integer(), server_default=sa.text('20'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['student_id'], ['students.student_id'], name=op.f('fk_premium_usage_quotas_student_id'), ondelete='cascade'),
        sa.CheckConstraint('month = DATE_TRUNC(\'month\', month)::DATE', name='valid_month'),
        sa.CheckConstraint('reset_date = (month + INTERVAL \'1 month\')::DATE', name='valid_reset_date'),
        sa.CheckConstraint('adaptive_paths_used >= 0', name='valid_adaptive_used'),
        sa.CheckConstraint('adaptive_paths_limit > 0', name='valid_adaptive_limit'),
        sa.CheckConstraint('assessments_used >= 0', name='valid_assessments_used'),
        sa.CheckConstraint('assessments_limit > 0', name='valid_assessments_limit'),
        sa.UniqueConstraint('student_id', 'month', name='unique_student_month')
    )

    # Create indexes for llm_usage_logs
    op.create_index('idx_llm_logs_student_id', 'llm_usage_logs', ['student_id'])
    op.create_index('idx_llm_logs_feature', 'llm_usage_logs', ['feature'])
    op.create_index('idx_llm_logs_timestamp', 'llm_usage_logs', [sa.text('request_timestamp DESC')])
    op.create_index('idx_llm_logs_success', 'llm_usage_logs', ['success'])

    # Create partial index for active logs (not soft-deleted)
    op.execute('CREATE INDEX idx_llm_logs_active ON llm_usage_logs (request_timestamp) WHERE deleted_at IS NULL')

    # Create composite indexes for analytics
    op.execute('CREATE INDEX idx_llm_logs_student_month ON llm_usage_logs (student_id, DATE_TRUNC(\'month\', request_timestamp))')
    op.execute('CREATE INDEX idx_llm_logs_feature_month ON llm_usage_logs (feature, DATE_TRUNC(\'month\', request_timestamp))')

    # Create indexes for premium_usage_quotas
    op.create_index('idx_quotas_student_id', 'premium_usage_quotas', ['student_id'])
    op.create_index('idx_quotas_month', 'premium_usage_quotas', ['month'])
    op.create_index('idx_quotas_reset_date', 'premium_usage_quotas', ['reset_date'])
    op.create_index('idx_quotas_student_month', 'premium_usage_quotas', ['student_id', 'month'])


def downgrade():
    # Drop premium_usage_quotas indexes and table
    op.drop_index('idx_quotas_student_month', table_name='premium_usage_quotas')
    op.drop_index('idx_quotas_reset_date', table_name='premium_usage_quotas')
    op.drop_index('idx_quotas_month', table_name='premium_usage_quotas')
    op.drop_index('idx_quotas_student_id', table_name='premium_usage_quotas')
    op.drop_table('premium_usage_quotas')

    # Drop llm_usage_logs indexes and table
    op.execute('DROP INDEX IF EXISTS idx_llm_logs_feature_month')
    op.execute('DROP INDEX IF EXISTS idx_llm_logs_student_month')
    op.execute('DROP INDEX IF EXISTS idx_llm_logs_active')
    op.drop_index('idx_llm_logs_success', table_name='llm_usage_logs')
    op.drop_index('idx_llm_logs_timestamp', table_name='llm_usage_logs')
    op.drop_index('idx_llm_logs_feature', table_name='llm_usage_logs')
    op.drop_index('idx_llm_logs_student_id', table_name='llm_usage_logs')
    op.drop_table('llm_usage_logs')
