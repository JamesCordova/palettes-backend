from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.domain.entities.tag import Tag
from app.domain.repositories.tag_repository import TagRepository
from app.infrastructure.models.palette_tag_model import PaletteTagModel
from app.infrastructure.models.tag_model import TagModel


def _to_entity(model: TagModel) -> Tag:
    return Tag(id=model.id, name=model.name)


class SQLAlchemyTagRepository(TagRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, tag_id: int) -> Tag | None:
        model = await self._session.get(TagModel, tag_id)
        return _to_entity(model) if model else None

    async def get_by_name(self, name: str) -> Tag | None:
        result = await self._session.execute(select(TagModel).where(TagModel.name == name))
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def create(self, tag: Tag) -> Tag:
        model = TagModel(name=tag.name)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return _to_entity(model)

    async def list(self, limit: int = 50, offset: int = 0) -> tuple[list[Tag], int]:
        total = (
            await self._session.execute(select(func.count()).select_from(TagModel))
        ).scalar_one()
        result = await self._session.execute(select(TagModel).limit(limit).offset(offset))
        items = [_to_entity(model) for model in result.scalars().all()]
        return items, total

    async def delete(self, tag_id: int) -> None:
        model = await self._session.get(TagModel, tag_id)
        if model is None:
            raise NotFoundError(f"Tag {tag_id} not found")
        await self._session.delete(model)
        await self._session.flush()

    async def list_for_palette(self, palette_id: int) -> list[Tag]:
        result = await self._session.execute(
            select(TagModel)
            .join(PaletteTagModel, PaletteTagModel.tag_id == TagModel.id)
            .where(PaletteTagModel.palette_id == palette_id)
        )
        return [_to_entity(model) for model in result.scalars().all()]
