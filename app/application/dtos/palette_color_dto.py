from dataclasses import dataclass


@dataclass
class AddPaletteColorDTO:
    hex_code: str
    hue: int
    saturation: int
    lightness: int
    luminance: float
    name: str | None = None
    position: int | None = None


@dataclass
class UpdatePaletteColorDTO:
    hex_code: str
    name: str | None = None


@dataclass
class ReorderPaletteColorDTO:
    ordered_ids: list[int]
