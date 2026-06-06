"""Add course fields (duration, category, track, pricing, prerequisite)

Revision ID: 0009_course_fields
Revises: 0008_user_fields
Create Date: 2026-06-06 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0009_course_fields'
down_revision = '0008_user_fields'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'courses',
        sa.Column('duration', sa.String(length=80), nullable=True)
    )
    op.add_column(
        'courses',
        sa.Column('category', sa.String(length=100), nullable=True)
    )
    op.add_column(
        'courses',
        sa.Column('track', sa.String(length=120), nullable=True)
    )
    op.add_column(
        'courses',
        sa.Column('price', sa.Integer(), nullable=False, server_default=sa.text('0'))
    )
    op.add_column(
        'courses',
        sa.Column('is_paid', sa.Boolean(), nullable=False, server_default=sa.text('false'))
    )
    op.add_column(
        'courses',
        sa.Column('prerequisite_course_id', sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        'fk_courses_prerequisite_course_id',
        'courses',
        'courses',
        ['prerequisite_course_id'],
        ['id'],
        ondelete='SET NULL'
    )


def downgrade():
    op.drop_constraint('fk_courses_prerequisite_course_id', 'courses', type_='foreignkey')
    op.drop_column('courses', 'prerequisite_course_id')
    op.drop_column('courses', 'is_paid')
    op.drop_column('courses', 'price')
    op.drop_column('courses', 'track')
    op.drop_column('courses', 'category')
    op.drop_column('courses', 'duration')
