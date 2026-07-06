from app.core.exceptions import ForbiddenError
from app.domain.entities.favorite import Favorite
from app.domain.entities.palette import Palette
from app.domain.repositories.favorite_repository import FavoriteRepository


class FavoriteService:
    def __init__(self, favorite_repository: FavoriteRepository) -> None:
        self._favorite_repository = favorite_repository

    async def favorite_palette(self, user_id: int, palette_id: int) -> Favorite:
        if await self._favorite_repository.exists(user_id, palette_id):
            return Favorite(user_id=user_id, palette_id=palette_id, created_at=None)
        return await self._favorite_repository.add(user_id, palette_id)

    async def unfavorite_palette(self, user_id: int, palette_id: int) -> None:
        await self._favorite_repository.remove(user_id, palette_id)

    async def list_favorites(
        self, user_id: int, requesting_user_id: int, limit: int = 50, offset: int = 0
    ) -> tuple[list[Palette], int]:
        if user_id != requesting_user_id:
            raise ForbiddenError(f"User {requesting_user_id} cannot view favorites of {user_id}")
        return await self._favorite_repository.list_by_user(user_id, limit, offset)

    async def is_favorited(self, user_id: int, palette_id: int) -> bool:
        return await self._favorite_repository.exists(user_id, palette_id)
