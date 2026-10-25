"""add preferred_language to student_profiles

Revision ID: ccbefc4090d1
Revises: a1b2c3d4e5f6
Create Date: 2026-10-25 15:26:53.603899

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ccbefc4090d1'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'student_profiles',
        sa.Column('preferred_language', sa.String(length=5), nullable=False, server_default='en')
    )


def downgrade() -> None:
    op.drop_column('student_profiles', 'preferred_language')
