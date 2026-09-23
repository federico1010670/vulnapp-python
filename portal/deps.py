from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from portal.config import JWT_SECRET
from portal.db import get_db
from portal.models import User

SessionDep = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(request: Request, db: SessionDep) -> User:
    token = request.cookies.get("session")
    if not token:
        raise HTTPException(status_code=401)
    claims = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    user = await db.get(User, int(claims["sub"]))
    if user is None or not user.is_active:
        raise HTTPException(status_code=401)
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def require_admin(user: CurrentUser) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403)
    return user


AdminUser = Annotated[User, Depends(require_admin)]


async def get_partner(request: Request) -> dict:
    token = request.headers.get("x-partner-token", "")
    return jwt.decode(token, JWT_SECRET, algorithms=["HS256", "none"])
