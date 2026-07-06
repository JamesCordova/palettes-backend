from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.color_catalog import ColorCatalog
from app.domain.repositories.color_catalog_repository import ColorCatalogRepository
from app.infrastructure.models.color_catalog_model import ColorCatalogModel


def _to_entity(model: ColorCatalogModel) -> ColorCatalog:
    return ColorCatalog(
        hex_code=model.hex_code,
        hue=model.hue,
        saturation=model.saturation,
        lightness=model.lightness,
        luminance=model.luminance,
        usage_count=model.usage_count,
        created_at=model.created_at,
    )


class SQLAlchemyColorCatalogRepository(ColorCatalogRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_hex(self, hex_code: str) -> ColorCatalog | None:
        model = await self._session.get(ColorCatalogModel, hex_code)
        return _to_entity(model) if model else None

    async def upsert(self, color: ColorCatalog) -> ColorCatalog:
        model = await self._session.get(ColorCatalogModel, color.hex_code)
        if model is not None:
            return _to_entity(model)
        model = ColorCatalogModel(
            hex_code=color.hex_code,
            hue=color.hue,
            saturation=color.saturation,
            lightness=color.lightness,
            luminance=color.luminance,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return _to_entity(model)

    async def list_by_hue_range(
        self, min_hue: int, max_hue: int, limit: int = 50
    ) -> list[ColorCatalog]:
        result = await self._session.execute(
            select(ColorCatalogModel)
            .where(ColorCatalogModel.hue >= min_hue, ColorCatalogModel.hue <= max_hue)
            .limit(limit)
        )
        return [_to_entity(model) for model in result.scalars().all()]

    async def list_most_used(self, limit: int = 20) -> list[ColorCatalog]:
        result = await self._session.execute(
            select(ColorCatalogModel).order_by(ColorCatalogModel.usage_count.desc()).limit(limit)
        )
        return [_to_entity(model) for model in result.scalars().all()]
