from dataclasses import dataclass

from app.domain.entities.palette import Palette
from app.domain.entities.palette_color import PaletteColor


@dataclass
class PaletteListItem:
    palette: Palette
    colors: list[PaletteColor]
    color_count: int


@dataclass
class CreatePaletteDTO:
    name: str
    description: str | None = None
    is_public: bool = True


@dataclass
class UpdatePaletteDTO:
    name: str
    description: str | None = None
    is_public: bool = True


@dataclass
class ForkPaletteDTO:
    name: str | None = None
