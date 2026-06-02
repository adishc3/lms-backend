"""Add email_verified_at to users

Revision ID: 0004_add_email_verified
Revises: 0003_add_certificates
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0004_add_email_verified"
down_revision = "0003_add_certificates"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "users" in inspector.get_table_names():
        # SQLite has limited ALTER support; use add_column if absent
        columns = [c.get("name") for c in inspector.get_columns("users")]
        if "email_verified_at" not in columns:
            op.add_column("users", sa.Column("email_verified_at", sa.DateTime(timezone=True), nullable=True))


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "users" in inspector.get_table_names():
        columns = [c.get("name") for c in inspector.get_columns("users")]
        if "email_verified_at" in columns:
            op.drop_column("users", "email_verified_at")
