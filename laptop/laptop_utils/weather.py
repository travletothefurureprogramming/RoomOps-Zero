import requests
def get_weather():
    try:
        response = requests.get("http://192.168.1.22:8080/api/weather/Kavala", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return "Δεν μπόρεσα να φέρω τα δεδομένα του καιρού."
            
    except Exception as e:
        print(f"[WEATHER ERROR]: {e}")
        return "Υπήρξε πρόβλημα κατά τη σύνδεση με την υπηρεσία καιρού."