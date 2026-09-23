from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from portal.config import APP_NAME
from portal.routers import admin, auth, documents, imports, integrations, pages, reports, search

app = FastAPI(title=APP_NAME, debug=True)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for module in (admin, auth, documents, imports, integrations, pages, reports, search):
    app.include_router(module.router)
