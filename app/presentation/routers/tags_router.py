from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.application.dtos.tag_dto import CreateTagDTO
from app.application.services.palette_service import PaletteService
from app.application.services.tag_service import TagService
from app.core.constants import DEFAULT_PAGE_SIZE
from app.presentation.dependencies import get_palette_service, get_tag_service
from app.presentation.schemas.pagination_schema import Paginated
from app.presentation.schemas.palette_schema import PaletteRead
from app.presentation.schemas.tag_schema import TagCreate, TagRead

router = APIRouter(prefix="/tags", tags=["tags"])

TagServiceDep = Annotated[TagService, Depends(get_tag_service)]
PaletteServiceDep = Annotated[PaletteService, Depends(get_palette_service)]


@router.post("", response_model=TagRead, status_code=status.HTTP_201_CREATED)
async def create_tag(payload: TagCreate, service: TagServiceDep) -> TagRead:
    tag = await service.create_tag(CreateTagDTO(name=payload.name))
    return TagRead.model_validate(tag)


@router.get("", response_model=Paginated[TagRead])
async def list_tags(
    service: TagServiceDep,
    limit: int = Query(default=DEFAULT_PAGE_SIZE, le=200),
    offset: int = 0,
) -> Paginated[TagRead]:
    tags, total = await service.list_tags(limit, offset)
    return Paginated(
        items=[TagRead.model_validate(t) for t in tags],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(tag_id: int, service: TagServiceDep) -> None:
    await service.delete_tag(tag_id)


@router.get("/{tag_id}/palettes", response_model=Paginated[PaletteRead])
async def list_palettes_by_tag(
    tag_id: int,
    service: PaletteServiceDep,
    limit: int = Query(default=DEFAULT_PAGE_SIZE, le=200),
    offset: int = 0,
) -> Paginated[PaletteRead]:
    palettes, total = await service.list_public_palettes_by_tag(tag_id, limit, offset)
    return Paginated(
        items=[PaletteRead.model_validate(p) for p in palettes],
        total=total,
        limit=limit,
        offset=offset,
    )
