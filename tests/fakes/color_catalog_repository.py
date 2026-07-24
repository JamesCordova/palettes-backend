from dataclasses import replace
from datetime import UTC, datetime

from app.domain.entities.color_catalog import ColorCatalog
from app.domain.repositories.color_catalog_repository import ColorCatalogRepository


class FakeColorCatalogRepository(ColorCatalogRepository):
    def __init__(self) -> None:
        self._colors: dict[str, ColorCatalog] = {}

    async def get_by_hex(self, hex_code: str) -> ColorCatalog | None:
        return self._colors.get(hex_code)

    async def upsert(self, color: ColorCatalog) -> ColorCatalog:
        # Mirrors the real repository's upsert: a hex that already exists
        # keeps its trigger-owned usage_count and its curated name — only a
        # brand-new hex gets the incoming row (with usage_count reset to 0,
        # same as the caller always sends).
        existing = self._colors.get(color.hex_code)
        if existing is not None:
            merged = replace(
                color,
                usage_count=existing.usage_count,
                name=existing.name,
                created_at=existing.created_at,
            )
            self._colors[color.hex_code] = merged
            return merged
        created = replace(color, created_at=datetime.now(UTC))
        self._colors[color.hex_code] = created
        return created

    async def update_name(self, hex_code: str, name: str | None) -> ColorCatalog:
        color = self._colors[hex_code]
        color.name = name
        return color

    async def list_by_hue_range(
        self, min_hue: int, max_hue: int, limit: int = 50, offset: int = 0
    ) -> tuple[list[ColorCatalog], int]:
        matching = [c for c in self._colors.values() if min_hue <= c.hue <= max_hue]
        return matching[offset : offset + limit], len(matching)

    async def list_most_used(
        self, limit: int = 20, offset: int = 0
    ) -> tuple[list[ColorCatalog], int]:
        ordered = sorted(
            self._colors.values(), key=lambda c: c.usage_count, reverse=True
        )
        return ordered[offset : offset + limit], len(ordered)
