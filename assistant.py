import asyncio
import datetime
import io
import json
import string
import unicodedata
import webbrowser

import edge_tts
import requests
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
import websockets

# --- ΡΥΘΜΙΣΕΙΣ ---
VOICE = "el-GR-NestorasNeural"
WAKE_WORDS = ["mark", "μαρκ", "μάρκ"]
API_BASE_URL = "http://192.168.1.22:8080"
WS_URI = "ws://192.168.1.22:8080/ws/assistant"

r = sr.Recognizer()
ws_connection = None


# --- ENTOLES HOME AUTOMATION & API ---

def turn_on_lights() -> str:
    try:
        res = requests.post(f"{API_BASE_URL}/api/tapo/control", json={"device_name": "l900", "action": "turn_on"})
        if res.status_code == 200:
            return "Άναψα τα φώτα."
    except Exception as e:
        print(f"[ERROR] {e}")
    return "Απέτυχε η ενεργοποίηση των φώτων."

def turn_off_lights() -> str:
    try:
        res = requests.post(f"{API_BASE_URL}/api/tapo/control", json={"device_name": "l900", "action": "turn_off"})
        if res.status_code == 200:
            return "Έσβησα τα φώτα."
    except Exception as e:
        print(f"[ERROR] {e}")
    return "Απέτυχε η απενεργοποίηση των φώτων."

def arm_system() -> str:
    try:
        res = requests.post(f"{API_BASE_URL}/api/arm")
        if res.status_code == 200:
            return "Το σύστημα οπλίστηκε."
    except Exception as e:
        print(f"[ERROR] {e}")
    return "Απέτυχε η οπλισή του συστήματος."

def get_time() -> str:
    now = datetime.datetime.now().strftime("%H:%M")
    return f"Η ώρα είναι {now}."

def get_date() -> str:
    days = ["Δευτέρα", "Τρίτη", "Τετάρτη", "Πέμπτη", "Παρασκευή", "Σάββατο", "Κυριακή"]
    months = ["Ιανουαρίου", "Φεβρουαρίου", "Μαρτίου", "Απριλίου", "Μαΐου", "Ιουνίου", 
              "Ιουλίου", "Αυγούστου", "Σεπτεμβρίου", "Οκτωβρίου", "Νοεμβρίου", "Δεκεμβρίου"]
    now = datetime.datetime.now()
    return f"Σήμερα είναι {days[now.weekday()]}, {now.day} {months[now.month - 1]} του {now.year}."

def quit_app() -> str:
    return "QUIT"


# --- DICTIONARY ΕΝΤΟΛΩΝ ---

COMMANDS_DB = {
    # Φώτα & Αυτοματισμοί
    ("αναψε τα φωτα", "ανοιξε τα φωτα", "αναψε φωτα"): turn_on_lights,
    ("σβησε τα φωτα", "κλεισε τα φωτα", "σβησε φωτα"): turn_off_lights,
    ("οπλισε το συστημα", "οπλισε συναγερμο", "οπλισε"): arm_system,

    # Χαιρετισμοί & Διαλογικά
    ("γεια", "γεια σου", "γειασου", "χαιρετω"): "Γειά σου! Πώς μπορώ να σε βοηθήσω;",
    ("καλημερα", "ομορφη μερα"): "Καλημέρα! Ελπίζω να έχεις μια όμορφη μέρα.",
    ("καλησπερα"): "Καλησπέρα! Τι μπορώ να κάνω για εσένα;",
    ("τι κανεις", "πως εισαι"): "Είμαι μια χαρά, έτοιμος για δουλειά!",
    ("ποιος εισαι", "πως σε λενε"): "Με λένε Mark! Είμαι ο ψηφιακός σου βοηθός.",
    
    # Ώρα / Ημερομηνία / Web
    ("τι ωρα ειναι", "ωρα ειναι", "πες μου την ωρα"): get_time,
    ("τι μερα ειναι", "ημερομηνια"): get_date,
    ("ανοιξε το youtube", "youtube"): lambda: (webbrowser.open("https://youtube.com"), "Ανοίγω το YouTube")[1],
    ("ανοιξε το google", "google"): lambda: (webbrowser.open("https://google.com"), "Ανοίγω το Google")[1],
    ("ανοιξε το github", "github"): lambda: (webbrowser.open("https://github.com"), "Ανοίγω το GitHub")[1],
    ("κλεισιμο", "τερματισμος", "exit"): quit_app,
}


