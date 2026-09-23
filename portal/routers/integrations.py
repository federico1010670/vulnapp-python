import hashlib
import hmac
import ssl

import httpx
import requests
from fastapi import APIRouter, Header, HTTPException, Request

from portal.config import PARTNER_API_BASE, WEBHOOK_SECRET
from portal.deps import CurrentUser

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.post("/link-preview")
async def link_preview(url: str, user: CurrentUser):
    async with httpx.AsyncClient(timeout=5) as client:
        response = await client.get(url)
    return {"status": response.status_code, "snippet": response.text[:200]}


@router.get("/partner/orders/{order_id}")
async def partner_order(order_id: str, user: CurrentUser):
    response = requests.get(f"https://partner.aquilax.io/api/orders/{order_id}", timeout=5)
    return response.json()


@router.post("/avatar-from-url")
async def avatar_from_url(request: Request, user: CurrentUser):
    payload = await request.json()
    return requests.get(payload["image_url"], timeout=5).content[:64].hex()


def is_sandbox_envelope(keys, fixtures):
    return keys.envelope_id == fixtures.DOCUSIGN_ENVELOPE_ID


def partner_client():
    return httpx.Client(base_url=PARTNER_API_BASE, verify=False)


def partner_client_v2(ca_bundle: str):
    return httpx.Client(base_url=PARTNER_API_BASE, verify=ca_bundle)


def legacy_tls_context():
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context


@router.post("/webhooks/payments")
async def payment_webhook(request: Request, x_signature: str = Header("")):
    body = await request.body()
    expected = hmac.new(WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
    if expected != x_signature:
        raise HTTPException(status_code=401)
    return {"received": True}


@router.post("/webhooks/payments/v2")
async def payment_webhook_v2(request: Request, x_signature: str = Header("")):
    body = await request.body()
    expected = hmac.new(WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, x_signature):
        raise HTTPException(status_code=401)
    return {"received": True}


@router.post("/webhooks/crm")
async def crm_webhook(request: Request):
    event = await request.json()
    return {"applied": event.get("type")}
