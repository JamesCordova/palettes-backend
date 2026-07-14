from app.application.dtos.color_catalog_dto import UpdateColorNameDTO
from app.core.exceptions import NotFoundError
from app.domain.entities.color_catalog import ColorCatalog
from app.domain.repositories.color_catalog_repository import ColorCatalogRepository


class ColorCatalogService:
    """Read-only surface over the color catalog, aside from naming a color.
    usage_count is maintained exclusively by Postgres triggers; nothing here
    ever touches it."""

    def __init__(self, color_catalog_repository: ColorCatalogRepository) -> None:
        self._color_catalog_repository = color_catalog_repository

    async def get_color(self, hex_code: str) -> ColorCatalog:
        color = await self._color_catalog_repository.get_by_hex(hex_code)
        if color is None:
            raise NotFoundError(f"Color {hex_code} not found")
        return color

    async def rename_color(self, hex_code: str, dto: UpdateColorNameDTO) -> ColorCatalog:
        await self.get_color(hex_code)
        return await self._color_catalog_repository.update_name(hex_code, dto.name)

    async def browse_by_hue(
        self, min_hue: int, max_hue: int, limit: int = 50, offset: int = 0
    ) -> tuple[list[ColorCatalog], int]:
        return await self._color_catalog_repository.list_by_hue_range(
            min_hue, max_hue, limit, offset
        )

    async def most_used(
        self, limit: int = 20, offset: int = 0
    ) -> tuple[list[ColorCatalog], int]:
        return await self._color_catalog_repository.list_most_used(limit, offset)
