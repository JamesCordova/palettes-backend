import pytest

from app.application.services.favorite_service import FavoriteService
from app.core.exceptions import ForbiddenError
from app.domain.entities.palette import Palette
from tests.fakes.favorite_repository import FakeFavoriteRepository
from tests.fakes.palette_color_repository import FakePaletteColorRepository
from tests.fakes.palette_repository import FakePaletteRepository


@pytest.fixture
def palette_repo() -> FakePaletteRepository:
    return FakePaletteRepository()


@pytest.fixture
def palette_color_repo() -> FakePaletteColorRepository:
    return FakePaletteColorRepository()


@pytest.fixture
def favorite_repo(palette_repo: FakePaletteRepository) -> FakeFavoriteRepository:
    return FakeFavoriteRepository(palette_repo)


@pytest.fixture
def service(
    favorite_repo: FakeFavoriteRepository,
    palette_color_repo: FakePaletteColorRepository,
) -> FavoriteService:
    return FavoriteService(favorite_repo, palette_color_repo)


async def _seed_palette(repo: FakePaletteRepository, user_id: int = 1) -> Palette:
    return await repo.create(
        Palette(
            id=None,
            user_id=user_id,
            name="Sunset",
            description=None,
            is_public=True,
            forked_from=None,
            created_at=None,
            updated_at=None,
        )
    )


class TestFavoritePalette:
    async def test_adds_a_new_favorite(
        self,
        service: FavoriteService,
        favorite_repo: FakeFavoriteRepository,
        palette_repo: FakePaletteRepository,
    ) -> None:
        palette = await _seed_palette(palette_repo)

        favorite = await service.favorite_palette(user_id=7, palette_id=palette.id)

        assert favorite.user_id == 7
        assert favorite.palette_id == palette.id
        assert favorite.created_at is not None
        assert await favorite_repo.exists(7, palette.id) is True

    async def test_favoriting_twice_is_idempotent(
        self, service: FavoriteService, palette_repo: FakePaletteRepository
    ) -> None:
        palette = await _seed_palette(palette_repo)
        await service.favorite_palette(user_id=7, palette_id=palette.id)

        # Documents the service's actual (slightly odd) behavior: the
        # already-favorited branch returns a synthetic, non-persisted
        # Favorite with created_at=None instead of the original record.
        second = await service.favorite_palette(user_id=7, palette_id=palette.id)

        assert second.created_at is None


class TestUnfavoritePalette:
    async def test_removes_an_existing_favorite(
        self,
        service: FavoriteService,
        favorite_repo: FakeFavoriteRepository,
        palette_repo: FakePaletteRepository,
    ) -> None:
        palette = await _seed_palette(palette_repo)
        await service.favorite_palette(user_id=7, palette_id=palette.id)

        await service.unfavorite_palette(user_id=7, palette_id=palette.id)

        assert await favorite_repo.exists(7, palette.id) is False

    async def test_is_a_no_op_when_not_favorited(
        self, service: FavoriteService
    ) -> None:
        await service.unfavorite_palette(user_id=7, palette_id=999)


class TestListFavorites:
    async def test_returns_own_favorites(
        self, service: FavoriteService, palette_repo: FakePaletteRepository
    ) -> None:
        palette = await _seed_palette(palette_repo)
        await service.favorite_palette(user_id=7, palette_id=palette.id)

        items, total = await service.list_favorites(user_id=7, requesting_user_id=7)

        assert total == 1
        assert items[0].palette.id == palette.id

    async def test_rejects_viewing_someone_elses_favorites(
        self, service: FavoriteService
    ) -> None:
        with pytest.raises(ForbiddenError):
            await service.list_favorites(user_id=7, requesting_user_id=8)


class TestIsFavorited:
    async def test_true_when_favorited(
        self, service: FavoriteService, palette_repo: FakePaletteRepository
    ) -> None:
        palette = await _seed_palette(palette_repo)
        await service.favorite_palette(user_id=7, palette_id=palette.id)

        assert await service.is_favorited(7, palette.id) is True

    async def test_false_when_not_favorited(self, service: FavoriteService) -> None:
        assert await service.is_favorited(7, 999) is False
