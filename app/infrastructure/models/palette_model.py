from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base

if TYPE_CHECKING:
    from app.infrastructure.models.palette_color_model import PaletteColorModel
    from app.infrastructure.models.user_model import UserModel


class PaletteModel(Base):
    __tablename__ = "palettes"
    __table_args__ = (
        Index("idx_palettes_user_id", "user_id"),
        Index("idx_palettes_is_public", "is_public"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, server_default="true")
    forked_from: Mapped[int | None] = mapped_column(
        ForeignKey("palettes.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    owner: Mapped["UserModel"] = relationship(back_populates="palettes", lazy="selectin")
    colors: Mapped[list["PaletteColorModel"]] = relationship(
        back_populates="palette",
        cascade="all, delete-orphan",
        order_by="PaletteColorModel.position",
        lazy="selectin",
    )
