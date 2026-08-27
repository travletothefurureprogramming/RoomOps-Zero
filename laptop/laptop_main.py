import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI
from playsound import playsound
import uvicorn
import random
import speech_recognition as sr

from laptop_services.tts import say
from laptop_utils import datetime, weather

app = FastAPI()
executor = ThreadPoolExecutor()

recognizer = sr.Recognizer()
microphone = sr.Microphone()
stop_listening_fn = None
is_speaking = False  

def speak_with_mute(text: str):
    """Ρυθμίζει το flag ώστε να αγνοούνται οι εντολές όση ώρα μιλάει το TTS."""
    global is_speaking
    is_speaking = True
    try:
        say(text)
    finally:
        is_speaking = False

def speech_callback(recognizer, audio):
    global is_speaking
    
    if is_speaking:
        return

    try:
        text = recognizer.recognize_google(audio, language="el-GR")
        print("[VOICE IN]: " + text)

        text_lower = text.lower()
        
        if any(w in text_lower for w in ["ώρα", "ώρες", "τι ώρα"]):
            time_str = datetime.get_current_time()
            responses = [
                f"Η ώρα είναι {time_str}.",
                f"Αυτή τη στιγμή η ώρα είναι {time_str}.",
                f"Είναι ακριβώς {time_str}.",
                f"Τσεκάρισα το ρολόι, είναι {time_str}."
            ]
            speak_with_mute(random.choice(responses))

        elif any(w in text_lower for w in ["ημερομηνία", "μέρα", "σήματα", "ποια μέρα"]):
            date_str = datetime.get_current_date()
            responses = [
                f"Σήμερα είναι {date_str}.",
                f"Έχουμε {date_str}.",
                f"Το ημερολόγιο δείχνει {date_str}."
            ]
            speak_with_mute(random.choice(responses))

        elif any(w in text_lower for w in ["καιρός", "καιρό", "θερμοκρασία", "ζέστη", "κρύο"]):
            weather_data = weather.get_weather()
            temperature = weather_data.get("temperature", 20) if isinstance(weather_data, dict) else 20
            
            if temperature > 28:
                options = [
                    f"Έχει πολλή ζέστη σήμερα, η θερμοκρασία είναι στους {int(temperature)} βαθμούς.",
                    f"Καίει ο ήλιος! Βλέπω {int(temperature)} βαθμούς Κελσίου.",
                    f"Ζεστή μέρα, είμαστε στους {int(temperature)} βαθμούς."
                ]
            elif temperature > 20:
                options = [
                    f"Ο καιρός είναι υπέροχος, γύρω στους {int(temperature)} βαθμούς.",
                    f"Πολύ γλυκός καιρός, η θερμοκρασία είναι στους {int(temperature)} βαθμούς.",
                    f"Ιδανική θερμοκρασία, έχουμε {int(temperature)} βαθμούς."
                ]
            elif temperature > 12:
                options = [
                    f"Έχει λίγη δροσιά, η θερμοκρασία είναι στους {int(temperature)} βαθμούς.",
                    f"Δεν κάνει πολύ κρύο, είμαστε στους {int(temperature)} βαθμούς.",
                    f"Ο καιρός είναι δροσερός, στους {int(temperature)} βαθμούς."
                ]
            else:
                options = [
                    f"Κάνει αρκετό κρύο, η θερμοκρασία έπεσε στους {int(temperature)} βαθμούς.",
                    f"Ντύσου καλά, έχουμε μόλις {int(temperature)} βαθμούς.",
                    f"Παγωνιά σήμερα, το θερμόμετρο δείχνει {int(temperature)} βαθμούς."
                ]
            speak_with_mute(random.choice(options))

        elif any(w in text_lower for w in ["γεια", "γειά", "γεια σου", "χαιρέτα", "τι κάνεις", "πώς είσαι"]):
            greetings = [
                "Γεια σου! Όλα καλά, εσύ πώς είσαι;",
                "Γεια! Είμαι έτοιμος να σε βοηθήσω.",
                "Χαίρετε! Όλα λειτουργούν στην εντέλεια.",
                "Γεια σου! Τι σχεδιάζουμε για σήμερα;"
            ]
            speak_with_mute(random.choice(greetings))

        elif any(w in text_lower for w in ["ποιος είσαι", "τι είσαι", "όνομα"]):
            identity_responses = [
                "Είμαι ο προσωπικός σου ψηφιακός βοηθός!",
                "Είμαι το έξυπνο σύστημα του σπιτιού σου.",
                "Είμαι ο βοηθός σου, πάντα εδώ για να σε διευκολύνω."
            ]
            speak_with_mute(random.choice(identity_responses))

    except sr.UnknownValueError:
        pass
    except sr.RequestError as e:
        print(f"[SPEECH ERROR]: {e}")

@app.on_event("startup")
def startup_event():
    global stop_listening_fn
    print("[SERVER] Calibrating microphone...")
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
    
    print("[SERVER] Starting background speech listener...")
    stop_listening_fn = recognizer.listen_in_background(microphone, speech_callback)

@app.on_event("shutdown")
def shutdown_event():
    global stop_listening_fn
    if stop_listening_fn:
        stop_listening_fn(wait_for_stop=False)

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