import requests

def say(text:str):
    requests.get(f"http://192.168.1.18:9000/api/say/{text}")

def alarm():
    requests.get(f"http://192.168.1.18:9000/api/alarm")

def stop_alarm():
    requests.get(f"http://192.168.1.18:9000/api/alarm/stop")

def morning(temperature:float):
    requests.get(f"http://192.168.1.18:9000/api/assistant/start-morning-brief/{temperature}")

