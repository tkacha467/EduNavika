"""milestone_4_exam_topics_association

Revision ID: a1b2c3d4e5f6
Revises: f1e2d3c4b5a6
Create Date: 2026-10-15 16:45:00.000000

Adds exam_topics associative table mapping examinations directly to canonical topics,
enforcing subtopic-level syllabus boundaries (e.g. Carnot engine in JEE Advanced only).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'f1e2d3c4b5a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Exam-Topic Associative Mapping Table
    op.create_table(
        'exam_topics',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('exam_code', sa.String(length=32), sa.ForeignKey('examinations.code', ondelete='RESTRICT'), nullable=False),
        sa.Column('topic_id', sa.String(length=36), sa.ForeignKey('topics.id', ondelete='CASCADE'), nullable=False),
        sa.Column('curriculum_role', sa.String(length=32), nullable=False, server_default='CORE_MANDATORY'),
        sa.Column('inclusion_status', sa.String(length=32), nullable=False, server_default='ACTIVE'),
        sa.Column('verification_status', sa.String(length=32), nullable=False, server_default='VERIFIED_PRIMARY_SOURCE'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.UniqueConstraint('exam_code', 'topic_id', name='uq_exam_topics_link')
    )
    op.create_index('ix_exam_topics_exam_code', 'exam_topics', ['exam_code'])
    op.create_index('ix_exam_topics_topic_id', 'exam_topics', ['topic_id'])
    op.create_index('idx_exam_topics_lookup', 'exam_topics', ['exam_code', 'topic_id'])


def downgrade() -> None:
    op.drop_index('idx_exam_topics_lookup', table_name='exam_topics')
    op.drop_index('ix_exam_topics_topic_id', table_name='exam_topics')
    op.drop_index('ix_exam_topics_exam_code', table_name='exam_topics')
    op.drop_table('exam_topics')
