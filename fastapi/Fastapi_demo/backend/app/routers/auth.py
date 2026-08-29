import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import User
from ..schemas import LoginRequest, LoginResponse, UserOut
from ..security import create_access_token, verify_password

router = APIRouter()

logger = logging.getLogger("auth")


@router.post("/login", response_model=LoginResponse, summary="用户登录")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if user is None:
        logger.warning("登录失败 [用户不存在] username=%r", payload.username)
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if not verify_password(payload.password, user.password_hash):
        logger.warning(
            "登录失败 [密码错误] username=%r hash_len=%s hash_head=%r",
            payload.username,
            len(user.password_hash),
            user.password_hash[:25],
        )
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    token = create_access_token(str(user.id))
    return LoginResponse(
        access_token=token,
        user=UserOut.model_validate(user),
    )


@router.get("/me", response_model=UserOut, summary="获取当前登录用户")
def me(user: User = Depends(get_current_user)):
    return UserOut.model_validate(user)
