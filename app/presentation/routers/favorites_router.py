from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.application.services.favorite_service import FavoriteService
from app.core.constants import DEFAULT_PAGE_SIZE
from app.presentation.dependencies import get_current_user_id, get_favorite_service
from app.presentation.schemas.pagination_schema import Paginated
from app.presentation.schemas.palette_schema import PaletteRead

router = APIRouter(tags=["favorites"])

FavoriteServiceDep = Annotated[FavoriteService, Depends(get_favorite_service)]
CurrentUserIdDep = Annotated[int, Depends(get_current_user_id)]


@router.post("/palettes/{palette_id}/favorite", status_code=status.HTTP_204_NO_CONTENT)
async def favorite_palette(
    palette_id: int, service: FavoriteServiceDep, current_user_id: CurrentUserIdDep
) -> None:
    await service.favorite_palette(current_user_id, palette_id)


@router.delete("/palettes/{palette_id}/favorite", status_code=status.HTTP_204_NO_CONTENT)
async def unfavorite_palette(
    palette_id: int, service: FavoriteServiceDep, current_user_id: CurrentUserIdDep
) -> None:
    await service.unfavorite_palette(current_user_id, palette_id)


@router.get("/users/{user_id}/favorites", response_model=Paginated[PaletteRead])
async def list_favorites(
    user_id: int,
    service: FavoriteServiceDep,
    current_user_id: CurrentUserIdDep,
    limit: int = Query(default=DEFAULT_PAGE_SIZE, le=200),
    offset: int = 0,
) -> Paginated[PaletteRead]:
    palettes, total = await service.list_favorites(user_id, current_user_id, limit, offset)
    return Paginated(
        items=[PaletteRead.model_validate(p) for p in palettes],
        total=total,
        limit=limit,
        offset=offset,
    )
