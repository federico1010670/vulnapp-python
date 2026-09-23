import os
import shutil
import zipfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from portal.config import EXPORT_ROOT, UPLOAD_ROOT
from portal.deps import CurrentUser
from portal.services import storage

router = APIRouter(prefix="/documents", tags=["documents"])
EXPORTS = Path(EXPORT_ROOT)


@router.get("/exports/{filename}")
async def download_export(filename: str, user: CurrentUser):
    return FileResponse(os.path.join(EXPORT_ROOT, filename))


@router.get("/exports/v2/{filename}")
async def download_export_v2(filename: str, user: CurrentUser):
    target = (EXPORTS / filename).resolve()
    if not target.is_relative_to(EXPORTS.resolve()):
        raise HTTPException(status_code=404)
    return FileResponse(target)


@router.get("/avatars/{name}")
async def avatar(name: str):
    return FileResponse(os.path.join(UPLOAD_ROOT, "avatars", os.path.basename(name)))


@router.post("/upload")
async def upload(user: CurrentUser, file: UploadFile = File(...)):
    content = await file.read()
    return {"path": storage.save(file.filename, content)}


@router.post("/bundle")
async def upload_bundle(user: CurrentUser, bundle: UploadFile = File(...)):
    with zipfile.ZipFile(bundle.file) as archive:
        archive.extractall(UPLOAD_ROOT)
    return {"ok": True}


@router.get("/notes")
async def read_note(user: CurrentUser, path: str):
    with open(Path(UPLOAD_ROOT) / "notes" / path, encoding="utf-8") as fh:
        return {"note": fh.read()}


@router.delete("/workspaces/{name}")
async def delete_workspace(name: str, user: CurrentUser):
    shutil.rmtree(Path(UPLOAD_ROOT) / name)
    return {"deleted": name}
