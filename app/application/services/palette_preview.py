from app.application.dtos.palette_dto import PaletteListItem
from app.core.constants import COLOR_PREVIEW_LIMIT
from app.domain.entities.palette import Palette
from app.domain.repositories.palette_color_repository import PaletteColorRepository


async def build_palette_list_items(
    palette_color_repository: PaletteColorRepository,
    palettes: list[Palette],
    colors_limit: int = COLOR_PREVIEW_LIMIT,
) -> list[PaletteListItem]:
    palette_ids = [p.id for p in palettes if p.id is not None]
    colors_by_palette = await palette_color_repository.list_for_palettes_capped(
        palette_ids, colors_limit
    )
    counts_by_palette = await palette_color_repository.count_by_palette(palette_ids)
    return [
        PaletteListItem(
            palette=palette,
            colors=colors_by_palette.get(palette.id, []),
            color_count=counts_by_palette.get(palette.id, 0),
        )
        for palette in palettes
    ]
