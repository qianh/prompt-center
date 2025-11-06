"""change version_number to string

Revision ID: a1b2c3d4e5f6
Revises: 9c3d43e4b821
Create Date: 2025-11-06 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '9c3d43e4b821'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Change version_number from Integer to String(50)
    # SQLite doesn't support ALTER COLUMN, so we need to:
    # 1. Create new column
    # 2. Copy data
    # 3. Drop old column
    # 4. Rename new column

    # Add new column
    op.add_column('prompt_versions', sa.Column('version_number_new', sa.String(50), nullable=True))

    # Copy data from old column to new column, converting int to string with ".0" format
    op.execute("""
        UPDATE prompt_versions
        SET version_number_new = CAST(version_number AS TEXT) || '.0'
    """)

    # Make the new column non-nullable
    op.alter_column('prompt_versions', 'version_number_new', nullable=False)

    # Drop the old column (this also drops the unique constraint)
    op.drop_constraint('unique_prompt_version', 'prompt_versions', type_='unique')
    op.drop_column('prompt_versions', 'version_number')

    # Rename new column to version_number
    op.alter_column('prompt_versions', 'version_number_new', new_column_name='version_number')

    # Re-create the unique constraint
    op.create_unique_constraint('unique_prompt_version', 'prompt_versions', ['prompt_id', 'version_number'])


def downgrade() -> None:
    # Reverse the migration
    # Add integer column
    op.add_column('prompt_versions', sa.Column('version_number_new', sa.Integer(), nullable=True))

    # Copy data, converting string to integer (strip ".0" if present)
    op.execute("""
        UPDATE prompt_versions
        SET version_number_new = CAST(REPLACE(version_number, '.0', '') AS INTEGER)
    """)

    # Make the new column non-nullable
    op.alter_column('prompt_versions', 'version_number_new', nullable=False)

    # Drop the old column
    op.drop_constraint('unique_prompt_version', 'prompt_versions', type_='unique')
    op.drop_column('prompt_versions', 'version_number')

    # Rename new column to version_number
    op.alter_column('prompt_versions', 'version_number_new', new_column_name='version_number')

    # Re-create the unique constraint
    op.create_unique_constraint('unique_prompt_version', 'prompt_versions', ['prompt_id', 'version_number'])
