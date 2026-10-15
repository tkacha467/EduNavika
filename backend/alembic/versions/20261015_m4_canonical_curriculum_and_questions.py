"""milestone_4_canonical_curriculum_and_questions

Revision ID: f1e2d3c4b5a6
Revises: e025394444f5
Create Date: 2026-10-15 13:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1e2d3c4b5a6'
down_revision: Union[str, None] = 'e025394444f5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Examinations Master Table
    op.create_table(
        'examinations',
        sa.Column('code', sa.String(length=32), primary_key=True),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('conducting_body', sa.String(length=128), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )

    # 2. Exam-Subject Associative Mapping (Zero-Duplication Core)
    op.create_table(
        'exam_subjects',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('exam_code', sa.String(length=32), sa.ForeignKey('examinations.code', ondelete='RESTRICT'), nullable=False),
        sa.Column('subject_id', sa.String(length=36), sa.ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('curriculum_role', sa.String(length=32), nullable=False, server_default='CORE'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.UniqueConstraint('exam_code', 'subject_id', name='uq_exam_subjects_link'),
    )
    op.create_index('idx_exam_subjects_lookup', 'exam_subjects', ['exam_code', 'subject_id'])

    # 3. Official Exam Papers / Sessions Table (Robust NULL-safe identifier)
    op.create_table(
        'exam_papers',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('paper_identifier', sa.String(length=128), unique=True, nullable=False),
        sa.Column('exam_code', sa.String(length=32), sa.ForeignKey('examinations.code', ondelete='RESTRICT'), nullable=False),
        sa.Column('exam_year', sa.Integer(), nullable=False),
        sa.Column('session_or_shift', sa.String(length=64), nullable=False),
        sa.Column('paper_code', sa.String(length=32), nullable=True),
        sa.Column('exam_date', sa.Date(), nullable=True),
        sa.Column('total_questions', sa.Integer(), nullable=False),
        sa.Column('source_pdf_path', sa.String(length=512), nullable=True),
        sa.Column('source_pdf_hash', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )
    op.create_index('idx_exam_papers_exam_year', 'exam_papers', ['exam_code', 'exam_year'])

    # 4. Canonical Competitive Questions Table
    op.create_table(
        'questions',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('exam_paper_id', sa.String(length=36), sa.ForeignKey('exam_papers.id', ondelete='SET NULL'), nullable=True),
        sa.Column('paper_question_number', sa.Integer(), nullable=True),
        
        # Authoritative Curriculum Anchor
        sa.Column('topic_id', sa.String(length=36), sa.ForeignKey('topics.id', ondelete='RESTRICT'), nullable=False),
        
        # Question Classification
        sa.Column('question_type', sa.String(length=32), nullable=False),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('diagram_asset_url', sa.String(length=512), nullable=True),
        
        # Scoring, Answer Key & Missing-Data Tolerance
        sa.Column('correct_answer_raw', sa.String(length=256), nullable=True),
        sa.Column('answer_verification_status', sa.String(length=32), nullable=False, server_default='UNVERIFIED'),
        sa.Column('solution_text', sa.Text(), nullable=True),
        sa.Column('ncert_citation', sa.String(length=256), nullable=True),
        
        # Numerical Evaluation Policies & Tolerance Bounds
        sa.Column('evaluation_policy', sa.String(length=64), nullable=False, server_default='UNRESOLVED_POLICY'),
        sa.Column('numerical_precision_type', sa.String(length=32), nullable=False, server_default='NOT_APPLICABLE'),
        sa.Column('numerical_min_val', sa.Float(), nullable=True),
        sa.Column('numerical_max_val', sa.Float(), nullable=True),
        sa.Column('numerical_tolerance_epsilon', sa.Float(), nullable=True),
        sa.Column('scoring_policy_version', sa.String(length=32), nullable=True),
        sa.Column('scoring_policy_source', sa.String(length=256), nullable=True),
        
        # Pedagogical Attributes
        sa.Column('difficulty_tier', sa.String(length=16), nullable=False, server_default='MEDIUM'),
        sa.Column('cognitive_level', sa.String(length=24), nullable=False, server_default='APPLYING'),
        sa.Column('estimated_seconds', sa.Integer(), nullable=False, server_default='120'),
        
        # Provenance, Rights & Publish Permissions (Unreviewed by default)
        sa.Column('source_type', sa.String(length=32), nullable=False, server_default='OFFICIAL_PYQ'),
        sa.Column('rights_status', sa.String(length=32), nullable=False, server_default='PENDING_LEGAL_REVIEW'),
        sa.Column('publish_permission', sa.String(length=32), nullable=False, server_default='FORBIDDEN'),
        sa.Column('rights_review_notes', sa.Text(), nullable=True),
        
        # Official Status & Quarantine Disciplinary Fields
        sa.Column('official_status', sa.String(length=32), nullable=False, server_default='REGULAR'),
        sa.Column('official_status_evidence', sa.Text(), nullable=True),
        sa.Column('quarantine_status', sa.String(length=32), nullable=False, server_default='CLEAN'),
        sa.Column('quarantine_reason', sa.Text(), nullable=True),
        sa.Column('eligibility_for_scoring', sa.String(length=32), nullable=False, server_default='INELIGIBLE_UNVERIFIED_KEY'),
        sa.Column('verification_status', sa.String(length=32), nullable=False, server_default='INGESTED'),
        
        # Deduplication Hash
        sa.Column('content_hash', sa.String(length=64), unique=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )
    op.create_index('idx_questions_topic_diff', 'questions', ['topic_id', 'difficulty_tier', 'verification_status'])
    op.create_index('idx_questions_scoring', 'questions', ['eligibility_for_scoring'])
    op.create_index('idx_questions_paper_qnum', 'questions', ['exam_paper_id', 'paper_question_number'])

    # 5. Question Options Table
    op.create_table(
        'question_options',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('question_id', sa.String(length=36), sa.ForeignKey('questions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('option_key', sa.String(length=8), nullable=False),
        sa.Column('option_text', sa.Text(), nullable=False),
        sa.Column('is_correct', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.UniqueConstraint('question_id', 'option_key', name='uq_question_option_key'),
    )
    op.create_index('idx_question_options_qid', 'question_options', ['question_id'])

    # 6. Question Verification & Audit Logs
    op.create_table(
        'question_verification_logs',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('question_id', sa.String(length=36), sa.ForeignKey('questions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('verified_by', sa.String(length=128), nullable=False),
        sa.Column('previous_status', sa.String(length=32), nullable=False),
        sa.Column('new_status', sa.String(length=32), nullable=False),
        sa.Column('action_type', sa.String(length=32), nullable=False),
        sa.Column('review_notes', sa.Text(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )
    op.create_index('idx_qvl_question_id', 'question_verification_logs', ['question_id'])


def downgrade() -> None:
    # Drops the 6 new tables in reverse dependency order without touching legacy tables
    op.drop_table('question_verification_logs')
    op.drop_table('question_options')
    op.drop_table('questions')
    op.drop_table('exam_papers')
    op.drop_table('exam_subjects')
    op.drop_table('examinations')
