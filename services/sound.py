from fastapi import FastAPI
from playsound import playsound
import pyttsx4
import uvicorn

engine = pyttsx4.init()
def say(text:str):
    engine.say(text)
    engine.runAndWait()

app = FastAPI()

@app.get("api/alarm")
async def alarm():
    playsound("static/alarm.mp3")
    return {"code":200,"message":"success"}

app.get("api/say/{text}")
async def say_text(text:str):
    say(text)
    return {"code":200,"message":"success"}

if __name__ == "__main__":
    uvicorn.run("sound:app", host="0.0.0.0", port=9000, reload=True)