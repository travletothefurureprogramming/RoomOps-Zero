import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
import uvicorn
from services import weather, tapo_control, news, camera
from utils import notifier, volume

load_dotenv()
SECURITY_PIN = os.getenv("SECURITY_PIN")  
app = FastAPI(title="Edge-AI Home Hub")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

armed = False

templates = Jinja2Templates(directory="templates")

class TapoBaseModel(BaseModel):
    device_name: str
    action: str

class PinModel(BaseModel):
    pin: str

@app.get("/")
async def serve_dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/api/weather/{city}")
async def get_current_weather(city: str = "Kavala"):
    return {"temperature": await weather.get_temperature(city)}

@app.get("/api/news/{city}")
async def get_current_news(city: str | None = None):
    return {"news": news.get_current_news(city)}

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

@app.api_route("/api/arm", methods=["GET", "POST"])
async def arm():
    global armed
    armed = True
    print("[SECURITY] System ARMED via Action Block / API!")
    return {"status": "success", "system_armed": True}

@app.post("/api/verify-pin")
async def verify_pin(data: PinModel):
    global armed
    if data.pin == SECURITY_PIN:
        armed = False
        print("[SECURITY] System DISARMED via Valid PIN!")
        return {"status": "success", "correct": True, "system_armed": False}
    else:
        print("[SECURITY] Invalid PIN attempt!")
        return {"status": "error", "correct": False, "message": "Invalid PIN"}

@app.api_route("/api/disarm", methods=["GET", "POST"])
async def disarm():
    global armed
    armed = False
    print("[SECURITY] System DISARMED via Direct API!")
    return {"status": "success", "system_armed": False}

@app.get("/api/status")
async def get_system_status():
    global armed
    return {"system_armed": armed}

os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/api/camera/check-motion")
async def check_motion():
    global armed
    if not armed:
        return {
            "motion": False,
            "system_armed": False,
            "timestamp": None,
            "image_url": None
        }

    has_motion = await camera.motion_detector.detect_motion()
    if has_motion:
        notifier.send_notification()
        volume.set_volume(100)
        await tapo_control.DeviceFactory.turn_on("l900")
        await tapo_control.DeviceFactory.set_colour("l900","red")

    return {
        "motion": has_motion,
        "system_armed": True,
        "timestamp": camera.motion_detector.last_motion_time,
        "image_url": "/static/last_motion.jpg" if has_motion else None
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)