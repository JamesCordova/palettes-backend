import pytest

from app.application.dtos.palette_color_dto import (
    AddPaletteColorDTO,
    ReorderPaletteColorDTO,
    UpdatePaletteColorDTO,
)
from app.application.dtos.palette_dto import (
    CreatePaletteDTO,
    ForkPaletteDTO,
    UpdatePaletteDTO,
)
from app.application.services.palette_service import PaletteService
from app.core.exceptions import ForbiddenError, NotFoundError
from app.domain.entities.tag import Tag
from tests.fakes.color_catalog_repository import FakeColorCatalogRepository
from tests.fakes.palette_color_repository import FakePaletteColorRepository
from tests.fakes.palette_repository import FakePaletteRepository
from tests.fakes.tag_repository import FakeTagRepository

OWNER_ID = 1
OTHER_USER_ID = 2


@pytest.fixture
def palette_color_repo() -> FakePaletteColorRepository:
    return FakePaletteColorRepository()


@pytest.fixture
def tag_repo() -> FakeTagRepository:
    return FakeTagRepository()


@pytest.fixture
def palette_repo(
    palette_color_repo: FakePaletteColorRepository, tag_repo: FakeTagRepository
) -> FakePaletteRepository:
    return FakePaletteRepository(palette_color_repo, tag_repo)


@pytest.fixture
def color_catalog_repo() -> FakeColorCatalogRepository:
    return FakeColorCatalogRepository()


@pytest.fixture
def service(
    palette_repo: FakePaletteRepository,
    palette_color_repo: FakePaletteColorRepository,
    color_catalog_repo: FakeColorCatalogRepository,
    tag_repo: FakeTagRepository,
) -> PaletteService:
    return PaletteService(
        palette_repo, palette_color_repo, color_catalog_repo, tag_repo
    )


async def _create_palette(
    service: PaletteService, is_public: bool = True, user_id: int = OWNER_ID
):
    return await service.create_palette(
        user_id,
        CreatePaletteDTO(name="Sunset", description="Warm tones", is_public=is_public),
    )


def _add_color_dto(
    hex_code: str = "#FF5733", position: int | None = None
) -> AddPaletteColorDTO:
    return AddPaletteColorDTO(
        hex_code=hex_code,
        hue=10,
        saturation=50,
        lightness=50,
        luminance=128.0,
        position=position,
    )


class TestCreatePalette:
    async def test_creates_palette_owned_by_user(self, service: PaletteService) -> None:
        palette = await service.create_palette(
            OWNER_ID, CreatePaletteDTO(name="Sunset", is_public=True)
        )

        assert palette.id is not None
        assert palette.user_id == OWNER_ID
        assert palette.name == "Sunset"


class TestGetPalette:
    async def test_returns_public_palette_to_anyone(
        self, service: PaletteService
    ) -> None:
        palette = await _create_palette(service, is_public=True)

        found = await service.get_palette(palette.id, requesting_user_id=None)

        assert found.id == palette.id

    async def test_returns_private_palette_to_owner(
        self, service: PaletteService
    ) -> None:
        palette = await _create_palette(service, is_public=False)

        found = await service.get_palette(palette.id, requesting_user_id=OWNER_ID)

        assert found.id == palette.id

    async def test_rejects_private_palette_for_non_owner(
        self, service: PaletteService
    ) -> None:
        palette = await _create_palette(service, is_public=False)

        with pytest.raises(ForbiddenError):
            await service.get_palette(palette.id, requesting_user_id=OTHER_USER_ID)

    async def test_raises_not_found_for_missing_palette(
        self, service: PaletteService
    ) -> None:
        with pytest.raises(NotFoundError):
            await service.get_palette(999, requesting_user_id=None)


class TestGetPaletteWithColors:
    async def test_returns_palette_and_its_colors(
        self, service: PaletteService
    ) -> None:
        palette = await _create_palette(service)
        await service.add_color(palette.id, OWNER_ID, _add_color_dto())

        found, colors = await service.get_palette_with_colors(palette.id, OWNER_ID)

        assert found.id == palette.id
        assert len(colors) == 1

    async def test_rejects_private_palette_for_non_owner(
        self, service: PaletteService
    ) -> None:
        palette = await _create_palette(service, is_public=False)

        with pytest.raises(ForbiddenError):
            await service.get_palette_with_colors(palette.id, OTHER_USER_ID)


