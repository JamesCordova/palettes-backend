from abc import ABC, abstractmethod

from app.domain.entities.palette import Palette
from app.domain.entities.palette_color import PaletteColor
from app.domain.entities.tag import Tag


class PaletteRepository(ABC):
    @abstractmethod
    async def get_by_id(self, palette_id: int) -> Palette | None: ...

    @abstractmethod
    async def get_by_id_with_colors(
        self, palette_id: int
    ) -> tuple[Palette, list[PaletteColor]] | None: ...

    @abstractmethod
    async def list_public(
        self, limit: int = 50, offset: int = 0
    ) -> tuple[list[Palette], int]: ...

    @abstractmethod
    async def list_by_user(
        self, user_id: int, limit: int = 50, offset: int = 0, public_only: bool = False
    ) -> tuple[list[Palette], int]: ...

    @abstractmethod
    async def list_public_by_tag(
        self, tag_id: int, limit: int = 50, offset: int = 0
    ) -> tuple[list[Palette], int]: ...

    @abstractmethod
    async def search_public(
        self, query: str, limit: int = 50, offset: int = 0
    ) -> tuple[list[Palette], int]: ...

    @abstractmethod
    async def create(self, palette: Palette) -> Palette: ...

    @abstractmethod
    async def update(self, palette: Palette) -> Palette: ...

    @abstractmethod
    async def delete(self, palette_id: int) -> None: ...

    @abstractmethod
    async def fork(
        self, source_palette_id: int, new_owner_id: int, name: str | None
    ) -> Palette: ...

    @abstractmethod
    async def add_tag(self, palette_id: int, tag_id: int) -> None: ...

    @abstractmethod
    async def remove_tag(self, palette_id: int, tag_id: int) -> None: ...

    @abstractmethod
    async def list_tags(self, palette_id: int) -> list[Tag]: ...
