# pyrefly: ignore [missing-import]
from app.core.security import verify_password
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
# pyrefly: ignore [missing-import]
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import UserCreate,UserLogin
from app.core.security import hash_password
from app.core.security import create_access_token


class AuthService:

    def register_user(self, db: Session, user_data: UserCreate):
        statement = select(User).where(
            User.email == user_data.email
        )

        existing_user = db.execute(statement).scalar_one_or_none()

        if existing_user:
            return{
                "status_code":400,  
                "message":"Email already exists"
            }

        hashed_password = hash_password(user_data.password)
        user = User(
            name=user_data.name,
            email=user_data.email,
            password=hashed_password
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return {
            "status_code":200,
            "message": "User registered successfully"
        }

    def login_user(self,db:Session,user_data:UserLogin):

        statement = select(User).where(
            User.email == user_data.email
        )

        existing_user = db.execute(statement).scalar_one_or_none()

        if not existing_user:
            return{
                "status_code":401,
                "message":"Invalid credentials"
            }

        check_pass = verify_password(user_data.password, existing_user.password)
        if not check_pass:
            return {
                "status_code": 401,
                "message": "Invalid credentials"
            }

        access_token = create_access_token(existing_user.id)
        return {
            "status_code": 200,
            "message": "Login successful",
            "access_token": access_token,
            "token_type": "bearer"
        }
        
        