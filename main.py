import os
import asyncio
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles

import uvicorn

from services import weather, tapo_control, news, camera
from utils import notifier, laptop, matrix

from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

SECURITY_PIN = os.getenv("SECURITY_PIN")


# ============================================================
# LIFESPAN
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start Matrix background loop
    matrix_task = asyncio.create_task(
        matrix.start_matrix_loop()
    )

    try:
        yield
    finally:
        matrix_task.cancel()

        try:
            await matrix_task
        except asyncio.CancelledError:
            pass


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="Edge-AI Home Hub",
    lifespan=lifespan
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# GLOBAL STATE
# ============================================================

armed = False


# ============================================================
# TEMPLATES
# ============================================================

templates = Jinja2Templates(
    directory="templates"
)


# ============================================================
# MODELS
# ============================================================

class TapoBaseModel(BaseModel):
    device_name: str
    action: str


class PinModel(BaseModel):
    pin: str


# ============================================================
# DASHBOARD
# ============================================================

@app.get("/")
async def serve_dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )

@app.get("/tablet")
async def serve_tablet_dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="tablet.html")

# ============================================================
# ASSISTANT
# ============================================================

@app.websocket("/ws/assistant")
async def websocket_assistant(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ============================================================
# WEATHER
# ============================================================

@app.get("/api/weather/{city}")
async def get_current_weather(city: str = "Kavala"):
    return {
        "temperature": await weather.get_temperature(city)
    }


# ============================================================
# NEWS
# ============================================================

@app.get("/api/news/{city}")
async def get_current_news(city: str | None = None):
    return {
        "news": news.get_current_news(city)
    }


# ============================================================
# TAPO CONTROL
# ============================================================

@app.post("/api/tapo/control")
async def control_tapo(tapo: TapoBaseModel):

    try:

        if tapo.action == "turn_on":

            await tapo_control.DeviceFactory.turn_on(
                tapo.device_name
            )

            # Non-blocking TTS
            asyncio.create_task(
                laptop.say(
                    f"Το {tapo.device_name} ενεργοποιήθηκε επιτυχώς"
                )
            )

        elif tapo.action == "turn_off":

            await tapo_control.DeviceFactory.turn_off(
                tapo.device_name
            )

            # Non-blocking TTS
            asyncio.create_task(
                laptop.say(
                    f"Το {tapo.device_name} απενεργοποιήθηκε επιτυχώς"
                )
            )

        else:

            return {
                "code": 400,
                "message": "Unknown action"
            }

        return {
            "code": 200,
            "message": "Action executed successfully"
        }

    except Exception as e:

        print(f"[TAPO] Error: {e}")

        return {
            "code": 500,
            "message": f"Error: {str(e)}"
        }


# ============================================================
# ARM SYSTEM
# ============================================================

@app.api_route(
    "/api/arm",
    methods=["GET", "POST"]
)
async def arm():

    global armed

    armed = True

    matrix.set_text("ARMED  ")

    # Non-blocking TTS
    asyncio.create_task(
        laptop.say(
            "Το σύστημα οπλίστηκε"
        )
    )

    print(
        "[SECURITY] System ARMED via Action Block / API!"
    )

    return {
        "status": "success",
        "system_armed": True
    }


# ============================================================
# VERIFY PIN
# ============================================================

@app.post("/api/verify-pin")
async def verify_pin(data: PinModel):

    global armed

    if data.pin == SECURITY_PIN:

        armed = False

        matrix.set_text("DISARMED  ")

        print(
            "[SECURITY] System DISARMED via Valid PIN!"
        )

        # Non-blocking TTS
        asyncio.create_task(
            laptop.say(
                "Το σύστημα αφοπλίστηκε"
            )
        )

        # Stop alarm without blocking
        asyncio.create_task(
            laptop.stop_alarm()
        )

        return {
            "status": "success",
            "correct": True,
            "system_armed": False
        }

    else:

        print(
            "[SECURITY] Invalid PIN attempt!"
        )

        return {
            "status": "error",
            "correct": False,
            "message": "Invalid PIN"
        }


# ============================================================
# DIRECT DISARM
# ============================================================

@app.api_route(
    "/api/disarm",
    methods=["GET", "POST"]
)
async def disarm():

    global armed

    armed = False

    matrix.set_text("DISARMED  ")

    # Non-blocking TTS
    asyncio.create_task(
        laptop.say(
            "Το σύστημα αφοπλίστηκε"
        )
    )

    # Non-blocking alarm stop
    asyncio.create_task(
        laptop.stop_alarm()
    )

    print(
        "[SECURITY] System DISARMED via Direct API!"
    )

    return {
        "status": "success",
        "system_armed": False
    }


# ============================================================
# SYSTEM STATUS
# ============================================================

@app.get("/api/status")
async def get_system_status():

    # IMPORTANT:
    # Do NOT call laptop.say() here.
    #
    # The frontend may call /api/status repeatedly.
    # Calling TTS here would make the laptop speak repeatedly.

    return {
        "system_armed": armed
    }


# ============================================================
# STATIC FILES
# ============================================================

os.makedirs(
    "static",
    exist_ok=True
)

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


# ============================================================
# MOTION DETECTION
# ============================================================

@app.get("/api/camera/check-motion")
async def check_motion():

    global armed

    # --------------------------------------------------------
    # SYSTEM NOT ARMED
    # --------------------------------------------------------

    if not armed:

        return {
            "motion": False,
            "system_armed": False,
            "timestamp": None,
            "image_url": None
        }

    # --------------------------------------------------------
    # DETECT MOTION
    # --------------------------------------------------------

    has_motion = await camera.motion_detector.detect_motion()

    # --------------------------------------------------------
    # MOTION DETECTED
    # --------------------------------------------------------

    if has_motion:

        print(
            "[SECURITY] MOTION DETECTED!"
        )

        # Matrix
        matrix.set_text(
            "ALERT!   MOTION   DETECTED  "
        )

        # Notification
        notifier.send_notification()

        # ----------------------------------------------------
        # LAPTOP ALARM
        # ----------------------------------------------------
        # IMPORTANT:
        # Do NOT await this.
        #
        # The server continues immediately.

        asyncio.create_task(
            laptop.alarm()
        )

        # ----------------------------------------------------
        # TURN ON SECURITY LIGHT
        # ----------------------------------------------------

        await tapo_control.DeviceFactory.turn_on(
            "l900"
        )

        # ----------------------------------------------------
        # SET LIGHT RED
        # ----------------------------------------------------

        await tapo_control.DeviceFactory.set_colour(
            "l900",
            "red"
        )

    # ========================================================
    # RESPONSE
    # ========================================================

    return {
        "motion": has_motion,
        "system_armed": True,
        "timestamp": camera.motion_detector.last_motion_time,
        "image_url": (
            "/static/last_motion.jpg"
            if has_motion
            else None
        )
    }


# ============================================================
# SERVER
# ============================================================

if __name__ == "__main__":

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True
    )