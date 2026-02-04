"""Phase 2: Add assessment_submissions and assessment_feedback tables

Revision ID: 003_phase2_assessments
Revises: 002_phase2_adaptive_paths
Create Date: 2026-01-27

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003_phase2_assessments'
down_revision = '002_phase2_adaptive_paths'
branch_labels = None
depends_on = None


def upgrade():
    # Create assessment_submissions table
    op.create_table(
        'assessment_submissions',
        sa.Column('submission_id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('student_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('question_id', sa.String(length=50), nullable=False),
        sa.Column('previous_submission_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('answer_text', sa.Text(), nullable=False),
        sa.Column('submitted_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('grading_status', sa.String(length=20), server_default=sa.text('\'pending\''), nullable=False),
        sa.Column('grading_started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('grading_completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('attempt_number', sa.Integer(), server_default=sa.text('1'), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['previous_submission_id'], ['assessment_submissions.submission_id'], name=op.f('fk_assessment_submissions_previous')),
        sa.ForeignKeyConstraint(['student_id'], ['users.id'], name=op.f('fk_assessment_submissions_student_id'), ondelete='cascade'),
        sa.CheckConstraint("grading_status IN ('pending', 'processing', 'completed', 'failed')", name='submissions_status_check'),
        sa.CheckConstraint('LENGTH(answer_text) BETWEEN 50 AND 5000', name='answer_length_check'),
        sa.CheckConstraint('attempt_number BETWEEN 1 AND 3', name='attempt_limit_check'),
        sa.CheckConstraint('grading_completed_at IS NULL OR grading_started_at IS NULL OR grading_completed_at >= grading_started_at', name='valid_grading_timeline')
    )

    # Create assessment_feedback table
    op.create_table(
        'assessment_feedback',
        sa.Column('feedback_id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('submission_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('human_reviewer_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('quality_score', sa.Numeric(precision=3, scale=1), nullable=False),
        sa.Column('strengths_json', postgresql.JSONB(), nullable=False),
        sa.Column('improvements_json', postgresql.JSONB(), nullable=False),
        sa.Column('detailed_feedback', sa.Text(), nullable=False),
        sa.Column('generated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('tokens_input', sa.Integer(), nullable=False),
        sa.Column('tokens_output', sa.Integer(), nullable=False),
        sa.Column('cost_usd', sa.Numeric(precision=10, scale=6), nullable=False),
        sa.Column('is_off_topic', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('human_reviewed', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('human_review_notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['human_reviewer_id'], ['users.id'], name=op.f('fk_assessment_feedback_reviewer')),
        sa.ForeignKeyConstraint(['submission_id'], ['assessment_submissions.submission_id'], name=op.f('fk_assessment_feedback_submission'), ondelete='cascade'),
        sa.CheckConstraint('quality_score BETWEEN 0 AND 10', name='score_range_check')
    )

    # Create indexes for assessment_submissions
    op.create_index('idx_submissions_student_id', 'assessment_submissions', ['student_id'])
    op.create_index('idx_submissions_question_id', 'assessment_submissions', ['question_id'])
    op.create_index('idx_submissions_status', 'assessment_submissions', ['grading_status'])
    op.create_index('idx_submissions_submitted_at', 'assessment_submissions', [sa.text('submitted_at DESC')])
    op.create_index('idx_submissions_student_question', 'assessment_submissions', ['student_id', 'question_id', sa.text('submitted_at DESC')])

    # Create indexes for assessment_feedback
    op.create_index('idx_feedback_submission_id', 'assessment_feedback', ['submission_id'], unique=True)
    op.create_index('idx_feedback_generated_at', 'assessment_feedback', [sa.text('generated_at DESC')])
    op.create_index('idx_feedback_score', 'assessment_feedback', ['quality_score'])
    op.create_index('idx_feedback_unreviewed', 'assessment_feedback', ['human_reviewed', 'generated_at'])


def downgrade():
    # Drop assessment_feedback indexes and table
    op.drop_index('idx_feedback_unreviewed', table_name='assessment_feedback')
    op.drop_index('idx_feedback_score', table_name='assessment_feedback')
    op.drop_index('idx_feedback_generated_at', table_name='assessment_feedback')
    op.drop_index('idx_feedback_submission_id', table_name='assessment_feedback')
    op.drop_table('assessment_feedback')

    # Drop assessment_submissions indexes and table
    op.drop_index('idx_submissions_student_question', table_name='assessment_submissions')
    op.drop_index('idx_submissions_submitted_at', table_name='assessment_submissions')
    op.drop_index('idx_submissions_status', table_name='assessment_submissions')
    op.drop_index('idx_submissions_question_id', table_name='assessment_submissions')
    op.drop_index('idx_submissions_student_id', table_name='assessment_submissions')
    op.drop_table('assessment_submissions')
