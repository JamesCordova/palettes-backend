from abc import ABC, abstractmethod

from app.domain.entities.palette_color import PaletteColor


class PaletteColorRepository(ABC):
    @abstractmethod
    async def list_for_palette(self, palette_id: int) -> list[PaletteColor]: ...

    @abstractmethod
    async def add(self, palette_color: PaletteColor) -> PaletteColor: ...

    @abstractmethod
    async def update(self, palette_color: PaletteColor) -> PaletteColor: ...

    @abstractmethod
    async def remove(self, palette_color_id: int) -> None: ...

    @abstractmethod
    async def reorder(
        self, palette_id: int, ordered_ids: list[int]
    ) -> list[PaletteColor]: ...

    @abstractmethod
    async def list_for_palettes_capped(
        self, palette_ids: list[int], colors_limit: int
    ) -> dict[int, list[PaletteColor]]: ...

    @abstractmethod
    async def count_by_palette(self, palette_ids: list[int]) -> dict[int, int]: ...
