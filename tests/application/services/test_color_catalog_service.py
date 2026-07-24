from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.application.dtos.color_catalog_dto import UpdateColorNameDTO
from app.application.services.color_catalog_service import ColorCatalogService
from app.core.exceptions import NotFoundError
from app.domain.entities.color_catalog import ColorCatalog
from tests.fakes.color_catalog_repository import FakeColorCatalogRepository


def make_color(
    hex_code: str, hue: int, usage_count: int = 0, name: str | None = None
) -> ColorCatalog:
    return ColorCatalog(
        hex_code=hex_code,
        hue=hue,
        saturation=50,
        lightness=50,
        luminance=Decimal("128.00"),
        usage_count=usage_count,
        created_at=datetime.now(UTC),
        name=name,
    )


@pytest.fixture
def repo() -> FakeColorCatalogRepository:
    return FakeColorCatalogRepository()


@pytest.fixture
def service(repo: FakeColorCatalogRepository) -> ColorCatalogService:
    return ColorCatalogService(repo)


class TestGetColor:
    async def test_returns_existing_color(
        self, service: ColorCatalogService, repo: FakeColorCatalogRepository
    ) -> None:
        await repo.upsert(make_color("#FF0000", hue=0))

        color = await service.get_color("#FF0000")

        assert color.hex_code == "#FF0000"

    async def test_raises_not_found_for_missing_color(
        self, service: ColorCatalogService
    ) -> None:
        with pytest.raises(NotFoundError):
            await service.get_color("#000000")


class TestRenameColor:
    async def test_renames_existing_color(
        self, service: ColorCatalogService, repo: FakeColorCatalogRepository
    ) -> None:
        await repo.upsert(make_color("#FF0000", hue=0))

        renamed = await service.rename_color(
            "#FF0000", UpdateColorNameDTO(name="Fire Engine")
        )

        assert renamed.name == "Fire Engine"

    async def test_raises_not_found_for_missing_color(
        self, service: ColorCatalogService
    ) -> None:
        with pytest.raises(NotFoundError):
            await service.rename_color("#000000", UpdateColorNameDTO(name="Void"))


class TestBrowseByHue:
    async def test_filters_to_hue_range(
        self, service: ColorCatalogService, repo: FakeColorCatalogRepository
    ) -> None:
        await repo.upsert(make_color("#RED", hue=10))
        await repo.upsert(make_color("#GREEN", hue=120))
        await repo.upsert(make_color("#BLUE", hue=240))

        colors, total = await service.browse_by_hue(0, 60)

        assert total == 1
        assert [c.hex_code for c in colors] == ["#RED"]


class TestMostUsed:
    async def test_orders_by_usage_count_descending(
        self, service: ColorCatalogService, repo: FakeColorCatalogRepository
    ) -> None:
        await repo.upsert(make_color("#LOW", hue=0, usage_count=1))
        await repo.upsert(make_color("#HIGH", hue=0, usage_count=99))

        colors, total = await service.most_used()

        assert total == 2
        assert [c.hex_code for c in colors] == ["#HIGH", "#LOW"]
