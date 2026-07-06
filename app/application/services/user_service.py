from passlib.context import CryptContext

from app.application.dtos.user_dto import ChangePasswordDTO, CreateUserDTO, UpdateUserDTO
from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError, UnauthorizedError
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

    async def authenticate(self, identifier: str, password: str) -> User:
        user = await self._user_repository.get_by_username(identifier)
        if user is None:
            user = await self._user_repository.get_by_email(identifier)
        if user is None or not _pwd_context.verify(password, user.password_hash):
            raise UnauthorizedError("Invalid username/email or password")
        return user

    async def get_profile(self, user_id: int) -> User:
        user = await self._user_repository.get_by_id(user_id)
        if user is None:
            raise NotFoundError(f"User {user_id} not found")
        return user

    async def update_profile(
        self, user_id: int, requesting_user_id: int, dto: UpdateUserDTO
    ) -> User:
        self._require_self(user_id, requesting_user_id)
        user = await self.get_profile(user_id)
        user.username = dto.username
        user.email = dto.email
        user.avatar_url = dto.avatar_url
        return await self._user_repository.update(user)

    async def change_password(
        self, user_id: int, requesting_user_id: int, dto: ChangePasswordDTO
    ) -> None:
        self._require_self(user_id, requesting_user_id)
        user = await self.get_profile(user_id)
        if not _pwd_context.verify(dto.old_password, user.password_hash):
            raise UnauthorizedError("Current password is incorrect")
        await self._user_repository.update_password_hash(
            user_id, _pwd_context.hash(dto.new_password)
        )

    async def delete_account(self, user_id: int, requesting_user_id: int) -> None:
        self._require_self(user_id, requesting_user_id)
        await self._user_repository.delete(user_id)

    async def is_username_available(self, username: str) -> bool:
        return await self._user_repository.get_by_username(username) is None

    async def is_email_available(self, email: str) -> bool:
        return await self._user_repository.get_by_email(email) is None

    def _require_self(self, user_id: int, requesting_user_id: int) -> None:
        if user_id != requesting_user_id:
            raise ForbiddenError(f"User {requesting_user_id} cannot act on user {user_id}")
