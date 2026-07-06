from sqlalchemy import ForeignKey, Index, SmallInteger, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base


class PaletteColorModel(Base):
    __tablename__ = "palette_colors"
    __table_args__ = (
        UniqueConstraint("palette_id", "position", name="palette_colors_palette_id_position_key"),
        Index("idx_palette_colors_palette_id", "palette_id"),
        Index("idx_palette_colors_hex_code", "hex_code"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    palette_id: Mapped[int] = mapped_column(
        ForeignKey("palettes.id", ondelete="CASCADE"), nullable=False
    )
    hex_code: Mapped[str] = mapped_column(
        String(7), ForeignKey("color_catalog.hex_code"), nullable=False
    )
    name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    position: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    palette: Mapped["PaletteModel"] = relationship(back_populates="colors", lazy="selectin")