class TestUpdatePalette:
    async def test_owner_can_update(self, service: PaletteService) -> None:
        palette = await _create_palette(service)

        updated = await service.update_palette(
            palette.id, OWNER_ID, UpdatePaletteDTO(name="New name", is_public=False)
        )

        assert updated.name == "New name"
        assert updated.is_public is False

    async def test_non_owner_cannot_update(self, service: PaletteService) -> None:
        palette = await _create_palette(service)

        with pytest.raises(ForbiddenError):
            await service.update_palette(
                palette.id, OTHER_USER_ID, UpdatePaletteDTO(name="Hijacked")
            )

    async def test_raises_not_found_for_missing_palette(
        self, service: PaletteService
    ) -> None:
        with pytest.raises(NotFoundError):
            await service.update_palette(999, OWNER_ID, UpdatePaletteDTO(name="x"))


class TestDeletePalette:
    async def test_owner_can_delete(
        self, service: PaletteService, palette_repo: FakePaletteRepository
    ) -> None:
        palette = await _create_palette(service)

        await service.delete_palette(palette.id, OWNER_ID)

        assert await palette_repo.get_by_id(palette.id) is None

    async def test_non_owner_cannot_delete(self, service: PaletteService) -> None:
        palette = await _create_palette(service)

        with pytest.raises(ForbiddenError):
            await service.delete_palette(palette.id, OTHER_USER_ID)


class TestForkPalette:
    async def test_forks_a_public_palette(self, service: PaletteService) -> None:
        original = await _create_palette(service, is_public=True)

        forked = await service.fork_palette(
            original.id, OTHER_USER_ID, ForkPaletteDTO(name="My remix")
        )

        assert forked.id != original.id
        assert forked.user_id == OTHER_USER_ID
        assert forked.forked_from == original.id
        assert forked.name == "My remix"

    async def test_rejects_forking_a_private_palette_you_dont_own(
        self, service: PaletteService
    ) -> None:
        original = await _create_palette(service, is_public=False)

        with pytest.raises(ForbiddenError):
            await service.fork_palette(original.id, OTHER_USER_ID, ForkPaletteDTO())


class TestAddColor:
    async def test_adds_color_and_upserts_catalog_entry(
        self,
        service: PaletteService,
        color_catalog_repo: FakeColorCatalogRepository,
    ) -> None:
        palette = await _create_palette(service)

        color = await service.add_color(palette.id, OWNER_ID, _add_color_dto("#FF5733"))

        assert color.id is not None
        assert color.hex_code == "#FF5733"
        assert color.position == 1
        assert await color_catalog_repo.get_by_hex("#FF5733") is not None

    async def test_auto_assigns_next_position_when_omitted(
        self, service: PaletteService
    ) -> None:
        palette = await _create_palette(service)
        await service.add_color(palette.id, OWNER_ID, _add_color_dto("#111111"))

        second = await service.add_color(
            palette.id, OWNER_ID, _add_color_dto("#222222")
        )

        assert second.position == 2

    async def test_respects_explicit_position(self, service: PaletteService) -> None:
        palette = await _create_palette(service)

        color = await service.add_color(
            palette.id, OWNER_ID, _add_color_dto("#FF5733", position=5)
        )

        assert color.position == 5

    async def test_non_owner_cannot_add_color(self, service: PaletteService) -> None:
        palette = await _create_palette(service)

        with pytest.raises(ForbiddenError):
            await service.add_color(palette.id, OTHER_USER_ID, _add_color_dto())


