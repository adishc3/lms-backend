"""Add AI system prompt field to courses

Revision ID: 0011_add_course_ai_system_prompt
Revises: 0010_lesson_fields
Create Date: 2026-06-11 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0011_add_course_ai_system_prompt'
down_revision = '0010_lesson_fields'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'courses',
        sa.Column('ai_system_prompt', sa.Text(), nullable=True)
    )


def downgrade():
    op.drop_column('courses', 'ai_system_prompt')
