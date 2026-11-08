"""add persistent authentication records

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
"""
from alembic import op
import sqlalchemy as sa

revision = "c3d4e5f6a7b8"
down_revision = "b2c3d4e5f6a7"
branch_labels = None
depends_on = None

def upgrade():
    for name, columns in (("auth_sessions", [sa.Column("id", sa.String(36), primary_key=True), sa.Column("token_digest", sa.String(64), nullable=False), sa.Column("family_id", sa.String(36), nullable=False), sa.Column("parent_session_id", sa.String(36), sa.ForeignKey("auth_sessions.id", ondelete="SET NULL")), sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False), sa.Column("revoked_at", sa.DateTime(timezone=True)), sa.Column("replaced_at", sa.DateTime(timezone=True)), sa.Column("reuse_detected_at", sa.DateTime(timezone=True)), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False)]), ("password_reset_tokens", [sa.Column("id", sa.String(36), primary_key=True), sa.Column("token_digest", sa.String(64), nullable=False), sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False), sa.Column("consumed_at", sa.DateTime(timezone=True)), sa.Column("revoked_at", sa.DateTime(timezone=True)), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False)]), ("auth_rate_limits", [sa.Column("id", sa.String(36), primary_key=True), sa.Column("scope", sa.String(32), nullable=False), sa.Column("key", sa.String(255), nullable=False), sa.Column("window_started_at", sa.DateTime(timezone=True), nullable=False), sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False), sa.Column("attempts", sa.Integer(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False)])):
        op.create_table(name, *columns)
    op.create_index("ix_auth_sessions_family_active", "auth_sessions", ["family_id", "revoked_at"])
    op.create_unique_constraint("uq_auth_sessions_digest", "auth_sessions", ["token_digest"])
    op.create_unique_constraint("uq_password_reset_tokens_digest", "password_reset_tokens", ["token_digest"])
    op.create_unique_constraint("uq_auth_rate_limit_window", "auth_rate_limits", ["scope", "key", "window_started_at"])

def downgrade():
    op.drop_table("auth_rate_limits")
    op.drop_table("password_reset_tokens")
    op.drop_table("auth_sessions")
