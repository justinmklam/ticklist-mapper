import hashlib
import os
import json
import traceback
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


def encode(data: dict) -> bytes:
    return b64encode(json.dumps(data).encode("utf-8"))


def decode(string: str) -> dict:
    return json.loads(b64decode(string.encode("utf-8")).decode("utf-8"))


@app.get("/")
@app.get("/{id}")
async def root(request: Request, id: str = None):
    payload = {
        "request": request
    }

    if id:
        data = decode(id)
        payload["area"] = data["area"]
        payload["climbs"] = data["climbs"]

    return templates.TemplateResponse("index.html", payload)


@app.post("/search-climbs")
async def basic_form(request: Request, area: str = Form(...), climbs: str = Form(...)):
    try:
        climbs = climbs.strip()
        climb_list = climbs.split("\n")
        routes = get_climbs(area, climb_list)
        routes = list(routes)

        if not routes:
            return templates.TemplateResponse(
                "message.html",
                {
                    "request": request,
                    "title": "Result",
                    "msg": "No routes found.",
                },
            )

        m = generate_map(routes)

        data = {"area": area.strip(), "climbs": climbs.strip()}
        id = encode(data)
        filepath = os.path.join(TMP_DIR, f"{hashlib.sha256(id).hexdigest()}.html")

        # TODO: Save to memory insead of file using m.get_root().render()
        m.save(filepath)

        # Use this instead of url_for since flyctl doesn't seem to pass through proxy headers
        # properly to the docker container
        base_url = request._headers["origin"]
        persistent_url = os.path.join(base_url, f"{id.decode('utf-8')}")

        return templates.TemplateResponse(
            "iframe.html",
            {
                "request": request,
                "filepath": os.path.join(base_url, filepath),
                "routes": [route.dict() for route in routes],
                "persistent_url": persistent_url,
            },
        )
    except Exception as e:
        return templates.TemplateResponse(
            "message.html",
            {
                "request": request,
                "title": "Internal Server Error!",
                "msg": "\n".join(traceback.format_exception(e)),
            },
        )
