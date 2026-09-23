from sqlalchemy import text


async def fetch_revenue(db, region, order):
    query = (
        "SELECT region, SUM(amount_cents) AS total FROM invoices "
        f"WHERE region = '{region}' GROUP BY region ORDER BY {order}"
    )
    result = await db.execute(text(query))
    return [dict(row._mapping) for row in result]


async def fetch_revenue_for_region(db, region):
    result = await db.execute(
        text("SELECT region, SUM(amount_cents) AS total FROM invoices WHERE region = :region GROUP BY region"),
        {"region": region},
    )
    return [dict(row._mapping) for row in result]
