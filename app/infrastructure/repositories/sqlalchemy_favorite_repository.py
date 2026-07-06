from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.domain.entities.favorite import Favorite
from app.domain.entities.palette import Palette
from app.domain.repositories.favorite_repository import FavoriteRepository
from app.infrastructure.models.favorite_model import FavoriteModel
from app.infrastructure.models.palette_model import PaletteModel


def _favorite_to_entity(model: FavoriteModel) -> Favorite:
    return Favorite(
        user_id=model.user_id, palette_id=model.palette_id, created_at=model.created_at
    )


def _palette_to_entity(model: PaletteModel) -> Palette:
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


class SQLAlchemyFavoriteRepository(FavoriteRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, user_id: int, palette_id: int) -> Favorite:
        model = FavoriteModel(user_id=user_id, palette_id=palette_id)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return _favorite_to_entity(model)

    async def remove(self, user_id: int, palette_id: int) -> None:
        model = await self._session.get(FavoriteModel, (user_id, palette_id))
        if model is None:
            raise NotFoundError(f"Favorite ({user_id}, {palette_id}) not found")
        await self._session.delete(model)
        await self._session.flush()

    async def exists(self, user_id: int, palette_id: int) -> bool:
        model = await self._session.get(FavoriteModel, (user_id, palette_id))
        return model is not None

    async def list_by_user(
        self, user_id: int, limit: int = 50, offset: int = 0
    ) -> tuple[list[Palette], int]:
        base = (
            select(PaletteModel)
            .join(FavoriteModel, FavoriteModel.palette_id == PaletteModel.id)
            .where(FavoriteModel.user_id == user_id)
        )
        total = (
            await self._session.execute(select(func.count()).select_from(base.subquery()))
        ).scalar_one()
        result = await self._session.execute(base.limit(limit).offset(offset))
        items = [_palette_to_entity(model) for model in result.scalars().all()]
        return items, total

    async def count_for_palette(self, palette_id: int) -> int:
        result = await self._session.execute(
            select(func.count()).select_from(FavoriteModel).where(
                FavoriteModel.palette_id == palette_id
            )
        )
        return result.scalar_one()
