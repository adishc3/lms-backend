"""add cover_image_url to courses

Revision ID: 0007_add_cover_image
Revises: 0006_add_lesson_asset_metadata
Create Date: 2026-06-04 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0007_add_cover_image'
down_revision = '0006_add_lesson_asset_metadata'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('courses', sa.Column('cover_image_url', sa.String(length=1024), nullable=True))


def downgrade():
    op.drop_column('courses', 'cover_image_url')
