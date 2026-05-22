from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import User
from app.schemas.schemas import UserResponse, PasswordChange
from app.utils.security import verify_password, hash_password
from app.utils.deps import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


@router.get("/", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    users = db.scalars(select(User)).all()
    return [UserResponse.model_validate(u) for u in users]


@router.patch("/me/password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
        data: PasswordChange,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if not verify_password(data.old_password, current_user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong password")

    current_user.password_hash = hash_password(data.new_password)
    db.commit()