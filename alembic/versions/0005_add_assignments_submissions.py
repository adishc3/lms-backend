"""Add assignments and submissions tables

Revision ID: 0005_add_assignments_submissions
Revises: 0004_add_email_verified
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0005_add_assignments_submissions"
down_revision = "0004_add_email_verified"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "assignments" not in inspector.get_table_names():
        op.create_table(
            "assignments",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("course_id", sa.Integer(), sa.ForeignKey("courses.id"), nullable=False),
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("max_score", sa.Integer(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        )
    if "submissions" not in inspector.get_table_names():
        op.create_table(
            "submissions",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("assignment_id", sa.Integer(), sa.ForeignKey("assignments.id"), nullable=False),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("content", sa.Text(), nullable=True),
            sa.Column("submitted_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("grade", sa.Integer(), nullable=True),
            sa.Column("feedback", sa.Text(), nullable=True),
            sa.Column("graded_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("graded_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        )


def downgrade():
    op.drop_table("submissions")
    op.drop_table("assignments")