class TestUpdateColor:
    async def test_owner_can_update_color_hex(self, service: PaletteService) -> None:
        palette = await _create_palette(service)
        color = await service.add_color(palette.id, OWNER_ID, _add_color_dto("#FF5733"))

        updated = await service.update_color(
            palette.id,
            OWNER_ID,
            color.id,
            UpdatePaletteColorDTO(
                hex_code="#00FF00",
                hue=120,
                saturation=100,
                lightness=50,
                luminance=200.0,
            ),
        )

        assert updated.hex_code == "#00FF00"
        # Position is carried over from the existing row, not reset.
        assert updated.position == color.position

    async def test_raises_not_found_when_color_belongs_to_different_palette(
        self, service: PaletteService
    ) -> None:
        palette_a = await _create_palette(service)
        palette_b = await service.create_palette(
            OWNER_ID, CreatePaletteDTO(name="Other")
        )
        color = await service.add_color(palette_a.id, OWNER_ID, _add_color_dto())

        with pytest.raises(NotFoundError):
            await service.update_color(
                palette_b.id,
                OWNER_ID,
                color.id,
                UpdatePaletteColorDTO(
                    hex_code="#00FF00",
                    hue=120,
                    saturation=100,
                    lightness=50,
                    luminance=200.0,
                ),
            )

    async def test_non_owner_cannot_update_color(self, service: PaletteService) -> None:
        palette = await _create_palette(service)
        color = await service.add_color(palette.id, OWNER_ID, _add_color_dto())

        with pytest.raises(ForbiddenError):
            await service.update_color(
                palette.id,
                OTHER_USER_ID,
                color.id,
                UpdatePaletteColorDTO(
                    hex_code="#00FF00",
                    hue=120,
                    saturation=100,
                    lightness=50,
                    luminance=200.0,
                ),
            )


class TestRemoveColor:
    async def test_owner_can_remove_color(
        self, service: PaletteService, palette_color_repo: FakePaletteColorRepository
    ) -> None:
        palette = await _create_palette(service)
        color = await service.add_color(palette.id, OWNER_ID, _add_color_dto())

        await service.remove_color(palette.id, OWNER_ID, color.id)

        assert await palette_color_repo.get_by_id(color.id) is None

    async def test_non_owner_cannot_remove_color(self, service: PaletteService) -> None:
        palette = await _create_palette(service)
        color = await service.add_color(palette.id, OWNER_ID, _add_color_dto())

        with pytest.raises(ForbiddenError):
            await service.remove_color(palette.id, OTHER_USER_ID, color.id)

    async def test_does_not_verify_the_color_belongs_to_the_palette(
        self, service: PaletteService, palette_color_repo: FakePaletteColorRepository
    ) -> None:
        # Documents an existing gap: unlike update_color, remove_color only
        # checks that the CALLER owns `palette_id` — it never confirms
        # `palette_color_id` actually belongs to that palette. Owning any
        # palette is enough to delete any color row by id.
        palette_a = await _create_palette(service)
        palette_b = await service.create_palette(
            OWNER_ID, CreatePaletteDTO(name="Other")
        )
        color_in_b = await service.add_color(palette_b.id, OWNER_ID, _add_color_dto())

        await service.remove_color(palette_a.id, OWNER_ID, color_in_b.id)

        assert await palette_color_repo.get_by_id(color_in_b.id) is None


class TestReorderColors:
    async def test_owner_can_reorder_colors(self, service: PaletteService) -> None:
        palette = await _create_palette(service)
        first = await service.add_color(palette.id, OWNER_ID, _add_color_dto("#111111"))
        second = await service.add_color(
            palette.id, OWNER_ID, _add_color_dto("#222222")
        )

        reordered = await service.reorder_colors(
            palette.id,
            OWNER_ID,
            ReorderPaletteColorDTO(ordered_ids=[second.id, first.id]),
        )

        assert [c.id for c in reordered] == [second.id, first.id]

    async def test_non_owner_cannot_reorder(self, service: PaletteService) -> None:
        palette = await _create_palette(service)

        with pytest.raises(ForbiddenError):
            await service.reorder_colors(
                palette.id, OTHER_USER_ID, ReorderPaletteColorDTO(ordered_ids=[])
            )


