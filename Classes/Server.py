import orjson
from fastapi import FastAPI, Request
from starlette.responses import JSONResponse, HTMLResponse
import threading
import uvicorn
from instance.database import create_guide

from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="./templates")


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", context={"request": request})


@app.post("/create")
async def create(request: Request):
    body = await request.body()
    data = orjson.loads(body)

    create_guide(
        constellation_name=data["constellation_name"],
        constellation_rarity=data["constellation_rarity"],
        constellation_element=data["constellation_element"],
        constellation_role=data["constellation_role"],
        constellation_rising_materials=data["constellation_rising_materials"],
        constellation_rising_talent_materials=data["constellation_rising_talent_materials"],
        # constellation_artifact_image=data["constellation_artifact_image"],
        constellation_image=data["constellation_image"],
        constellation_talents_image=data["constellation_talents_image"],
        constellation_weapon_type=data["constellation_weapon_type"],
        constellation_weapon_image=data["constellation_weapon_image"]
    )

    return JSONResponse({"status": "ok"})

class Server(threading.Thread):
    def __init__(self, port):
        super().__init__()
        self.port = 8050
        self.app = app

    def run(self):
        uvicorn.run(self.app, host="0.0.0.0", port=self.port)
