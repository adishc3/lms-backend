"""Add lesson fields (duration, is_mandatory, sequence)

Revision ID: 0010_lesson_fields
Revises: 0009_course_fields
Create Date: 2026-06-06 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0010_lesson_fields'
down_revision = '0009_course_fields'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'lessons',
        sa.Column('duration', sa.String(length=80), nullable=True)
    )
    op.add_column(
        'lessons',
        sa.Column('is_mandatory', sa.Boolean(), nullable=False, server_default=sa.text('true'))
    )
    op.add_column(
        'lessons',
        sa.Column('sequence', sa.Integer(), nullable=True)
    )


def downgrade():
    op.drop_column('lessons', 'sequence')
    op.drop_column('lessons', 'is_mandatory')
    op.drop_column('lessons', 'duration')
