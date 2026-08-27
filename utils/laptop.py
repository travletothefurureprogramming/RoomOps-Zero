import requests

def say(text:str):
    requests.get(f"192.168.1.18/api/say/{text}")

def alarm():
    requests.get(f"192.168.1.18/api/alarm")

def morning(temperature:float):
    requests.get(f"192.168.1.18/api/assistant/start-morning-brief/{temperature}")