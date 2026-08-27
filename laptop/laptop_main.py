import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI
from playsound import playsound
import uvicorn
import random
from laptop_services.tts import say

app = FastAPI()
executor = ThreadPoolExecutor()


def speak_with_mute(text: str):
    """Ρυθμίζει το flag ώστε να αγνοούνται οι εντολές όση ώρα μιλάει το TTS."""
    global is_speaking
    is_speaking = True
    try:
        say(text)
    finally:
        is_speaking = False



def build_morning_script(temperature: float) -> str:
    greet_options = [
        "Καλημέρα! Ώρα να ξεκινήσουμε τη μέρα μας.",
        "Όμορφη καλημέρα! Ελπίζω να κοιμήθηκες καλά.",
        "Καλημέρα! Ας δούμε τι καιρό έχουμε σήμερα.",
        "Καλημέρα! Άλλη μια δημιουργική μέρα ξεκινά."
    ]
    greeting = random.choice(greet_options)
    
    if temperature > 24:
        weather_desc = f"Έχει αρκετή ζέστη σήμερα, με τη θερμοκρασία στους {int(temperature)} βαθμούς."
        outfit_advice = "Ένα ελαφρύ T-shirt είναι η καλύτερη επιλογή."
    elif temperature > 20:
        weather_desc = f"Ο καιρός είναι πολύ ευχάριστος και ήπιος, γύρω στους {int(temperature)} βαθμούς."
        outfit_advice = "Ένα λεπτό φούτερ ή μια ζακέτα θα σου χρειαστεί."
    else:
        weather_desc = f"Κάνει αρκετό κρύο σήμερα, η θερμοκρασία είναι μόλις στους {int(temperature)} βαθμούς."
        outfit_advice = "Ντύσου καλά και πάρε μαζί σου ένα ζεστό μπουφάν."
        
    wishes = [
        "Καλή σου μέρα!",
        "Να έχεις μια όμορφη μέρα!",
        "Πάμε να κατακτήσουμε τη μέρα!"
    ]
    
    return f"{greeting} {weather_desc} {outfit_advice} {random.choice(wishes)}"

@app.get("/api/alarm")
async def alarm():
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, playsound, "static/alarm.mp3")
    return {"code": 200, "message": "success"}

@app.get("/api/say/{text}")
async def say_text(text: str):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, speak_with_mute, text)
    return {"code": 200, "message": "success"}

@app.get("/api/assistant/start-morning-brief/{temperature}")
async def start_morning_brief(temperature: float):
    text = build_morning_script(float(temperature))
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, speak_with_mute, text)
    return {"status": "success", "message": "Morning brief played"}

if __name__ == "__main__":
    uvicorn.run("laptop_main:app", host="0.0.0.0", port=9000, reload=True)