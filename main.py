from utils import weather
from utils import tapo_control
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

class TapoBaseModel(BaseModel):
    device_name:str
    action:str


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/weather/{city}")
async def get_current_weather(city:str):
    return {"temperature":await weather.get_temperature(city)}

@app.post("/api/tapo/control")
async def control_tapo(tapo: TapoBaseModel):
    try:
        if tapo.action == "turn_on":
            await tapo_control.DeviceFactory.turn_on(tapo.device_name)
        elif tapo.action == "turn_off":
            await tapo_control.DeviceFactory.turn_off(tapo.device_name)

        return {"code": 200, "message":"The action has sended succesfull"}

    except:
        return {"code": 404, "message":"An error has occured during the send of the action"}

    

if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=8080)