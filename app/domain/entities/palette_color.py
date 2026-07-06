from dataclasses import dataclass


@dataclass
class PaletteColor:
    id: int | None
    palette_id: int
    hex_code: str
    name: str | None
    position: int
