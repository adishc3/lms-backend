"""Add lesson_completions table

Revision ID: 0002_add_lesson_completions
Revises: 0001_initial
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0002_add_lesson_completions"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "lesson_completions" not in inspector.get_table_names():
        op.create_table(
            "lesson_completions",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("lesson_id", sa.Integer(), sa.ForeignKey("lessons.id"), nullable=False),
            sa.Column("completed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("time_spent_minutes", sa.Integer(), nullable=True),
        )


def downgrade():
    op.drop_table("lesson_completions")
