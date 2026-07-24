from dataclasses import replace
from datetime import UTC, datetime

from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository


class FakeUserRepository(UserRepository):
    """In-memory stand-in for the real SQLAlchemy repository, only faithful
    enough for the behavior UserService actually exercises (uniqueness
    lookups, id/created_at assignment on create)."""

    def __init__(self) -> None:
        self._users: dict[int, User] = {}
        self._next_id = 1

    async def get_by_id(self, user_id: int) -> User | None:
        return self._users.get(user_id)

    async def get_by_username(self, username: str) -> User | None:
        return next((u for u in self._users.values() if u.username == username), None)

    async def get_by_email(self, email: str) -> User | None:
        return next((u for u in self._users.values() if u.email == email), None)

    async def create(self, user: User) -> User:
        created = replace(user, id=self._next_id, created_at=datetime.now(UTC))
        self._users[created.id] = created
        self._next_id += 1
        return created

    async def update(self, user: User) -> User:
        self._users[user.id] = user
        return user

    async def update_password_hash(self, user_id: int, password_hash: str) -> None:
        self._users[user_id].password_hash = password_hash

    async def delete(self, user_id: int) -> None:
        self._users.pop(user_id, None)

    async def list(self, limit: int = 50, offset: int = 0) -> list[User]:
        return list(self._users.values())[offset : offset + limit]
