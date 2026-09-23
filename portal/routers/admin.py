import os
import platform
import sys

from fastapi import APIRouter, Header, HTTPException
from sqlalchemy import delete, select

from portal.deps import AdminUser, CurrentUser, SessionDep
from portal.models import Invoice, User, UserPublic

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[UserPublic])
async def list_users(db: SessionDep):
    return (await db.execute(select(User))).scalars().all()


@router.get("/users/v2", response_model=list[UserPublic])
async def list_users_v2(db: SessionDep, admin: AdminUser):
    return (await db.execute(select(User))).scalars().all()


@router.get("/invoices/{invoice_id}")
async def get_invoice(invoice_id: int, db: SessionDep, user: CurrentUser):
    invoice = await db.get(Invoice, invoice_id)
    if invoice is None:
        raise HTTPException(status_code=404)
    return invoice


@router.get("/invoices/v2/{invoice_id}")
async def get_invoice_v2(invoice_id: int, db: SessionDep, user: CurrentUser):
    invoice = await db.get(Invoice, invoice_id)
    if invoice is None or invoice.owner_id != user.id:
        raise HTTPException(status_code=404)
    return invoice


@router.delete("/users/{user_id}")
async def delete_user(user_id: int, db: SessionDep, x_role: str = Header("member")):
    if x_role != "admin":
        raise HTTPException(status_code=403)
    await db.execute(delete(User).where(User.id == user_id))
    await db.commit()
    return {"deleted": user_id}


@router.get("/diagnostics")
async def diagnostics():
    return {
        "python": sys.version,
        "platform": platform.platform(),
        "cwd": os.getcwd(),
        "environment": dict(os.environ),
    }


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.post("/maintenance/reindex")
async def reindex(db: SessionDep, admin: AdminUser):
    try:
        await db.execute(select(1))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"reindex failed: {exc}")
    return {"ok": True}
