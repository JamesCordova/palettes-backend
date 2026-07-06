from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.domain.entities.palette import Palette
from app.domain.entities.palette_color import PaletteColor
from app.domain.entities.tag import Tag
from app.domain.repositories.palette_repository import PaletteRepository
from app.infrastructure.models.palette_color_model import PaletteColorModel
from app.infrastructure.models.palette_model import PaletteModel
from app.infrastructure.models.palette_tag_model import PaletteTagModel
from app.infrastructure.models.tag_model import TagModel


def _to_entity(model: PaletteModel) -> Palette:
    return Palette(
        id=model.id,
        user_id=model.user_id,
        name=model.name,
        description=model.description,
        is_public=model.is_public,
        forked_from=model.forked_from,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _color_to_entity(model: PaletteColorModel) -> PaletteColor:
    return PaletteColor(
        id=model.id,
        palette_id=model.palette_id,
        hex_code=model.hex_code,
        name=model.name,
        position=model.position,
    )


def _tag_to_entity(model: TagModel) -> Tag:
    return Tag(id=model.id, name=model.name)


class SQLAlchemyPaletteRepository(PaletteRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, palette_id: int) -> Palette | None:
        model = await self._session.get(PaletteModel, palette_id)
        return _to_entity(model) if model else None

    async def get_by_id_with_colors(
        self, palette_id: int
    ) -> tuple[Palette, list[PaletteColor]] | None:
        model = await self._session.get(PaletteModel, palette_id)
        if model is None:
            return None
        return _to_entity(model), [_color_to_entity(color) for color in model.colors]

    async def list_public(
        self, limit: int = 50, offset: int = 0
    ) -> tuple[list[Palette], int]:
        base = select(PaletteModel).where(PaletteModel.is_public.is_(True))
        return await self._paginate(base, limit, offset)

    async def list_by_user(
        self, user_id: int, limit: int = 50, offset: int = 0
    ) -> tuple[list[Palette], int]:
        base = select(PaletteModel).where(PaletteModel.user_id == user_id)
        return await self._paginate(base, limit, offset)

    async def list_public_by_tag(
        self, tag_id: int, limit: int = 50, offset: int = 0
    ) -> tuple[list[Palette], int]:
        base = (
            select(PaletteModel)
            .join(PaletteTagModel, PaletteTagModel.palette_id == PaletteModel.id)
            .where(PaletteTagModel.tag_id == tag_id, PaletteModel.is_public.is_(True))
        )
        return await self._paginate(base, limit, offset)

    async def search_public(
        self, query: str, limit: int = 50, offset: int = 0
    ) -> tuple[list[Palette], int]:
        pattern = f"%{query}%"
        base = select(PaletteModel).where(
            PaletteModel.is_public.is_(True),
            or_(
                PaletteModel.name.ilike(pattern),
                PaletteModel.description.ilike(pattern),
            ),
        )
        return await self._paginate(base, limit, offset)

    async def _paginate(
        self, base_query, limit: int, offset: int
    ) -> tuple[list[Palette], int]:
        total = (
            await self._session.execute(
                select(func.count()).select_from(base_query.subquery())
            )
        ).scalar_one()
        result = await self._session.execute(base_query.limit(limit).offset(offset))
        items = [_to_entity(model) for model in result.scalars().all()]
        return items, total

    async def create(self, palette: Palette) -> Palette:
        model = PaletteModel(
            user_id=palette.user_id,
            name=palette.name,
            description=palette.description,
            is_public=palette.is_public,
            forked_from=palette.forked_from,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return _to_entity(model)

    async def update(self, palette: Palette) -> Palette:
        model = await self._session.get(PaletteModel, palette.id)
        if model is None:
            raise NotFoundError(f"Palette {palette.id} not found")
        model.name = palette.name
        model.description = palette.description
        model.is_public = palette.is_public
        await self._session.flush()
        await self._session.refresh(model)
        return _to_entity(model)

    async def delete(self, palette_id: int) -> None:
        model = await self._session.get(PaletteModel, palette_id)
        if model is None:
            raise NotFoundError(f"Palette {palette_id} not found")
        await self._session.delete(model)
        await self._session.flush()

    async def fork(
        self, source_palette_id: int, new_owner_id: int, name: str | None
    ) -> Palette:
        source = await self._session.get(PaletteModel, source_palette_id)
        if source is None:
            raise NotFoundError(f"Palette {source_palette_id} not found")
        forked = PaletteModel(
            user_id=new_owner_id,
            name=name or f"{source.name} (fork)",
            description=source.description,
            is_public=source.is_public,
            forked_from=source.id,
        )
        self._session.add(forked)
        await self._session.flush()
        for color in source.colors:
            self._session.add(
                PaletteColorModel(
                    palette_id=forked.id,
                    hex_code=color.hex_code,
                    name=color.name,
                    position=color.position,
                )
            )
        await self._session.flush()
        await self._session.refresh(forked)
        return _to_entity(forked)

    async def add_tag(self, palette_id: int, tag_id: int) -> None:
        self._session.add(PaletteTagModel(palette_id=palette_id, tag_id=tag_id))
        await self._session.flush()

    async def remove_tag(self, palette_id: int, tag_id: int) -> None:
        model = await self._session.get(PaletteTagModel, (palette_id, tag_id))
        if model is None:
            raise NotFoundError(f"Tag {tag_id} not attached to palette {palette_id}")
        await self._session.delete(model)
        await self._session.flush()

    async def list_tags(self, palette_id: int) -> list[Tag]:
        result = await self._session.execute(
            select(TagModel)
            .join(PaletteTagModel, PaletteTagModel.tag_id == TagModel.id)
            .where(PaletteTagModel.palette_id == palette_id)
        )
        return [_tag_to_entity(model) for model in result.scalars().all()]
