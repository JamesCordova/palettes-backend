"""move color name from palette_colors to color_catalog

Revision ID: b7d4e29a1f63
Revises: e621b78e3392
Create Date: 2026-07-12 00:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7d4e29a1f63'
down_revision: Union[str, Sequence[str], None] = 'e621b78e3392'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('color_catalog', sa.Column('name', sa.String(length=50), nullable=True))

    # Backfill: a color may have been named differently across several
    # palettes that used it. Pick one non-null name per hex_code (oldest row
    # wins) rather than losing the data outright.
    op.execute("""
        UPDATE color_catalog cc
        SET name = pc.name
        FROM (
            SELECT DISTINCT ON (hex_code) hex_code, name
            FROM palette_colors
            WHERE name IS NOT NULL
            ORDER BY hex_code, id
        ) pc
        WHERE cc.hex_code = pc.hex_code AND cc.name IS NULL;
    """)

    op.drop_column('palette_colors', 'name')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('palette_colors', sa.Column('name', sa.String(length=50), nullable=True))
    op.drop_column('color_catalog', 'name')
