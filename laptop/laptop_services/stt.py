import sys
from pathlib import Path

# Προσθήκη root path
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import time
import random
import asyncio
import threading
import webbrowser
import speech_recognition as sr
from laptop.laptop_utils import datetime, weather
from utils import laptop

stop_listening = None

# -------------------------------------------------------------
# Δημιουργία μόνιμου Event Loop σε ξεχωριστό background thread
# -------------------------------------------------------------
loop = asyncio.new_event_loop()

def start_loop(event_loop):
    asyncio.set_event_loop(event_loop)
    event_loop.run_forever()

loop_thread = threading.Thread(target=start_loop, args=(loop,), daemon=True)
loop_thread.start()

def speak(text: str):
    """Στέλνει την async laptop.say() στο μόνιμο event loop."""
    try:
        future = asyncio.run_coroutine_threadsafe(laptop.say(text), loop)
        future.result()  # Περιμένει να ολοκληρωθεί η ομιλία
    except Exception as e:
        print(f"Σφάλμα κατά την ομιλία: {e}")

# --- Λίστες Απαντήσεων ---
TIME_RESPONSES = [
    "Η ώρα είναι {time}.",
    "Αυτή τη στιγμή η ώρα είναι {time}.",
    "Τώρα είναι {time}."
]

UNKNOWN_RESPONSES = [
    "Δεν κατάλαβα τι είπατε.",
    "Μπορείτε να το επαναλάβετε;",
    "Δεν είμαι σίγουρος ότι σε έπιασα."
]

def callback(recognizer, audio):
    try:
        text = recognizer.recognize_google(audio, language="el-GR").lower()
        print(f"Ακούστηκε: {text}")

        # 1. Ώρα
        if any(w in text for w in ["ώρα", "ωρα", "τι ωρα", "ποση ωρα"]):
            current_time = datetime.get_current_time()
            phrase = random.choice(TIME_RESPONSES).format(time=current_time)
            speak(phrase)

        # 2. Ημερομηνία / Μέρα
        elif any(w in text for w in ["ημερομηνία", "ημερομηνια", "μέρα", "μερα", "τι μέρα", "ποια μέρα"]):
            current_date = datetime.get_current_date()
            responses = [
                f"Σήμερα είναι {current_date}.",
                f"Η ημερομηνία είναι {current_date}.",
                f"Έχουμε {current_date}."
            ]
            speak(random.choice(responses))

        # 3. Καιρός
        elif any(w in text for w in ["καιρός", "καιρος", "καιρό", "καιρο", "βρέξει", "θερμοκρασία"]):
            current_weather = weather.get_weather()
            responses = [
                f"Ο καιρός αυτή τη στιγμή: {current_weather}.",
                f"Τα νέα για τον καιρό είναι: {current_weather}.",
                f"Ο καιρός δείχνει {current_weather}."
            ]
            speak(random.choice(responses))

        # 4. Αναζήτηση στο Google
        elif any(w in text for w in ["ψάξε", "ψαξε", "αναζήτηση", "αναζητηση", "βρες", "γούγλαρε"]):
            search_query = text
            for trigger in ["ψάξε", "ψαξε", "αναζήτηση", "αναζητηση", "βρες", "γούγλαρε", "στο google"]:
                search_query = search_query.replace(trigger, "")
            
            search_query = search_query.strip()
            
            if search_query:
                responses = [
                    f"Ψάχνω στο Google για {search_query}.",
                    f"Ανοίγω αναζήτηση για {search_query}.",
                    f"Βρίσκω αποτελέσματα για {search_query}."
                ]
                speak(random.choice(responses))
                webbrowser.open(f"https://www.google.com/search?q={search_query}")
            else:
                speak("Τι θέλετε να ψάξω;")

        # 5. Χιούμορ / Αστεία
        elif any(w in text for w in ["αστείο", "αστειο", "ανέκδοτο", "ανεκδοτο", "πες κάτι αστείο"]):
            jokes = [
                "Γιατί οι προγραμματιστές προτιμούν το σκοτάδι; Επειδή το φως τραβάει τα bugs!",
                "Υπάρχουν 10 τύποι ανθρώπων: αυτοί που καταλαβαίνουν το δυαδικό σύστημα και αυτοί που δεν το καταλαβαίνουν.",
                "Πώς λέγεται ο προγραμματιστής που δεν πίνει καφέ; Null Pointer Exception!"
            ]
            speak(random.choice(jokes))

        # 6. Τερματισμός
        elif any(w in text for w in ["στοπ", "stop", "κλείσε", "κλεισε", "αντίο", "αντιο", "σταμάτα"]):
            responses = ["Αντίο σας!", "Τα λέμε μετά!", "Τερματισμός λειτουργίας."]
            speak(random.choice(responses))
            if stop_listening:
                stop_listening(wait_for_stop=False)


    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results; {e}")

r = sr.Recognizer()
m = sr.Microphone()

with m as source:
    r.adjust_for_ambient_noise(source)

def listen_in_background():
    global stop_listening
    stop_listening = r.listen_in_background(m, callback)

listen_in_background()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    if stop_listening:
        stop_listening(wait_for_stop=False)