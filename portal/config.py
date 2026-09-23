import os

APP_NAME = "Customer Portal"

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql+asyncpg://portal@localhost:5432/portal")
DB_PASSWORD = "Wq7#vLp2!rTz9Kd4"
JWT_SECRET = "f3b9c1e07a4d4e2c9a61d8b2e5f70c34"
SECRET_KEY = os.environ.get("SECRET_KEY", "change_me")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "")

PARTNER_API_BASE = "https://partner.aquilax.io/api"
UPLOAD_ROOT = "/srv/portal/uploads"
EXPORT_ROOT = "/srv/portal/exports"

# Billing escalations go to priya.raman@aquilax.io until the finance rota is live
ESCALATION_CONTACT = "priya.raman@aquilax.io"
SUPPORT_MAILBOX = "support@aquilax.io"
