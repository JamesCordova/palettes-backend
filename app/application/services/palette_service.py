from app.application.dtos.palette_color_dto import (
    AddPaletteColorDTO,
    ReorderPaletteColorDTO,
)
from app.application.dtos.palette_dto import CreatePaletteDTO, ForkPaletteDTO, UpdatePaletteDTO
from app.core.exceptions import ForbiddenError, NotFoundError
from app.domain.entities.color_catalog import ColorCatalog
from app.domain.entities.palette import Palette
from app.domain.entities.palette_color import PaletteColor
from app.domain.entities.tag import Tag
from app.domain.repositories.color_catalog_repository import ColorCatalogRepository
from app.domain.repositories.palette_color_repository import PaletteColorRepository
from app.domain.repositories.palette_repository import PaletteRepository
from app.domain.repositories.tag_repository import TagRepository


class PaletteService:
    def __init__(
        self,
        palette_repository: PaletteRepository,
        palette_color_repository: PaletteColorRepository,
        color_catalog_repository: ColorCatalogRepository,
        tag_repository: TagRepository,
    ) -> None:
        self._palette_repository = palette_repository
        self._palette_color_repository = palette_color_repository
        self._color_catalog_repository = color_catalog_repository
        self._tag_repository = tag_repository

    async def create_palette(self, user_id: int, dto: CreatePaletteDTO) -> Palette:
        palette = Palette(
            id=None,
            user_id=user_id,
            name=dto.name,
            description=dto.description,
            is_public=dto.is_public,
            forked_from=None,
            created_at=None,
            updated_at=None,
        )
        return await self._palette_repository.create(palette)

    async def get_palette(self, palette_id: int, requesting_user_id: int | None) -> Palette:
        palette = await self._palette_repository.get_by_id(palette_id)
        if palette is None:
            raise NotFoundError(f"Palette {palette_id} not found")
        if not palette.is_public and palette.user_id != requesting_user_id:
            raise ForbiddenError(f"Palette {palette_id} is private")
        return palette

    async def list_public_palettes(
        self, limit: int = 50, offset: int = 0
    ) -> tuple[list[Palette], int]:
        return await self._palette_repository.list_public(limit, offset)

    async def list_user_palettes(
        self, user_id: int, limit: int = 50, offset: int = 0
    ) -> tuple[list[Palette], int]:
        return await self._palette_repository.list_by_user(user_id, limit, offset)

    async def list_public_palettes_by_tag(
        self, tag_id: int, limit: int = 50, offset: int = 0
    ) -> tuple[list[Palette], int]:
        return await self._palette_repository.list_public_by_tag(tag_id, limit, offset)

    async def search_public_palettes(
        self, query: str, limit: int = 50, offset: int = 0
    ) -> tuple[list[Palette], int]:
        return await self._palette_repository.search_public(query, limit, offset)

    async def update_palette(
        self, palette_id: int, user_id: int, dto: UpdatePaletteDTO
    ) -> Palette:
        palette = await self._get_owned_palette(palette_id, user_id)
        palette.name = dto.name
        palette.description = dto.description
        palette.is_public = dto.is_public
        return await self._palette_repository.update(palette)

    async def delete_palette(self, palette_id: int, user_id: int) -> None:
        await self._get_owned_palette(palette_id, user_id)
        await self._palette_repository.delete(palette_id)

    async def fork_palette(self, palette_id: int, requesting_user_id: int, dto: ForkPaletteDTO) -> Palette:
        await self.get_palette(palette_id, requesting_user_id)
        return await self._palette_repository.fork(palette_id, requesting_user_id, dto.name)

    async def add_color(
        self, palette_id: int, user_id: int, dto: AddPaletteColorDTO
    ) -> PaletteColor:
        await self._get_owned_palette(palette_id, user_id)
        await self._color_catalog_repository.upsert(
            ColorCatalog(
                hex_code=dto.hex_code,
                hue=dto.hue,
                saturation=dto.saturation,
                lightness=dto.lightness,
                luminance=dto.luminance,
                usage_count=0,
                created_at=None,
            )
        )
        position = dto.position
        if position is None:
            existing = await self._palette_color_repository.list_for_palette(palette_id)
            position = len(existing) + 1
        return await self._palette_color_repository.add(
            PaletteColor(
                id=None,
                palette_id=palette_id,
                hex_code=dto.hex_code,
                name=dto.name,
                position=position,
            )
        )

    async def remove_color(self, palette_id: int, user_id: int, palette_color_id: int) -> None:
        await self._get_owned_palette(palette_id, user_id)
        await self._palette_color_repository.remove(palette_color_id)

    async def reorder_colors(
        self, palette_id: int, user_id: int, dto: ReorderPaletteColorDTO
    ) -> list[PaletteColor]:
        await self._get_owned_palette(palette_id, user_id)
        return await self._palette_color_repository.reorder(palette_id, dto.ordered_ids)

    async def add_tag(self, palette_id: int, user_id: int, tag_id: int) -> None:
        await self._get_owned_palette(palette_id, user_id)
        await self._palette_repository.add_tag(palette_id, tag_id)

    async def remove_tag(self, palette_id: int, user_id: int, tag_id: int) -> None:
        await self._get_owned_palette(palette_id, user_id)
        await self._palette_repository.remove_tag(palette_id, tag_id)

    async def list_tags(self, palette_id: int) -> list[Tag]:
        return await self._palette_repository.list_tags(palette_id)

    async def _get_owned_palette(self, palette_id: int, user_id: int) -> Palette:
        palette = await self._palette_repository.get_by_id(palette_id)
        if palette is None:
            raise NotFoundError(f"Palette {palette_id} not found")
        if palette.user_id != user_id:
            raise ForbiddenError(f"User {user_id} does not own palette {palette_id}")
        return palette
