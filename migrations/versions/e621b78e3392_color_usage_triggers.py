"""color usage triggers

Revision ID: e621b78e3392
Revises: 11f848d3299f
Create Date: 2026-07-06 00:20:43.749177

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e621b78e3392'
down_revision: Union[str, Sequence[str], None] = '11f848d3299f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE OR REPLACE FUNCTION increment_color_usage() RETURNS TRIGGER AS $$
        BEGIN
          UPDATE color_catalog
          SET usage_count = usage_count + 1
          WHERE hex_code = NEW.hex_code;
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE OR REPLACE FUNCTION decrement_color_usage() RETURNS TRIGGER AS $$
        BEGIN
          UPDATE color_catalog
          SET usage_count = usage_count - 1
          WHERE hex_code = OLD.hex_code;
          RETURN OLD;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE OR REPLACE FUNCTION update_color_usage_on_change() RETURNS TRIGGER AS $$
        BEGIN
          IF OLD.hex_code IS DISTINCT FROM NEW.hex_code THEN
            UPDATE color_catalog SET usage_count = usage_count - 1 WHERE hex_code = OLD.hex_code;
            UPDATE color_catalog SET usage_count = usage_count + 1 WHERE hex_code = NEW.hex_code;
          END IF;
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE TRIGGER trg_increment_color_usage
        AFTER INSERT ON palette_colors
        FOR EACH ROW EXECUTE FUNCTION increment_color_usage();
    """)

    op.execute("""
        CREATE TRIGGER trg_decrement_color_usage
        AFTER DELETE ON palette_colors
        FOR EACH ROW EXECUTE FUNCTION decrement_color_usage();
    """)

    op.execute("""
        CREATE TRIGGER trg_update_color_usage
        AFTER UPDATE ON palette_colors
        FOR EACH ROW EXECUTE FUNCTION update_color_usage_on_change();
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TRIGGER IF EXISTS trg_update_color_usage ON palette_colors;")
    op.execute("DROP TRIGGER IF EXISTS trg_decrement_color_usage ON palette_colors;")
    op.execute("DROP TRIGGER IF EXISTS trg_increment_color_usage ON palette_colors;")
    op.execute("DROP FUNCTION IF EXISTS update_color_usage_on_change();")
    op.execute("DROP FUNCTION IF EXISTS decrement_color_usage();")
    op.execute("DROP FUNCTION IF EXISTS increment_color_usage();")
