"""add base_url to llm_configs

Revision ID: 9c3d43e4b821
Revises: 8b2932d2a753
Create Date: 2025-11-06 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9c3d43e4b821'
down_revision = '8b2932d2a753'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add base_url column to llm_configs table
    op.add_column('llm_configs', sa.Column('base_url', sa.String(length=500), nullable=True))


def downgrade() -> None:
    # Remove base_url column from llm_configs table
    op.drop_column('llm_configs', 'base_url')
