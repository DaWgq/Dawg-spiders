from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .database import get_db
from .models import User
from .security import decode_token

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """从请求头 Authorization 中解析当前登录用户"""
    if credentials is None:
        raise HTTPException(status_code=401, detail="未登录或登录已过期")
    user_id = decode_token(credentials.credentials)
    if user_id is None:
        raise HTTPException(status_code=401, detail="登录状态无效或已过期")
    user = db.get(User, int(user_id))
    if user is None:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user
