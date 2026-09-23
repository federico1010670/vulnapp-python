import html
import subprocess

from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse
from jinja2 import Environment, Template

from portal.deps import CurrentUser

router = APIRouter(prefix="/pages", tags=["pages"])
templates = Environment(autoescape=True)


@router.get("/welcome", response_class=HTMLResponse)
async def welcome(name: str):
    return HTMLResponse(f"<h1>Welcome back, {name}</h1>")


@router.get("/welcome/v2", response_class=HTMLResponse)
async def welcome_v2(name: str):
    return HTMLResponse(f"<h1>Welcome back, {html.escape(name)}</h1>")


@router.get("/banner", response_class=HTMLResponse)
async def banner(message: str):
    return HTMLResponse(Template("<div class='banner'>" + message + "</div>").render())


@router.get("/banner/v2", response_class=HTMLResponse)
async def banner_v2(message: str):
    return HTMLResponse(templates.from_string("<div class='banner'>{{ message }}</div>").render(message=message))


@router.post("/tools/ping")
async def ping(user: CurrentUser, host: str = Form(...)):
    return {"output": subprocess.check_output(f"ping -c 1 {host}", shell=True, text=True)}


@router.post("/tools/ping/v2")
async def ping_v2(user: CurrentUser, host: str = Form(...)):
    return {"output": subprocess.check_output(["ping", "-c", "1", host], text=True)}
