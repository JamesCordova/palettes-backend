from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities.tag import Tag


class TagRepository(ABC):
    @abstractmethod
    async def get_by_id(self, tag_id: int) -> Tag | None: ...

    @abstractmethod
    async def get_by_name(self, name: str) -> Tag | None: ...

    @abstractmethod
    async def create(self, tag: Tag) -> Tag: ...

    @abstractmethod
    async def list(self, limit: int = 50, offset: int = 0) -> tuple[list[Tag], int]: ...

    @abstractmethod
    async def list_for_palette(self, palette_id: int) -> list[Tag]: ...

    @abstractmethod
    async def delete(self, tag_id: int) -> None: ...
