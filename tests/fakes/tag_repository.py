from __future__ import annotations

from dataclasses import replace

from app.domain.entities.tag import Tag
from app.domain.repositories.tag_repository import TagRepository


class FakeTagRepository(TagRepository):
    def __init__(self) -> None:
        self._tags: dict[int, Tag] = {}
        self._next_id = 1

    async def get_by_id(self, tag_id: int) -> Tag | None:
        return self._tags.get(tag_id)

    async def get_by_name(self, name: str) -> Tag | None:
        return next((t for t in self._tags.values() if t.name == name), None)

    async def create(self, tag: Tag) -> Tag:
        created = replace(tag, id=self._next_id)
        self._tags[created.id] = created
        self._next_id += 1
        return created

    async def list(self, limit: int = 50, offset: int = 0) -> tuple[list[Tag], int]:
        items = list(self._tags.values())
        return items[offset : offset + limit], len(items)

    async def list_for_palette(self, palette_id: int) -> list[Tag]:
        # Not exercised by any current service — palette-tag associations
        # are tracked on FakePaletteRepository, which is what
        # PaletteService.list_tags actually calls.
        raise NotImplementedError

    async def delete(self, tag_id: int) -> None:
        self._tags.pop(tag_id, None)
