from datetime import datetime

from sqlalchemy import DateTime, Index, Numeric, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base


class ColorCatalogModel(Base):
    __tablename__ = "color_catalog"
    __table_args__ = (
        Index("idx_color_catalog_hue", "hue"),
        Index("idx_color_catalog_lightness", "lightness"),
        Index("idx_color_catalog_usage_count", "usage_count"),
    )

    hex_code: Mapped[str] = mapped_column(String(7), primary_key=True)
    hue: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    saturation: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    lightness: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    luminance: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    # Maintained exclusively by Postgres triggers (migration 0002). Never
    # written or updated by application/repository code.
    usage_count: Mapped[int] = mapped_column(server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
