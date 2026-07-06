from app.application.dtos.palette_dto import PaletteListItem
from app.application.services.palette_preview import build_palette_list_items
from app.core.exceptions import ForbiddenError
from app.domain.entities.favorite import Favorite
from app.domain.repositories.favorite_repository import FavoriteRepository
from app.domain.repositories.palette_color_repository import PaletteColorRepository


class FavoriteService:
    def __init__(
        self,
        favorite_repository: FavoriteRepository,
        palette_color_repository: PaletteColorRepository,
    ) -> None:
        self._favorite_repository = favorite_repository
        self._palette_color_repository = palette_color_repository

    async def favorite_palette(self, user_id: int, palette_id: int) -> Favorite:
        if await self._favorite_repository.exists(user_id, palette_id):
            return Favorite(user_id=user_id, palette_id=palette_id, created_at=None)
        return await self._favorite_repository.add(user_id, palette_id)

    async def unfavorite_palette(self, user_id: int, palette_id: int) -> None:
        await self._favorite_repository.remove(user_id, palette_id)

    async def list_favorites(
        self, user_id: int, requesting_user_id: int, limit: int = 50, offset: int = 0
    ) -> tuple[list[PaletteListItem], int]:
        if user_id != requesting_user_id:
            raise ForbiddenError(f"User {requesting_user_id} cannot view favorites of {user_id}")
        palettes, total = await self._favorite_repository.list_by_user(user_id, limit, offset)
        items = await build_palette_list_items(self._palette_color_repository, palettes)
        return items, total

    async def is_favorited(self, user_id: int, palette_id: int) -> bool:
        return await self._favorite_repository.exists(user_id, palette_id)
