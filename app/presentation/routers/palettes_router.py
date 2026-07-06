from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.application.dtos.palette_color_dto import (
    AddPaletteColorDTO,
    ReorderPaletteColorDTO,
)
from app.application.dtos.palette_dto import CreatePaletteDTO, ForkPaletteDTO, UpdatePaletteDTO
from app.application.services.palette_service import PaletteService
from app.core.constants import DEFAULT_PAGE_SIZE
from app.presentation.dependencies import (
    get_current_user_id,
    get_optional_current_user_id,
    get_palette_service,
)
from app.presentation.schemas.palette_color_schema import (
    PaletteColorCreate,
    PaletteColorRead,
    ReorderPaletteColorsRequest,
)
from app.presentation.schemas.pagination_schema import Paginated
from app.presentation.schemas.palette_schema import (
    ForkPaletteRequest,
    PaletteCreate,
    PaletteRead,
    PaletteUpdate,
)

router = APIRouter(prefix="/palettes", tags=["palettes"])

PaletteServiceDep = Annotated[PaletteService, Depends(get_palette_service)]
CurrentUserIdDep = Annotated[int, Depends(get_current_user_id)]
OptionalCurrentUserIdDep = Annotated[int | None, Depends(get_optional_current_user_id)]


@router.post("", response_model=PaletteRead, status_code=status.HTTP_201_CREATED)
async def create_palette(
    payload: PaletteCreate, service: PaletteServiceDep, current_user_id: CurrentUserIdDep
) -> PaletteRead:
    palette = await service.create_palette(
        current_user_id,
        CreatePaletteDTO(
            name=payload.name, description=payload.description, is_public=payload.is_public
        ),
    )
    return PaletteRead.model_validate(palette)


@router.get("", response_model=Paginated[PaletteRead])
async def list_public_palettes(
    service: PaletteServiceDep,
    limit: int = Query(default=DEFAULT_PAGE_SIZE, le=200),
    offset: int = 0,
) -> Paginated[PaletteRead]:
    palettes, total = await service.list_public_palettes(limit, offset)
    return Paginated(
        items=[PaletteRead.model_validate(p) for p in palettes],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/search", response_model=Paginated[PaletteRead])
async def search_palettes(
    service: PaletteServiceDep,
    q: str = Query(min_length=1),
    limit: int = Query(default=DEFAULT_PAGE_SIZE, le=200),
    offset: int = 0,
) -> Paginated[PaletteRead]:
    palettes, total = await service.search_public_palettes(q, limit, offset)
    return Paginated(
        items=[PaletteRead.model_validate(p) for p in palettes],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{palette_id}", response_model=PaletteRead)
async def get_palette(
    palette_id: int, service: PaletteServiceDep, current_user_id: OptionalCurrentUserIdDep
) -> PaletteRead:
    palette = await service.get_palette(palette_id, current_user_id)
    return PaletteRead.model_validate(palette)


@router.patch("/{palette_id}", response_model=PaletteRead)
async def update_palette(
    palette_id: int,
    payload: PaletteUpdate,
    service: PaletteServiceDep,
    current_user_id: CurrentUserIdDep,
) -> PaletteRead:
    palette = await service.update_palette(
        palette_id,
        current_user_id,
        UpdatePaletteDTO(
            name=payload.name, description=payload.description, is_public=payload.is_public
        ),
    )
    return PaletteRead.model_validate(palette)


@router.delete("/{palette_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_palette(
    palette_id: int, service: PaletteServiceDep, current_user_id: CurrentUserIdDep
) -> None:
    await service.delete_palette(palette_id, current_user_id)


@router.post("/{palette_id}/fork", response_model=PaletteRead, status_code=status.HTTP_201_CREATED)
async def fork_palette(
    palette_id: int,
    payload: ForkPaletteRequest,
    service: PaletteServiceDep,
    current_user_id: CurrentUserIdDep,
) -> PaletteRead:
    palette = await service.fork_palette(
        palette_id, current_user_id, ForkPaletteDTO(name=payload.name)
    )
    return PaletteRead.model_validate(palette)


@router.post(
    "/{palette_id}/colors", response_model=PaletteColorRead, status_code=status.HTTP_201_CREATED
)
async def add_color(
    palette_id: int,
    payload: PaletteColorCreate,
    service: PaletteServiceDep,
    current_user_id: CurrentUserIdDep,
) -> PaletteColorRead:
    color = await service.add_color(
        palette_id,
        current_user_id,
        AddPaletteColorDTO(
            hex_code=payload.hex_code,
            hue=payload.hue,
            saturation=payload.saturation,
            lightness=payload.lightness,
            luminance=payload.luminance,
            name=payload.name,
            position=payload.position,
        ),
    )
    return PaletteColorRead.model_validate(color)


@router.delete("/{palette_id}/colors/{color_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_color(
    palette_id: int, color_id: int, service: PaletteServiceDep, current_user_id: CurrentUserIdDep
) -> None:
    await service.remove_color(palette_id, current_user_id, color_id)


@router.put("/{palette_id}/colors/reorder", response_model=list[PaletteColorRead])
async def reorder_colors(
    palette_id: int,
    payload: ReorderPaletteColorsRequest,
    service: PaletteServiceDep,
    current_user_id: CurrentUserIdDep,
) -> list[PaletteColorRead]:
    colors = await service.reorder_colors(
        palette_id, current_user_id, ReorderPaletteColorDTO(ordered_ids=payload.ordered_ids)
    )
    return [PaletteColorRead.model_validate(c) for c in colors]


@router.post("/{palette_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def add_tag(
    palette_id: int, tag_id: int, service: PaletteServiceDep, current_user_id: CurrentUserIdDep
) -> None:
    await service.add_tag(palette_id, current_user_id, tag_id)


@router.delete("/{palette_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_tag(
    palette_id: int, tag_id: int, service: PaletteServiceDep, current_user_id: CurrentUserIdDep
) -> None:
    await service.remove_tag(palette_id, current_user_id, tag_id)
