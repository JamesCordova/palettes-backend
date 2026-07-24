from dataclasses import replace

from app.domain.entities.palette_color import PaletteColor
from app.domain.repositories.palette_color_repository import PaletteColorRepository


class FakePaletteColorRepository(PaletteColorRepository):
    def __init__(self) -> None:
        self._colors: dict[int, PaletteColor] = {}
        self._next_id = 1

    async def get_by_id(self, palette_color_id: int) -> PaletteColor | None:
        return self._colors.get(palette_color_id)

    async def list_for_palette(self, palette_id: int) -> list[PaletteColor]:
        items = [c for c in self._colors.values() if c.palette_id == palette_id]
        return sorted(items, key=lambda c: c.position)

    async def add(self, palette_color: PaletteColor) -> PaletteColor:
        created = replace(palette_color, id=self._next_id)
        self._colors[created.id] = created
        self._next_id += 1
        return created

    async def update(self, palette_color: PaletteColor) -> PaletteColor:
        self._colors[palette_color.id] = palette_color
        return palette_color

    async def remove(self, palette_color_id: int) -> None:
        self._colors.pop(palette_color_id, None)

    async def reorder(
        self, palette_id: int, ordered_ids: list[int]
    ) -> list[PaletteColor]:
        for position, color_id in enumerate(ordered_ids, start=1):
            color = self._colors.get(color_id)
            if color is not None:
                color.position = position
        return await self.list_for_palette(palette_id)

    async def list_for_palettes_capped(
        self, palette_ids: list[int], colors_limit: int
    ) -> dict[int, list[PaletteColor]]:
        result: dict[int, list[PaletteColor]] = {}
        for palette_id in palette_ids:
            result[palette_id] = (await self.list_for_palette(palette_id))[
                :colors_limit
            ]
        return result

    async def count_by_palette(self, palette_ids: list[int]) -> dict[int, int]:
        return {
            palette_id: len(
                [c for c in self._colors.values() if c.palette_id == palette_id]
            )
            for palette_id in palette_ids
        }
