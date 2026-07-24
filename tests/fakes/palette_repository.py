from dataclasses import replace
from datetime import UTC, datetime

from app.domain.entities.palette import Palette
from app.domain.entities.palette_color import PaletteColor
from app.domain.entities.tag import Tag
from app.domain.repositories.palette_color_repository import PaletteColorRepository
from app.domain.repositories.palette_repository import PaletteRepository
from app.domain.repositories.tag_repository import TagRepository


class FakePaletteRepository(PaletteRepository):
    # Takes the palette-color and tag fakes it's constructed alongside so
    # get_by_id_with_colors/list_tags can resolve across "tables" the same
    # way a real join would — the two repositories are otherwise unrelated
    # objects in this in-memory setup.
    def __init__(
        self,
        palette_color_repository: PaletteColorRepository | None = None,
        tag_repository: TagRepository | None = None,
    ) -> None:
        self._palettes: dict[int, Palette] = {}
        self._tags_by_palette: dict[int, set[int]] = {}
        self._next_id = 1
        self._palette_color_repository = palette_color_repository
        self._tag_repository = tag_repository

    async def get_by_id(self, palette_id: int) -> Palette | None:
        return self._palettes.get(palette_id)

    async def get_by_id_with_colors(
        self, palette_id: int
    ) -> tuple[Palette, list[PaletteColor]] | None:
        palette = self._palettes.get(palette_id)
        if palette is None:
            return None
        colors: list[PaletteColor] = []
        if self._palette_color_repository is not None:
            colors = await self._palette_color_repository.list_for_palette(palette_id)
        return palette, colors

    async def list_public(
        self, limit: int = 50, offset: int = 0
    ) -> tuple[list[Palette], int]:
        matching = [p for p in self._palettes.values() if p.is_public]
        return matching[offset : offset + limit], len(matching)

    async def list_by_user(
        self, user_id: int, limit: int = 50, offset: int = 0, public_only: bool = False
    ) -> tuple[list[Palette], int]:
        matching = [
            p
            for p in self._palettes.values()
            if p.user_id == user_id and (p.is_public or not public_only)
        ]
        return matching[offset : offset + limit], len(matching)

    async def list_public_by_tag(
        self, tag_id: int, limit: int = 50, offset: int = 0
    ) -> tuple[list[Palette], int]:
        matching = [
            p
            for p in self._palettes.values()
            if p.is_public and tag_id in self._tags_by_palette.get(p.id, set())
        ]
        return matching[offset : offset + limit], len(matching)

    async def search_public(
        self, query: str, limit: int = 50, offset: int = 0
    ) -> tuple[list[Palette], int]:
        matching = [
            p
            for p in self._palettes.values()
            if p.is_public and query.lower() in p.name.lower()
        ]
        return matching[offset : offset + limit], len(matching)

    async def create(self, palette: Palette) -> Palette:
        now = datetime.now(UTC)
        created = replace(palette, id=self._next_id, created_at=now, updated_at=now)
        self._palettes[created.id] = created
        self._next_id += 1
        return created

    async def update(self, palette: Palette) -> Palette:
        self._palettes[palette.id] = palette
        return palette

    async def delete(self, palette_id: int) -> None:
        self._palettes.pop(palette_id, None)
        self._tags_by_palette.pop(palette_id, None)

    async def fork(
        self, source_palette_id: int, new_owner_id: int, name: str | None
    ) -> Palette:
        source = self._palettes[source_palette_id]
        now = datetime.now(UTC)
        forked = Palette(
            id=self._next_id,
            user_id=new_owner_id,
            name=name or source.name,
            description=source.description,
            is_public=source.is_public,
            forked_from=source_palette_id,
            created_at=now,
            updated_at=now,
        )
        self._palettes[forked.id] = forked
        self._next_id += 1
        return forked

    async def add_tag(self, palette_id: int, tag_id: int) -> None:
        self._tags_by_palette.setdefault(palette_id, set()).add(tag_id)

    async def remove_tag(self, palette_id: int, tag_id: int) -> None:
        self._tags_by_palette.get(palette_id, set()).discard(tag_id)

    async def list_tags(self, palette_id: int) -> list[Tag]:
        if self._tag_repository is None:
            return []
        tag_ids = self._tags_by_palette.get(palette_id, set())
        tags = [await self._tag_repository.get_by_id(tag_id) for tag_id in tag_ids]
        return [tag for tag in tags if tag is not None]
