from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.application.services.user_service import UserService
from app.core.security import create_access_token
from app.presentation.dependencies import get_user_service
from app.presentation.schemas.auth_schema import TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])

UserServiceDep = Annotated[UserService, Depends(get_user_service)]


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], service: UserServiceDep
) -> TokenResponse:
    user = await service.authenticate(form_data.username, form_data.password)
    token = create_access_token(user.id)
    return TokenResponse(access_token=token)
