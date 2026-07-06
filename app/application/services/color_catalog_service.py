from app.core.exceptions import NotFoundError
from app.domain.entities.color_catalog import ColorCatalog
from app.domain.repositories.color_catalog_repository import ColorCatalogRepository


class ColorCatalogService:
    """Read-only surface over the color catalog. usage_count is maintained
    exclusively by Postgres triggers; this service never mutates it."""

    def __init__(self, color_catalog_repository: ColorCatalogRepository) -> None:
        self._color_catalog_repository = color_catalog_repository

    async def get_color(self, hex_code: str) -> ColorCatalog:
        color = await self._color_catalog_repository.get_by_hex(hex_code)
        if color is None:
            raise NotFoundError(f"Color {hex_code} not found")
        return color

    async def browse_by_hue(self, min_hue: int, max_hue: int, limit: int = 50) -> list[ColorCatalog]:
        return await self._color_catalog_repository.list_by_hue_range(min_hue, max_hue, limit)

    async def most_used(self, limit: int = 20) -> list[ColorCatalog]:
        return await self._color_catalog_repository.list_most_used(limit)
