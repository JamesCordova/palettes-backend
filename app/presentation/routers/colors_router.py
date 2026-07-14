from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.application.dtos.color_catalog_dto import UpdateColorNameDTO
from app.application.services.color_catalog_service import ColorCatalogService
from app.presentation.dependencies import get_color_catalog_service, get_current_user_id
from app.presentation.schemas.color_catalog_schema import ColorCatalogRead, ColorCatalogUpdate
from app.presentation.schemas.pagination_schema import Paginated

router = APIRouter(prefix="/colors", tags=["colors"])

ColorCatalogServiceDep = Annotated[ColorCatalogService, Depends(get_color_catalog_service)]
CurrentUserIdDep = Annotated[int, Depends(get_current_user_id)]


@router.get("/trending", response_model=Paginated[ColorCatalogRead])
async def trending_colors(
    service: ColorCatalogServiceDep,
    limit: int = Query(default=20, le=200),
    offset: int = 0,
) -> Paginated[ColorCatalogRead]:
    colors, total = await service.most_used(limit, offset)
    return Paginated(
        items=[ColorCatalogRead.model_validate(c) for c in colors],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("", response_model=Paginated[ColorCatalogRead])
async def browse_colors(
    service: ColorCatalogServiceDep,
    hue_min: int = Query(default=0, ge=0, le=360),
    hue_max: int = Query(default=360, ge=0, le=360),
    limit: int = Query(default=50, le=200),
    offset: int = 0,
) -> Paginated[ColorCatalogRead]:
    colors, total = await service.browse_by_hue(hue_min, hue_max, limit, offset)
    return Paginated(
        items=[ColorCatalogRead.model_validate(c) for c in colors],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{hex_code}", response_model=ColorCatalogRead)
async def get_color(hex_code: str, service: ColorCatalogServiceDep) -> ColorCatalogRead:
    color = await service.get_color(hex_code)
    return ColorCatalogRead.model_validate(color)


@router.patch("/{hex_code}", response_model=ColorCatalogRead)
async def rename_color(
    hex_code: str,
    payload: ColorCatalogUpdate,
    service: ColorCatalogServiceDep,
    current_user_id: CurrentUserIdDep,
) -> ColorCatalogRead:
    color = await service.rename_color(hex_code, UpdateColorNameDTO(name=payload.name))
    return ColorCatalogRead.model_validate(color)
