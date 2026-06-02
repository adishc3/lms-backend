"""Initial migration: create all current tables

Revision ID: 0001_initial
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    # Use SQLAlchemy metadata to create all tables defined in models
    from app.db.session import Base

    Base.metadata.create_all(bind=bind)


def downgrade():
    bind = op.get_bind()
    from app.db.session import Base

    Base.metadata.drop_all(bind=bind)
