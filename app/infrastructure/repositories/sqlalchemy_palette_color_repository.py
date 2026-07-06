from collections import defaultdict

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.core.exceptions import NotFoundError
from app.domain.entities.palette_color import PaletteColor
from app.domain.repositories.palette_color_repository import PaletteColorRepository
from app.infrastructure.models.palette_color_model import PaletteColorModel


def _to_entity(model: PaletteColorModel) -> PaletteColor:
    return PaletteColor(
        id=model.id,
        palette_id=model.palette_id,
        hex_code=model.hex_code,
        name=model.name,
        position=model.position,
    )


class SQLAlchemyPaletteColorRepository(PaletteColorRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_for_palette(self, palette_id: int) -> list[PaletteColor]:
        result = await self._session.execute(
            select(PaletteColorModel)
            .where(PaletteColorModel.palette_id == palette_id)
            .order_by(PaletteColorModel.position)
        )
        return [_to_entity(model) for model in result.scalars().all()]

    async def add(self, palette_color: PaletteColor) -> PaletteColor:
        model = PaletteColorModel(
            palette_id=palette_color.palette_id,
            hex_code=palette_color.hex_code,
            name=palette_color.name,
            position=palette_color.position,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return _to_entity(model)

    async def update(self, palette_color: PaletteColor) -> PaletteColor:
        model = await self._session.get(PaletteColorModel, palette_color.id)
        if model is None:
            raise NotFoundError(f"PaletteColor {palette_color.id} not found")
        model.hex_code = palette_color.hex_code
        model.name = palette_color.name
        model.position = palette_color.position
        await self._session.flush()
        await self._session.refresh(model)
        return _to_entity(model)

    async def remove(self, palette_color_id: int) -> None:
        model = await self._session.get(PaletteColorModel, palette_color_id)
        if model is None:
            raise NotFoundError(f"PaletteColor {palette_color_id} not found")
        await self._session.delete(model)
        await self._session.flush()

    async def reorder(self, palette_id: int, ordered_ids: list[int]) -> list[PaletteColor]:
        result = await self._session.execute(
            select(PaletteColorModel).where(PaletteColorModel.palette_id == palette_id)
        )
        models = {model.id: model for model in result.scalars().all()}
        for position, palette_color_id in enumerate(ordered_ids, start=1):
            model = models.get(palette_color_id)
            if model is None:
                raise NotFoundError(f"PaletteColor {palette_color_id} not found")
            model.position = position
        await self._session.flush()
        return await self.list_for_palette(palette_id)

    async def list_for_palettes_capped(
        self, palette_ids: list[int], colors_limit: int
    ) -> dict[int, list[PaletteColor]]:
        if not palette_ids:
            return {}
        row_number = (
            func.row_number()
            .over(
                partition_by=PaletteColorModel.palette_id,
                order_by=PaletteColorModel.position,
            )
            .label("rn")
        )
        subquery = (
            select(PaletteColorModel, row_number)
            .where(PaletteColorModel.palette_id.in_(palette_ids))
            .subquery()
        )
        ranked = aliased(PaletteColorModel, subquery)
        result = await self._session.execute(
            select(ranked).where(subquery.c.rn <= colors_limit)
        )
        colors_by_palette: dict[int, list[PaletteColor]] = defaultdict(list)
        for model in result.scalars().all():
            colors_by_palette[model.palette_id].append(_to_entity(model))
        return dict(colors_by_palette)

    async def count_by_palette(self, palette_ids: list[int]) -> dict[int, int]:
        if not palette_ids:
            return {}
        result = await self._session.execute(
            select(PaletteColorModel.palette_id, func.count())
            .where(PaletteColorModel.palette_id.in_(palette_ids))
            .group_by(PaletteColorModel.palette_id)
        )
        return {palette_id: count for palette_id, count in result.all()}
