import pytest
from passlib.context import CryptContext

import app.application.services.user_service as user_service_module
from app.application.dtos.user_dto import (
    ChangePasswordDTO,
    CreateUserDTO,
    UpdateUserDTO,
)
from app.application.services.user_service import UserService
from app.core.exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
)
from app.domain.entities.user import User
from tests.fakes.user_repository import FakeUserRepository


@pytest.fixture(autouse=True)
def fast_bcrypt(monkeypatch: pytest.MonkeyPatch) -> None:
    # The real _pwd_context uses passlib's default bcrypt rounds (12, ~200ms
    # per hash) — a module-level singleton, not injected, so it has to be
    # monkeypatched rather than swapped via a constructor argument. 4 rounds
    # keeps register/authenticate/change_password tests fast without
    # changing what they're actually verifying (hash-then-verify roundtrip).
    monkeypatch.setattr(
        user_service_module,
        "_pwd_context",
        CryptContext(schemes=["bcrypt"], bcrypt__rounds=4),
    )


@pytest.fixture
def repo() -> FakeUserRepository:
    return FakeUserRepository()


@pytest.fixture
def service(repo: FakeUserRepository) -> UserService:
    return UserService(repo)


async def _seed_user(repo: FakeUserRepository, **overrides: object) -> User:
    defaults: dict[str, object] = {
        "username": "alice",
        "email": "alice@example.com",
        "password": "correct horse",
    }
    defaults.update(overrides)
    service = UserService(repo)
    return await service.register(CreateUserDTO(**defaults))


class TestRegister:
    async def test_creates_user_with_hashed_password_and_id(
        self, service: UserService, repo: FakeUserRepository
    ) -> None:
        user = await service.register(
            CreateUserDTO(
                username="alice", email="alice@example.com", password="secret123"
            )
        )

        assert user.id is not None
        assert user.username == "alice"
        assert user.password_hash != "secret123"
        assert await repo.get_by_id(user.id) == user

    async def test_rejects_duplicate_username(
        self, service: UserService, repo: FakeUserRepository
    ) -> None:
        await _seed_user(repo, username="alice", email="alice@example.com")

        with pytest.raises(ConflictError):
            await service.register(
                CreateUserDTO(
                    username="alice", email="different@example.com", password="x"
                )
            )

    async def test_rejects_duplicate_email(
        self, service: UserService, repo: FakeUserRepository
    ) -> None:
        await _seed_user(repo, username="alice", email="alice@example.com")

        with pytest.raises(ConflictError):
            await service.register(
                CreateUserDTO(
                    username="different", email="alice@example.com", password="x"
                )
            )


class TestAuthenticate:
    async def test_succeeds_with_username_and_correct_password(
        self, service: UserService, repo: FakeUserRepository
    ) -> None:
        created = await _seed_user(repo, password="correct horse")

        authenticated = await service.authenticate("alice", "correct horse")

        assert authenticated.id == created.id

    async def test_succeeds_with_email_as_identifier(
        self, service: UserService, repo: FakeUserRepository
    ) -> None:
        created = await _seed_user(repo, password="correct horse")

        authenticated = await service.authenticate("alice@example.com", "correct horse")

        assert authenticated.id == created.id

    async def test_rejects_unknown_identifier(self, service: UserService) -> None:
        with pytest.raises(UnauthorizedError):
            await service.authenticate("nobody", "whatever")

    async def test_rejects_wrong_password(
        self, service: UserService, repo: FakeUserRepository
    ) -> None:
        await _seed_user(repo, password="correct horse")

        with pytest.raises(UnauthorizedError):
            await service.authenticate("alice", "wrong password")


class TestGetProfile:
    async def test_returns_existing_user(
        self, service: UserService, repo: FakeUserRepository
    ) -> None:
        created = await _seed_user(repo)

        assert (await service.get_profile(created.id)).id == created.id

    async def test_raises_not_found_for_missing_user(
        self, service: UserService
    ) -> None:
        with pytest.raises(NotFoundError):
            await service.get_profile(999)


class TestUpdateProfile:
    async def test_updates_own_profile(
        self, service: UserService, repo: FakeUserRepository
    ) -> None:
        created = await _seed_user(repo)

        updated = await service.update_profile(
            created.id,
            created.id,
            UpdateUserDTO(
                username="alice2", email="alice2@example.com", avatar_url="a.png"
            ),
        )

        assert updated.username == "alice2"
        assert updated.email == "alice2@example.com"
        assert updated.avatar_url == "a.png"

    async def test_rejects_updating_someone_else(
        self, service: UserService, repo: FakeUserRepository
    ) -> None:
        created = await _seed_user(repo)

        with pytest.raises(ForbiddenError):
            await service.update_profile(
                created.id,
                created.id + 1,
                UpdateUserDTO(username="mallory", email="mallory@example.com"),
            )


class TestChangePassword:
    async def test_changes_password_with_correct_current_password(
        self, service: UserService, repo: FakeUserRepository
    ) -> None:
        created = await _seed_user(repo, password="old-password")

        await service.change_password(
            created.id,
            created.id,
            ChangePasswordDTO(old_password="old-password", new_password="new-password"),
        )

        # The new password authenticates; the old one no longer does.
        await service.authenticate("alice", "new-password")
        with pytest.raises(UnauthorizedError):
            await service.authenticate("alice", "old-password")

    async def test_rejects_wrong_current_password(
        self, service: UserService, repo: FakeUserRepository
    ) -> None:
        created = await _seed_user(repo, password="old-password")

        with pytest.raises(UnauthorizedError):
            await service.change_password(
                created.id,
                created.id,
                ChangePasswordDTO(old_password="not-it", new_password="new-password"),
            )

    async def test_rejects_changing_someone_elses_password(
        self, service: UserService, repo: FakeUserRepository
    ) -> None:
        created = await _seed_user(repo, password="old-password")

        with pytest.raises(ForbiddenError):
            await service.change_password(
                created.id,
                created.id + 1,
                ChangePasswordDTO(
                    old_password="old-password", new_password="new-password"
                ),
            )


class TestDeleteAccount:
    async def test_deletes_own_account(
        self, service: UserService, repo: FakeUserRepository
    ) -> None:
        created = await _seed_user(repo)

        await service.delete_account(created.id, created.id)

        assert await repo.get_by_id(created.id) is None

    async def test_rejects_deleting_someone_elses_account(
        self, service: UserService, repo: FakeUserRepository
    ) -> None:
        created = await _seed_user(repo)

        with pytest.raises(ForbiddenError):
            await service.delete_account(created.id, created.id + 1)

        assert await repo.get_by_id(created.id) is not None


class TestAvailability:
    async def test_username_available_when_unused(self, service: UserService) -> None:
        assert await service.is_username_available("nobody") is True

    async def test_username_unavailable_when_taken(
        self, service: UserService, repo: FakeUserRepository
    ) -> None:
        await _seed_user(repo, username="alice")

        assert await service.is_username_available("alice") is False

    async def test_email_available_when_unused(self, service: UserService) -> None:
        assert await service.is_email_available("nobody@example.com") is True

    async def test_email_unavailable_when_taken(
        self, service: UserService, repo: FakeUserRepository
    ) -> None:
        await _seed_user(repo, email="alice@example.com")

        assert await service.is_email_available("alice@example.com") is False
