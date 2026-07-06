from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.models.user_model import UserModel


def _to_entity(model: UserModel) -> User:
    return User(
        id=model.id,
        username=model.username,
        email=model.email,
        password_hash=model.password_hash,
        avatar_url=model.avatar_url,
        created_at=model.created_at,
    )


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: int) -> User | None:
        model = await self._session.get(UserModel, user_id)
        return _to_entity(model) if model else None

    async def get_by_username(self, username: str) -> User | None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.username == username)
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def get_by_email(self, email: str) -> User | None:
        result = await self._session.execute(select(UserModel).where(UserModel.email == email))
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def create(self, user: User) -> User:
        model = UserModel(
            username=user.username,
            email=user.email,
            password_hash=user.password_hash,
            avatar_url=user.avatar_url,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return _to_entity(model)

    async def update(self, user: User) -> User:
        model = await self._session.get(UserModel, user.id)
        if model is None:
            raise NotFoundError(f"User {user.id} not found")
        model.username = user.username
        model.email = user.email
        model.avatar_url = user.avatar_url
        await self._session.flush()
        await self._session.refresh(model)
        return _to_entity(model)

    async def update_password_hash(self, user_id: int, password_hash: str) -> None:
        model = await self._session.get(UserModel, user_id)
        if model is None:
            raise NotFoundError(f"User {user_id} not found")
        model.password_hash = password_hash
        await self._session.flush()

    async def delete(self, user_id: int) -> None:
        model = await self._session.get(UserModel, user_id)
        if model is None:
            raise NotFoundError(f"User {user_id} not found")
        await self._session.delete(model)
        await self._session.flush()

    async def list(self, limit: int = 50, offset: int = 0) -> list[User]:
        result = await self._session.execute(select(UserModel).limit(limit).offset(offset))
        return [_to_entity(model) for model in result.scalars().all()]
