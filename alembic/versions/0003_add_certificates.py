"""Add certificates table

Revision ID: 0003_add_certificates
Revises: 0002_add_lesson_completions
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0003_add_certificates"
down_revision = "0002_add_lesson_completions"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "certificates" not in inspector.get_table_names():
        op.create_table(
            "certificates",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("course_id", sa.Integer(), sa.ForeignKey("courses.id"), nullable=False),
            sa.Column("issued_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("certificate_id", sa.String(length=64), nullable=False, unique=True),
        )


def downgrade():
    op.drop_table("certificates")
