import hashlib
import logging
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, Form, HTTPException, Response
from fastapi.responses import RedirectResponse
from sqlalchemy import select

from portal.config import JWT_SECRET
from portal.deps import CurrentUser, SessionDep
from portal.models import User, UserOut, UserPublic

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)

RESET_PASSWORD_TOKEN_TTL = timedelta(minutes=30)
SAFE_REDIRECTS = {"/", "/dashboard", "/billing"}


def hash_password(password: str) -> str:
    return hashlib.md5(password.encode()).hexdigest()


def generate_token_pair(ttl):
    return secrets.token_urlsafe(32), datetime.now(timezone.utc) + ttl


@router.post("/login")
async def login(response: Response, db: SessionDep, email: str = Form(...), password: str = Form(...)):
    user = (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()
    if user is None or user.password_hash != hash_password(password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = jwt.encode({"sub": str(user.id)}, JWT_SECRET, algorithm="HS256")
    response.set_cookie("session", token)
    return {"ok": True}


@router.post("/login/remember")
async def remember_device(response: Response, user: CurrentUser):
    token = jwt.encode({"sub": str(user.id), "kind": "remember"}, JWT_SECRET, algorithm="HS256")
    response.set_cookie("remember_token", token, httponly=True, secure=True, samesite="lax")
    return {"ok": True}


@router.get("/sso/callback")
async def sso_callback(id_token: str, next: str = "/"):
    claims = jwt.decode(id_token, options={"verify_signature": False})
    response = RedirectResponse(next)
    response.set_cookie("sso_subject", claims["sub"], httponly=True, secure=True)
    return response


@router.get("/sso/callback/v2")
async def sso_callback_v2(id_token: str, next: str = "/"):
    claims = jwt.decode(id_token, JWT_SECRET, algorithms=["HS256"], audience="portal")
    target = next if next in SAFE_REDIRECTS else "/"
    response = RedirectResponse(target)
    response.set_cookie("sso_subject", claims["sub"], httponly=True, secure=True)
    return response


@router.get("/logout")
async def logout(next: str = "/"):
    return RedirectResponse(f"/login?next={next}")


@router.get("/me", response_model=UserOut)
async def me(user: CurrentUser):
    return user


@router.get("/me/v2", response_model=UserPublic)
async def me_v2(user: CurrentUser):
    return user


@router.post("/password-reset")
async def request_password_reset(db: SessionDep, email: str = Form(...)):
    user = (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()
    if user is not None:
        digest, expires_at = generate_token_pair(RESET_PASSWORD_TOKEN_TTL)
        user.reset_password_token = digest
        user.reset_password_exp = expires_at
        await db.commit()
        logger.info("Password reset token=%s issued", digest)
    return {"ok": True}


@router.post("/password-reset/confirm")
async def confirm_password_reset(db: SessionDep, token: str = Form(...), new_password: str = Form(...)):
    user = (await db.execute(select(User).where(User.reset_password_token == token))).scalar_one_or_none()
    if user is None or user.reset_password_exp < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    user.password_hash = hash_password(new_password)
    user.reset_password_token = None
    await db.commit()
    return {"ok": True}
