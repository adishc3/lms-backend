"""Add asset_metadata column to lessons table for Cloudinary file info.

Revision ID: 0006_add_lesson_asset_metadata
Revises: 0005_add_assignments_submissions
Create Date: 2026-05-29 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0006_add_lesson_asset_metadata"
down_revision = "0005_add_assignments_submissions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add asset_metadata column to lessons table
    op.add_column('lessons', sa.Column('asset_metadata', sa.JSON(), nullable=True))


def downgrade() -> None:
    # Remove asset_metadata column from lessons table
    op.drop_column('lessons', 'asset_metadata')
