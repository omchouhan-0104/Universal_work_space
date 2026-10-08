from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencie import get_current_user
from app.models.user import User


from app.database.session import get_db
from app.schemas.auth import (
    TokenResponse,
    UserLogin,
    UserRegister,
)
from app.services.auth_service import (
    authenticate_user,
    create_user_token,
    get_user_by_email,
    register_user,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
)
def register(
    user_data: UserRegister,
    db: Session = Depends(get_db),
):
    existing_user = get_user_by_email(
        db,
        user_data.email,
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = register_user(
        db=db,
        name=user_data.name,
        email=user_data.email,
        password=user_data.password,
    )

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "message": "User registered successfully",
    }


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    user_data: UserLogin,
    db: Session = Depends(get_db),
):
    user = authenticate_user(
        db=db,
        email=user_data.email,
        password=user_data.password,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_user_token(
        user
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
    
@router.get("/me")
def get_me(
    current_user: User = Depends(get_current_user),
):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "is_active": current_user.is_active,
    }