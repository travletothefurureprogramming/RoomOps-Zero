import time
import speech_recognition as sr
from laptop.laptop_utils import datetime, weather


stop_listening = None

def callback(recognizer, audio):
    try:
        text = recognizer.recognize_google(audio)
        print("Google Speech Recognition thinks you said " + text)

        if "ώρα" in text:
            datetime.get_current_time()
        elif "ημερομηνία" in text:
            datetime.get_current_date()
        elif "καιρός" in text:
            weather.get_weather()
        
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))


r = sr.Recognizer()
m = sr.Microphone()
with m as source:
    r.adjust_for_ambient_noise(source)  

def listen_in_background():
    global stop_listening
    stop_listening = r.listen_in_background(m, callback)

for _ in range(50): time.sleep(0.1)  

stop_listening(wait_for_stop=False)

while True: time.sleep(0.1) 