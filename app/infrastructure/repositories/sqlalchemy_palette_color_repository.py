from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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
