from dataclasses import dataclass


@dataclass
class PaletteColor:
    id: int | None
    palette_id: int
    hex_code: str
    position: int
    # Not this row's own data — derived from the linked color_catalog entry's
    # name (colors are named once, globally, not per palette-use). Always
    # populated by the repository from the joined catalog row, never written
    # back to palette_colors itself.
    name: str | None = None
