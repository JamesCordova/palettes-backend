from app.application.dtos.tag_dto import CreateTagDTO
from app.core.exceptions import ConflictError
from app.domain.entities.tag import Tag
from app.domain.repositories.tag_repository import TagRepository


class TagService:
    def __init__(self, tag_repository: TagRepository) -> None:
        self._tag_repository = tag_repository

    async def create_tag(self, dto: CreateTagDTO) -> Tag:
        if await self._tag_repository.get_by_name(dto.name) is not None:
            raise ConflictError(f"Tag '{dto.name}' already exists")
        return await self._tag_repository.create(Tag(id=None, name=dto.name))

    async def list_tags(self) -> list[Tag]:
        return await self._tag_repository.list()

    async def get_or_create(self, name: str) -> Tag:
        tag = await self._tag_repository.get_by_name(name)
        if tag is not None:
            return tag
        return await self._tag_repository.create(Tag(id=None, name=name))

    async def delete_tag(self, tag_id: int) -> None:
        await self._tag_repository.delete(tag_id)
