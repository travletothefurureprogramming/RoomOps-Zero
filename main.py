from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from utils import weather, tapo_control

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


templates = Jinja2Templates(directory="templates")


class TapoBaseModel(BaseModel):
    device_name: str
    action: str


@app.get("/")
async def serve_dashboard(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="index.html"
    )


@app.get("/api/weather/{city}")
async def get_current_weather(city: str):
    return {"temperature": await weather.get_temperature(city)}


@app.post("/api/tapo/control")
async def control_tapo(tapo: TapoBaseModel):
    try:
        if tapo.action == "turn_on":
            await tapo_control.DeviceFactory.turn_on(tapo.device_name)
        elif tapo.action == "turn_off":
            await tapo_control.DeviceFactory.turn_off(tapo.device_name)

        return {"code": 200, "message": "Action executed successfully"}
    except Exception as e:
        return {"code": 500, "message": f"Error: {str(e)}"}


if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=8080)