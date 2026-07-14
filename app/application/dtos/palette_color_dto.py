from dataclasses import dataclass


@dataclass
class AddPaletteColorDTO:
    hex_code: str
    hue: int
    saturation: int
    lightness: int
    luminance: float
    position: int | None = None


@dataclass
class UpdatePaletteColorDTO:
    hex_code: str


@dataclass
class ReorderPaletteColorDTO:
    ordered_ids: list[int]
