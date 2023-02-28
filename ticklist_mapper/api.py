import os
import json
from base64 import b64decode, b64encode
from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from ticklist_mapper.main import get_climbs, generate_map

TMP_DIR = "static/tmp"

app = FastAPI()
templates = Jinja2Templates(directory="ticklist_mapper/templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


if not os.path.exists(TMP_DIR):
    os.makedirs(TMP_DIR)


def encode(data: dict) -> str:
    return b64encode(json.dumps(data).encode("utf-8")).decode("utf-8")


def decode(string: str) -> dict:
    return json.loads(b64decode(string.encode("utf-8")).decode("utf-8"))


@app.get("/")
async def root(request: Request, id: str = None):
    # TODO: Preload page with climbs if a saved state is provided
    if id:
        data = decode(id)
        # TODO": Update encode/decode functions to properly serialize lists
        data["climbs"] = data["climbs"].split("\n")
        print(data)

    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/search-climbs")
async def basic_form(request: Request, area: str = Form(...), climbs: str = Form(...)):
    climb_list = climbs.split("\n")
    routes = get_climbs(area, climb_list)

    routes = list(routes)

    m = generate_map(routes)

    data = {"area": area, "climbs": climbs}
    id = encode(data)
    filepath = os.path.join(TMP_DIR, f"{id}.html")

    # TODO: Save to memory insead of file using m.get_root().render()
    m.save(filepath)

    persistent_url = os.path.join(request._headers["origin"], f"?id={id}")

    # Remove static from filepath since url_for contains it already>
    return templates.TemplateResponse(
        "iframe.html",
        {
            "request": request,
            "filepath": filepath.replace("static", ""),
            "routes": [route.dict() for route in routes],
            "persistent_url": persistent_url,
        },
    )
