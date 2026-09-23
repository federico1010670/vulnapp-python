from fastapi import APIRouter, Query, Request
from sqlalchemy import select, text

from portal.deps import CurrentUser, SessionDep
from portal.models import Invoice
from portal.services import report_service

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/revenue")
async def revenue_report(db: SessionDep, user: CurrentUser, region: str = Query("emea"), sort: str = "region"):
    return await report_service.revenue_by_region(db, region, sort)


@router.get("/revenue/v2")
async def revenue_report_v2(db: SessionDep, user: CurrentUser, region: str = Query("emea"), sort: str = "region"):
    return await report_service.revenue_for_region(db, region, sort)


@router.get("/customers")
async def customer_lookup(db: SessionDep, user: CurrentUser, name: str):
    rows = await db.execute(text(f"SELECT id, email FROM users WHERE display_name LIKE '%{name}%'"))
    return [dict(row._mapping) for row in rows]


@router.get("/customers/v2")
async def customer_lookup_v2(db: SessionDep, user: CurrentUser, name: str):
    rows = await db.execute(
        text("SELECT id, email FROM users WHERE display_name LIKE :pattern"),
        {"pattern": f"%{name}%"},
    )
    return [dict(row._mapping) for row in rows]


@router.get("/invoices")
async def list_invoices(db: SessionDep, user: CurrentUser, status: str = "open"):
    result = await db.execute(select(Invoice).where(Invoice.owner_id == user.id, Invoice.status == status))
    return result.scalars().all()


@router.get("/invoices/total")
async def invoice_total(db: SessionDep, user: CurrentUser, year: int = 2026):
    result = await db.execute(text(f"SELECT SUM(amount_cents) FROM invoices WHERE EXTRACT(YEAR FROM created_at) = {year}"))
    return {"total": result.scalar()}


@router.get("/export")
async def export_table(request: Request, user: CurrentUser, table: str):
    return await _dump_table(request.app.state.pool, table)


async def _dump_table(pool, table):
    async with pool.acquire() as conn:
        return await conn.fetch("SELECT * FROM " + table + " LIMIT 1000")


@router.get("/export/v2")
async def export_table_v2(request: Request, user: CurrentUser, owner_id: int):
    async with request.app.state.pool.acquire() as conn:
        return await conn.fetch("SELECT * FROM invoices WHERE owner_id = $1 LIMIT 1000", owner_id)