class TestTags:
    async def test_owner_can_add_and_list_tags(
        self, service: PaletteService, tag_repo: FakeTagRepository
    ) -> None:
        palette = await _create_palette(service)
        tag = await tag_repo.create(Tag(id=None, name="pastel"))

        await service.add_tag(palette.id, OWNER_ID, tag.id)
        tags = await service.list_tags(palette.id)

        assert [t.name for t in tags] == ["pastel"]

    async def test_owner_can_remove_tag(
        self, service: PaletteService, tag_repo: FakeTagRepository
    ) -> None:
        palette = await _create_palette(service)
        tag = await tag_repo.create(Tag(id=None, name="pastel"))
        await service.add_tag(palette.id, OWNER_ID, tag.id)

        await service.remove_tag(palette.id, OWNER_ID, tag.id)

        assert await service.list_tags(palette.id) == []

    async def test_non_owner_cannot_add_tag(
        self, service: PaletteService, tag_repo: FakeTagRepository
    ) -> None:
        palette = await _create_palette(service)
        tag = await tag_repo.create(Tag(id=None, name="pastel"))

        with pytest.raises(ForbiddenError):
            await service.add_tag(palette.id, OTHER_USER_ID, tag.id)

    async def test_list_tags_has_no_ownership_check(
        self, service: PaletteService, tag_repo: FakeTagRepository
    ) -> None:
        palette = await _create_palette(service, is_public=False)
        tag = await tag_repo.create(Tag(id=None, name="pastel"))
        await service.add_tag(palette.id, OWNER_ID, tag.id)

        # Public info about a palette's tags, readable regardless of who's
        # asking — no requesting_user_id parameter on this method at all.
        tags = await service.list_tags(palette.id)

        assert [t.name for t in tags] == ["pastel"]


class TestListingPalettes:
    async def test_list_public_palettes_only_returns_public_ones(
        self, service: PaletteService
    ) -> None:
        await _create_palette(service, is_public=True)
        await _create_palette(service, is_public=False)

        items, total = await service.list_public_palettes()

        assert total == 1
        assert items[0].palette.is_public is True

    async def test_list_public_palettes_includes_color_count(
        self, service: PaletteService
    ) -> None:
        palette = await _create_palette(service, is_public=True)
        await service.add_color(palette.id, OWNER_ID, _add_color_dto("#111111"))
        await service.add_color(palette.id, OWNER_ID, _add_color_dto("#222222"))

        items, _total = await service.list_public_palettes()

        assert items[0].color_count == 2
        assert len(items[0].colors) == 2

    async def test_list_user_palettes_hides_private_from_others(
        self, service: PaletteService
    ) -> None:
        await _create_palette(service, is_public=True, user_id=OWNER_ID)
        await _create_palette(service, is_public=False, user_id=OWNER_ID)

        items, total = await service.list_user_palettes(
            OWNER_ID, requesting_user_id=OTHER_USER_ID
        )

        assert total == 1
        assert items[0].palette.is_public is True

    async def test_list_user_palettes_shows_private_to_owner(
        self, service: PaletteService
    ) -> None:
        await _create_palette(service, is_public=True, user_id=OWNER_ID)
        await _create_palette(service, is_public=False, user_id=OWNER_ID)

        items, total = await service.list_user_palettes(
            OWNER_ID, requesting_user_id=OWNER_ID
        )

        assert total == 2

    async def test_search_public_palettes_matches_by_name(
        self, service: PaletteService
    ) -> None:
        await service.create_palette(OWNER_ID, CreatePaletteDTO(name="Sunset Beach"))
        await service.create_palette(OWNER_ID, CreatePaletteDTO(name="Forest"))

        items, total = await service.search_public_palettes("sunset")

        assert total == 1
        assert items[0].palette.name == "Sunset Beach"

    async def test_list_public_palettes_by_tag(
        self, service: PaletteService, tag_repo: FakeTagRepository
    ) -> None:
        matching = await _create_palette(service, is_public=True)
        await _create_palette(service, is_public=True)
        tag = await tag_repo.create(Tag(id=None, name="pastel"))
        await service.add_tag(matching.id, OWNER_ID, tag.id)

        items, total = await service.list_public_palettes_by_tag(tag.id)

        assert total == 1
        assert items[0].palette.id == matching.id
