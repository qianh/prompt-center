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
    # For SQLite, we need to use batch operations to recreate the table

    with op.batch_alter_table('prompt_versions', schema=None) as batch_op:
        # Add new column
        batch_op.add_column(sa.Column('version_number_new', sa.String(50), nullable=True))

    # Copy data from old column to new column, converting int to string with ".0" format
    op.execute("""
        UPDATE prompt_versions
        SET version_number_new = CAST(version_number AS TEXT) || '.0'
        WHERE version_number IS NOT NULL
    """)

    with op.batch_alter_table('prompt_versions', schema=None) as batch_op:
        # Drop the unique constraint and old column
        batch_op.drop_constraint('unique_prompt_version', type_='unique')
        batch_op.drop_column('version_number')
        # Add the new column as version_number
        batch_op.alter_column('version_number_new', new_column_name='version_number', nullable=False)
        # Re-create the unique constraint
        batch_op.create_unique_constraint('unique_prompt_version', ['prompt_id', 'version_number'])


def downgrade() -> None:
    # Reverse the migration using batch operations for SQLite compatibility

    with op.batch_alter_table('prompt_versions', schema=None) as batch_op:
        # Add integer column
        batch_op.add_column(sa.Column('version_number_new', sa.Integer(), nullable=True))

    # Copy data, converting string to integer (strip ".0" if present)
    op.execute("""
        UPDATE prompt_versions
        SET version_number_new = CAST(REPLACE(version_number, '.0', '') AS INTEGER)
        WHERE version_number IS NOT NULL
    """)

    with op.batch_alter_table('prompt_versions', schema=None) as batch_op:
        # Drop the unique constraint and old column
        batch_op.drop_constraint('unique_prompt_version', type_='unique')
        batch_op.drop_column('version_number')
        # Rename new column to version_number
        batch_op.alter_column('version_number_new', new_column_name='version_number', nullable=False)
        # Re-create the unique constraint
        batch_op.create_unique_constraint('unique_prompt_version', ['prompt_id', 'version_number'])
