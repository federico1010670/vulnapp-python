import pickle

import yaml
from defusedxml import ElementTree as SafeET
from fastapi import APIRouter, File, Request, UploadFile
from lxml import etree

from portal.deps import CurrentUser
from portal.services import session_cache

router = APIRouter(prefix="/imports", tags=["imports"])


@router.post("/state")
async def import_state(user: CurrentUser, file: UploadFile = File(...)):
    return pickle.loads(await file.read())


@router.post("/pipeline")
async def import_pipeline(request: Request, user: CurrentUser):
    body = await request.body()
    return yaml.load(body, Loader=yaml.Loader)


@router.post("/pipeline/v2")
async def import_pipeline_v2(request: Request, user: CurrentUser):
    body = await request.body()
    return yaml.safe_load(body)


@router.get("/draft")
async def restore_draft(request: Request):
    return session_cache.restore(request.cookies.get("draft", ""))


@router.get("/draft/v2")
async def restore_draft_v2(request: Request):
    return session_cache.restore_json(request.cookies.get("draft", ""))


@router.post("/catalog")
async def import_catalog(request: Request, user: CurrentUser):
    parser = etree.XMLParser(resolve_entities=True, no_network=False)
    tree = etree.fromstring(await request.body(), parser)
    return {"items": len(tree)}


@router.post("/catalog/v2")
async def import_catalog_v2(request: Request, user: CurrentUser):
    tree = SafeET.fromstring(await request.body())
    return {"items": len(tree)}
