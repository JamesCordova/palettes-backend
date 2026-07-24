from datetime import UTC, datetime

from app.domain.entities.favorite import Favorite
from app.domain.entities.palette import Palette
from app.domain.repositories.favorite_repository import FavoriteRepository
from app.domain.repositories.palette_repository import PaletteRepository


class FakeFavoriteRepository(FavoriteRepository):
    # Needs the palette fake to turn stored (user_id, palette_id) pairs back
    # into Palette objects for list_by_user, the same way the real
    # repository joins against the palettes table.
    def __init__(self, palette_repository: PaletteRepository | None = None) -> None:
        self._favorites: set[tuple[int, int]] = set()
        self._palette_repository = palette_repository

    async def add(self, user_id: int, palette_id: int) -> Favorite:
        self._favorites.add((user_id, palette_id))
        return Favorite(
            user_id=user_id, palette_id=palette_id, created_at=datetime.now(UTC)
        )

    async def remove(self, user_id: int, palette_id: int) -> None:
        self._favorites.discard((user_id, palette_id))

    async def exists(self, user_id: int, palette_id: int) -> bool:
        return (user_id, palette_id) in self._favorites

    async def list_by_user(
        self, user_id: int, limit: int = 50, offset: int = 0
    ) -> tuple[list[Palette], int]:
        palette_ids = [pid for (uid, pid) in self._favorites if uid == user_id]
        palettes: list[Palette] = []
        if self._palette_repository is not None:
            for palette_id in palette_ids:
                palette = await self._palette_repository.get_by_id(palette_id)
                if palette is not None:
                    palettes.append(palette)
        return palettes[offset : offset + limit], len(palettes)

    async def count_for_palette(self, palette_id: int) -> int:
        return len([1 for (_uid, pid) in self._favorites if pid == palette_id])
