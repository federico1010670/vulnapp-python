import csv
import io

from portal.repositories import report_repository

SORTABLE_COLUMNS = {"region", "total"}


async def revenue_by_region(db, region, sort):
    order = sort or "region"
    return await report_repository.fetch_revenue(db, region, order)


async def revenue_for_region(db, region, sort):
    rows = await report_repository.fetch_revenue_for_region(db, region)
    key = sort if sort in SORTABLE_COLUMNS else "region"
    return sorted(rows, key=lambda row: row[key])


def _legacy_csv_export(rows):
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=["region", "total"])
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()
