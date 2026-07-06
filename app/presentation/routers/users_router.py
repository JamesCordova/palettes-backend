from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.application.dtos.user_dto import ChangePasswordDTO, CreateUserDTO, UpdateUserDTO
from app.application.services.user_service import UserService
from app.presentation.dependencies import get_current_user_id, get_user_service
from app.presentation.schemas.user_schema import (
    ChangePasswordRequest,
    UserAvailability,
    UserCreate,
    UserRead,
    UserUpdate,
)

router = APIRouter(prefix="/users", tags=["users"])

UserServiceDep = Annotated[UserService, Depends(get_user_service)]
CurrentUserIdDep = Annotated[int, Depends(get_current_user_id)]


@router.get("/availability", response_model=UserAvailability)
async def check_availability(
    service: UserServiceDep,
    username: str | None = None,
    email: str | None = None,
) -> UserAvailability:
    return UserAvailability(
        username_available=(
            await service.is_username_available(username) if username is not None else None
        ),
        email_available=(
            await service.is_email_available(email) if email is not None else None
        ),
    )


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(payload: UserCreate, service: UserServiceDep) -> UserRead:
    user = await service.register(
        CreateUserDTO(
            username=payload.username,
            email=payload.email,
            password=payload.password,
            avatar_url=payload.avatar_url,
        )
    )
    return UserRead.model_validate(user)


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int, service: UserServiceDep) -> UserRead:
    user = await service.get_profile(user_id)
    return UserRead.model_validate(user)


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    payload: UserUpdate,
    service: UserServiceDep,
    current_user_id: CurrentUserIdDep,
) -> UserRead:
    user = await service.update_profile(
        user_id,
        current_user_id,
        UpdateUserDTO(
            username=payload.username, email=payload.email, avatar_url=payload.avatar_url
        ),
    )
    return UserRead.model_validate(user)


@router.patch("/{user_id}/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    user_id: int,
    payload: ChangePasswordRequest,
    service: UserServiceDep,
    current_user_id: CurrentUserIdDep,
) -> None:
    await service.change_password(
        user_id,
        current_user_id,
        ChangePasswordDTO(old_password=payload.old_password, new_password=payload.new_password),
    )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int, service: UserServiceDep, current_user_id: CurrentUserIdDep
) -> None:
    await service.delete_account(user_id, current_user_id)
