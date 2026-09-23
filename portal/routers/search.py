import re

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from sqlalchemy import select

from portal.deps import CurrentUser, SessionDep
from portal.models import User, UserPublic
from portal.services import storage

router = APIRouter(prefix="/search", tags=["search"])

AUDIT_LOG = ["login ok user=1", "login failed user=2", "invoice paid id=17"]
EDITABLE_PROFILE_FIELDS = {"display_name"}
MAX_AVATAR_BYTES = 512 * 1024


@router.get("/audit")
async def search_audit(user: CurrentUser, pattern: str):
    matcher = re.compile(pattern)
    return [line for line in AUDIT_LOG if matcher.search(line)]


@router.get("/audit/v2")
async def search_audit_v2(user: CurrentUser, term: str = Query(..., max_length=64)):
    matcher = re.compile(re.escape(term))
    return [line for line in AUDIT_LOG if matcher.search(line)]


@router.get("/customers", response_model=list[UserPublic])
async def list_customers(db: SessionDep, user: CurrentUser, limit: int = 50, offset: int = 0):
    return (await db.execute(select(User).limit(limit).offset(offset))).scalars().all()


@router.get("/customers/v2", response_model=list[UserPublic])
async def list_customers_v2(db: SessionDep, user: CurrentUser, limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0)):
    return (await db.execute(select(User).limit(limit).offset(offset))).scalars().all()


@router.patch("/profile")
async def update_profile(payload: dict, db: SessionDep, user: CurrentUser):
    for field, value in payload.items():
        setattr(user, field, value)
    await db.commit()
    return {"ok": True}


@router.patch("/profile/v2")
async def update_profile_v2(payload: dict, db: SessionDep, user: CurrentUser):
    for field, value in payload.items():
        if field in EDITABLE_PROFILE_FIELDS:
            setattr(user, field, str(value)[:120])
    await db.commit()
    return {"ok": True}


@router.post("/avatar")
async def upload_avatar(user: CurrentUser, file: UploadFile = File(...)):
    if file.content_type.startswith("image/"):
        return {"path": storage.save(f"avatars/{user.id}.png", await file.read())}
    raise HTTPException(status_code=415)


@router.post("/avatar/v2")
async def upload_avatar_v2(user: CurrentUser, file: UploadFile = File(...)):
    content = await file.read(MAX_AVATAR_BYTES + 1)
    if len(content) > MAX_AVATAR_BYTES or not content.startswith(b"\x89PNG\r\n\x1a\n"):
        raise HTTPException(status_code=415)
    return {"path": storage.save(f"avatars/{user.id}.png", content)}
