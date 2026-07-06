from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.color_catalog_service import ColorCatalogService
from app.core.security import decode_access_token
from app.application.services.favorite_service import FavoriteService
from app.application.services.palette_service import PaletteService
from app.application.services.tag_service import TagService
from app.application.services.user_service import UserService
from app.domain.repositories.color_catalog_repository import ColorCatalogRepository
from app.domain.repositories.favorite_repository import FavoriteRepository
from app.domain.repositories.palette_color_repository import PaletteColorRepository
from app.domain.repositories.palette_repository import PaletteRepository
from app.domain.repositories.tag_repository import TagRepository
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.sqlalchemy_color_catalog_repository import (
    SQLAlchemyColorCatalogRepository,
)
from app.infrastructure.repositories.sqlalchemy_favorite_repository import (
    SQLAlchemyFavoriteRepository,
)
from app.infrastructure.repositories.sqlalchemy_palette_color_repository import (
    SQLAlchemyPaletteColorRepository,
)
from app.infrastructure.repositories.sqlalchemy_palette_repository import (
    SQLAlchemyPaletteRepository,
)
from app.infrastructure.repositories.sqlalchemy_tag_repository import SQLAlchemyTagRepository
from app.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository

DbSession = Annotated[AsyncSession, Depends(get_db)]


def get_user_repository(db: DbSession) -> UserRepository:
    return SQLAlchemyUserRepository(db)


def get_palette_repository(db: DbSession) -> PaletteRepository:
    return SQLAlchemyPaletteRepository(db)


def get_palette_color_repository(db: DbSession) -> PaletteColorRepository:
    return SQLAlchemyPaletteColorRepository(db)


def get_color_catalog_repository(db: DbSession) -> ColorCatalogRepository:
    return SQLAlchemyColorCatalogRepository(db)


def get_favorite_repository(db: DbSession) -> FavoriteRepository:
    return SQLAlchemyFavoriteRepository(db)


def get_tag_repository(db: DbSession) -> TagRepository:
    return SQLAlchemyTagRepository(db)


def get_user_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserService:
    return UserService(user_repository)


def get_palette_service(
    palette_repository: Annotated[PaletteRepository, Depends(get_palette_repository)],
    palette_color_repository: Annotated[
        PaletteColorRepository, Depends(get_palette_color_repository)
    ],
    color_catalog_repository: Annotated[
        ColorCatalogRepository, Depends(get_color_catalog_repository)
    ],
    tag_repository: Annotated[TagRepository, Depends(get_tag_repository)],
) -> PaletteService:
    return PaletteService(
        palette_repository, palette_color_repository, color_catalog_repository, tag_repository
    )


def get_color_catalog_service(
    color_catalog_repository: Annotated[
        ColorCatalogRepository, Depends(get_color_catalog_repository)
    ],
) -> ColorCatalogService:
    return ColorCatalogService(color_catalog_repository)


def get_favorite_service(
    favorite_repository: Annotated[FavoriteRepository, Depends(get_favorite_repository)],
) -> FavoriteService:
    return FavoriteService(favorite_repository)


def get_tag_service(
    tag_repository: Annotated[TagRepository, Depends(get_tag_repository)],
) -> TagService:
    return TagService(tag_repository)


_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=True)
_oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def get_current_user_id(token: Annotated[str, Depends(_oauth2_scheme)]) -> int:
    return decode_access_token(token)


def get_optional_current_user_id(
    token: Annotated[str | None, Depends(_oauth2_scheme_optional)],
) -> int | None:
    if token is None:
        return None
    return decode_access_token(token)
