from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.application.services.color_catalog_service import ColorCatalogService
from app.presentation.dependencies import get_color_catalog_service
from app.presentation.schemas.color_catalog_schema import ColorCatalogRead

router = APIRouter(prefix="/colors", tags=["colors"])

ColorCatalogServiceDep = Annotated[ColorCatalogService, Depends(get_color_catalog_service)]


@router.get("/trending", response_model=list[ColorCatalogRead])
async def trending_colors(
    service: ColorCatalogServiceDep, limit: int = Query(default=20, le=100)
) -> list[ColorCatalogRead]:
    colors = await service.most_used(limit)
    return [ColorCatalogRead.model_validate(c) for c in colors]


@router.get("", response_model=list[ColorCatalogRead])
async def browse_colors(
    service: ColorCatalogServiceDep,
    hue_min: int = Query(default=0, ge=0, le=360),
    hue_max: int = Query(default=360, ge=0, le=360),
    limit: int = Query(default=50, le=200),
) -> list[ColorCatalogRead]:
    colors = await service.browse_by_hue(hue_min, hue_max, limit)
    return [ColorCatalogRead.model_validate(c) for c in colors]


@router.get("/{hex_code}", response_model=ColorCatalogRead)
async def get_color(hex_code: str, service: ColorCatalogServiceDep) -> ColorCatalogRead:
    color = await service.get_color(hex_code)
    return ColorCatalogRead.model_validate(color)
