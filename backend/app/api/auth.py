from app.dependencies import get_current_user
from fastapi import APIRouter, Depends
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.user import UserCreate, UserLogin
from app.services.auth_service import AuthService
from fastapi.security import OAuth2PasswordRequestForm
from app.models.user import User
from app.core.config import settings

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

auth_service= AuthService()

@router.post("/register")
def register(
    user:UserCreate,
    db:Session=Depends(get_db)
):
     return auth_service.register_user(db,user)

@router.post("/login")
def Login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db:Session=Depends(get_db)
):
    user_data = UserLogin(
        email=form_data.username,
        password=form_data.password
    )

    return auth_service.login_user(db, user_data)

@router.api_route("/me", methods=["GET", "POST"])
def get_me(
    current_user: User = Depends(get_current_user)
):
    return{
        "id":current_user.id,
        "name":current_user.name,
        "email":current_user.email,
        "is_admin": current_user.email == settings.ADMIN_EMAIL
    }