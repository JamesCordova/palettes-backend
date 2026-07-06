from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.application.dtos.palette_dto import PaletteListItem
from app.presentation.schemas.palette_color_schema import PaletteColorRead


class PaletteCreate(BaseModel):
    name: str
    description: str | None = None
    is_public: bool = True


class PaletteUpdate(BaseModel):
    name: str
    description: str | None = None
    is_public: bool = True


class ForkPaletteRequest(BaseModel):
    name: str | None = None


class PaletteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    name: str
    description: str | None
    is_public: bool
    forked_from: int | None
    created_at: datetime | None
    updated_at: datetime | None


class PaletteWithColorsRead(PaletteRead):
    colors: list[PaletteColorRead] = []


class PaletteListItemRead(PaletteRead):
    colors: list[PaletteColorRead] = []
    color_count: int

    @classmethod
    def from_item(cls, item: PaletteListItem) -> "PaletteListItemRead":
        return cls(
            **PaletteRead.model_validate(item.palette).model_dump(),
            colors=[PaletteColorRead.model_validate(c) for c in item.colors],
            color_count=item.color_count,
        )
