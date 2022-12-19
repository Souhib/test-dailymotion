from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from api.controller.user import UserController
from api.dependencies import get_current_active_user, get_user_controller
from api.model.shared import Token
from api.model.user import UserView, UserCreate, User

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=UserView)
async def create_user(
    *,
    user_create: UserCreate,
    user_controller: UserController = Depends(get_user_controller),
) -> UserView:
    user = user_controller.create_user(user_create)
    return UserView(id=user.id, email_address=user.email_address)


@router.post("/activate")
async def activate_user(
    *,
    email_str: str,
    activation_code: str,
    user_controller: UserController = Depends(get_user_controller),
):
    user_controller.activate_user(email_str, activation_code)


@router.post("/login", response_model=Token)
def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        user_controller: UserController = Depends(get_user_controller)
) -> Token:
    return user_controller.login_user(form_data)


@router.get("/me", response_model=UserView)
def read_users_me(current_user: User = Depends(get_current_active_user)) -> UserView:
    return UserView(id=current_user.id, email_address=current_user.email_address)