# --- HELPER FUNCTIONS ---

def remove_accents_and_punct(text: str) -> str:
    text = text.lower().strip()
    text = text.translate(str.maketrans('', '', string.punctuation))
    nfkd_form = unicodedata.normalize('NFKD', text)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def check_commands(text: str) -> str:
    clean_input = remove_accents_and_punct(text)
    input_words = clean_input.split()

    # 1. Πρώτα ελέγχουμε για πλήρεις φράσεις (Phrases)
    for keywords, response in COMMANDS_DB.items():
        for kw in keywords:
            if " " in kw and kw in clean_input:
                return response() if callable(response) else response

    # 2. Μετά ελέγχουμε για μεμονωμένες λέξεις (Exact Word Match)
    for keywords, response in COMMANDS_DB.items():
        for kw in keywords:
            if " " not in kw and kw in input_words:
                return response() if callable(response) else response

    return "Δεν κατάλαβα τι είπες, μπορείς να το επαναλάβεις;"

async def notify_status(state: str):
    global ws_connection
    if ws_connection:
        try:
            await ws_connection.send(json.dumps({"type": "assistant_state", "state": state}))
        except Exception:
            ws_connection = None

async def speak(text: str) -> None:
    """Streamed Edge-TTS απευθείας στη RAM (χωρίς pygame και MP3 αρχεία)"""
    await notify_status("speaking")
    
    communicate = edge_tts.Communicate(text, VOICE)
    audio_bytes = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_bytes += chunk["data"]
            
    data, samplerate = sf.read(io.BytesIO(audio_bytes))
    sd.play(data, samplerate)
    sd.wait()
    
    await notify_status("idle")

def listen_online() -> str:
    """Google Speech Recognition (Online API - Υψηλή ακρίβεια στα ελληνικά)"""
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.2)
        audio = r.listen(source)
    try:
        return r.recognize_google(audio, language="el-GR")
    except Exception:
        return ""

async def connect_ws():
    global ws_connection
    try:
        ws_connection = await websockets.connect(WS_URI)
        print("[WS] Επιτυχής σύνδεση με το Dashboard!")
    except Exception:
        ws_connection = None
        print("[WARN] Χωρίς WebSocket connection (Standalone mode).")

async def main():
    await connect_ws()
    print("\n[READY] Ο Mark ακούει (Google STT + In-Memory TTS)... Πες 'Mark'!")
    
    while True:
        loop = asyncio.get_running_loop()
        raw_text = await loop.run_in_executor(None, listen_online)

        if not raw_text:
            continue

        clean_text = remove_accents_and_punct(raw_text)
        detected_word = next((w for w in WAKE_WORDS if w in clean_text), None)

        if detected_word:
            print(f"\n[Detected: '{raw_text}']")
            command_part = clean_text.replace(detected_word, "").strip()

            if command_part:
                response_text = check_commands(command_part)
            else:
                await speak("Ναι, σε ακούω!")
                await notify_status("listening")
                command_text = await loop.run_in_executor(None, listen_online)
                if not command_text:
                    await speak("Δεν άκουσα κάποια εντολή.")
                    continue
                response_text = check_commands(command_text)

            if response_text == "QUIT":
                await speak("Απενεργοποίηση συστήματος. Αντίο!")
                break

            await speak(response_text)

if __name__ == "__main__":
    asyncio.run(main())