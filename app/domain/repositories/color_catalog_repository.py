from abc import ABC, abstractmethod

from app.domain.entities.color_catalog import ColorCatalog


class ColorCatalogRepository(ABC):
    """usage_count is exclusively maintained by Postgres triggers (see migration
    0002_color_usage_triggers). No method here writes or increments it directly."""

    @abstractmethod
    async def get_by_hex(self, hex_code: str) -> ColorCatalog | None: ...

    @abstractmethod
    async def upsert(self, color: ColorCatalog) -> ColorCatalog: ...

    @abstractmethod
    async def list_by_hue_range(
        self, min_hue: int, max_hue: int, limit: int = 50
    ) -> list[ColorCatalog]: ...

    @abstractmethod
    async def list_most_used(self, limit: int = 20) -> list[ColorCatalog]: ...
