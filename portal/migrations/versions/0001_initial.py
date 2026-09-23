"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-09-01 10:00:00
"""
import sqlalchemy as sa
from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

AUDITED_TABLES = ("users", "invoices")


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("display_name", sa.String(120), nullable=False, server_default=""),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(32), nullable=False, server_default="member"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("reset_password_token", sa.String(128)),
        sa.Column("reset_password_exp", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "invoices",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("owner_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("region", sa.String(32), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="open"),
        sa.Column("amount_cents", sa.Integer, nullable=False, server_default="0"),
        sa.Column("pdf_path", sa.String(255), nullable=False, server_default=""),
    )
    for table in AUDITED_TABLES:
        op.execute(sa.text(f"ALTER TABLE {table} ADD COLUMN created_at TIMESTAMPTZ NOT NULL DEFAULT now()"))


def downgrade():
    pass
