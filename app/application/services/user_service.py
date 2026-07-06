from passlib.context import CryptContext

from app.application.dtos.user_dto import CreateUserDTO, UpdateUserDTO
from app.core.exceptions import ConflictError, NotFoundError
from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repository = user_repository

    async def register(self, dto: CreateUserDTO) -> User:
        if await self._user_repository.get_by_username(dto.username) is not None:
            raise ConflictError(f"Username '{dto.username}' is already taken")
        if await self._user_repository.get_by_email(dto.email) is not None:
            raise ConflictError(f"Email '{dto.email}' is already registered")
        user = User(
            id=None,
            username=dto.username,
            email=dto.email,
            password_hash=_pwd_context.hash(dto.password),
            avatar_url=dto.avatar_url,
            created_at=None,
        )
        return await self._user_repository.create(user)

    async def get_profile(self, user_id: int) -> User:
        user = await self._user_repository.get_by_id(user_id)
        if user is None:
            raise NotFoundError(f"User {user_id} not found")
        return user

    async def update_profile(self, user_id: int, dto: UpdateUserDTO) -> User:
        user = await self.get_profile(user_id)
        user.username = dto.username
        user.email = dto.email
        user.avatar_url = dto.avatar_url
        return await self._user_repository.update(user)

    async def delete_account(self, user_id: int) -> None:
        await self._user_repository.delete(user_id)

    async def is_username_available(self, username: str) -> bool:
        return await self._user_repository.get_by_username(username) is None

    async def is_email_available(self, email: str) -> bool:
        return await self._user_repository.get_by_email(email) is None
