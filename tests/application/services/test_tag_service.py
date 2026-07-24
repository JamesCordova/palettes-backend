import pytest

from app.application.dtos.tag_dto import CreateTagDTO
from app.application.services.tag_service import TagService
from app.core.exceptions import ConflictError
from tests.fakes.tag_repository import FakeTagRepository


@pytest.fixture
def repo() -> FakeTagRepository:
    return FakeTagRepository()


@pytest.fixture
def service(repo: FakeTagRepository) -> TagService:
    return TagService(repo)


class TestCreateTag:
    async def test_creates_new_tag(self, service: TagService) -> None:
        tag = await service.create_tag(CreateTagDTO(name="pastel"))

        assert tag.id is not None
        assert tag.name == "pastel"

    async def test_rejects_duplicate_name(self, service: TagService) -> None:
        await service.create_tag(CreateTagDTO(name="pastel"))

        with pytest.raises(ConflictError):
            await service.create_tag(CreateTagDTO(name="pastel"))


class TestListTags:
    async def test_lists_created_tags(self, service: TagService) -> None:
        await service.create_tag(CreateTagDTO(name="pastel"))
        await service.create_tag(CreateTagDTO(name="vivid"))

        tags, total = await service.list_tags()

        assert total == 2
        assert {t.name for t in tags} == {"pastel", "vivid"}


class TestGetOrCreate:
    async def test_returns_existing_tag_without_creating_duplicate(
        self, service: TagService, repo: FakeTagRepository
    ) -> None:
        original = await service.create_tag(CreateTagDTO(name="pastel"))

        found = await service.get_or_create("pastel")

        assert found.id == original.id
        _, total = await repo.list()
        assert total == 1

    async def test_creates_tag_when_missing(self, service: TagService) -> None:
        created = await service.get_or_create("neon")

        assert created.id is not None
        assert created.name == "neon"


class TestDeleteTag:
    async def test_deletes_existing_tag(
        self, service: TagService, repo: FakeTagRepository
    ) -> None:
        tag = await service.create_tag(CreateTagDTO(name="pastel"))

        await service.delete_tag(tag.id)

        assert await repo.get_by_id(tag.id) is None

    async def test_is_a_no_op_for_missing_tag(self, service: TagService) -> None:
        # No existence check in the service — deleting an id that was never
        # there just does nothing, same as the underlying repository.
        await service.delete_tag(999)
