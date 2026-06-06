"""Add organization and progress fields to User

Revision ID: 0008_user_fields
Revises: 0007_add_cover_image
Create Date: 2026-06-06 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0008_user_fields'
down_revision = '0007_add_cover_image'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'users',
        sa.Column('organization_id', sa.Integer(), nullable=True)
    )
    op.add_column(
        'users',
        sa.Column('points', sa.Integer(), nullable=False, server_default=sa.text('0'))
    )
    op.add_column(
        'users',
        sa.Column('level', sa.Integer(), nullable=False, server_default=sa.text('1'))
    )
    op.create_foreign_key(
        'fk_users_organization_id',
        'users',
        'organizations',
        ['organization_id'],
        ['id'],
        ondelete='SET NULL'
    )


def downgrade():
    op.drop_constraint('fk_users_organization_id', 'users', type_='foreignkey')
    op.drop_column('users', 'level')
    op.drop_column('users', 'points')
    op.drop_column('users', 'organization_id')
