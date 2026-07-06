from abc import ABC, abstractmethod

from app.domain.entities.favorite import Favorite
from app.domain.entities.palette import Palette


class FavoriteRepository(ABC):
    @abstractmethod
    async def add(self, user_id: int, palette_id: int) -> Favorite: ...

    @abstractmethod
    async def remove(self, user_id: int, palette_id: int) -> None: ...

    @abstractmethod
    async def exists(self, user_id: int, palette_id: int) -> bool: ...

    @abstractmethod
    async def list_by_user(
        self, user_id: int, limit: int = 50, offset: int = 0
    ) -> tuple[list[Palette], int]: ...

    @abstractmethod
    async def count_for_palette(self, palette_id: int) -> int: ...
