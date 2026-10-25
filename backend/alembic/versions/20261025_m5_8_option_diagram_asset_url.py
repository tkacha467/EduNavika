"""milestone_5_8_option_diagram_asset_url

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-10-25 15:00:00.000000

Adds diagram_asset_url column to question_options table for first-class graphical option support (Milestone 5.8).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add diagram_asset_url to question_options (nullable for full backward compatibility)
    op.add_column(
        'question_options',
        sa.Column('diagram_asset_url', sa.String(length=512), nullable=True)
    )


def downgrade() -> None:
    # Drop diagram_asset_url from question_options
    op.drop_column('question_options', 'diagram_asset_url')
