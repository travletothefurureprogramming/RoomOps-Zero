import requests
import os
from dotenv import load_dotenv

load_dotenv(".env")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def send_notification(title="🚨 SECURITY ALERT", message="Motion detected in the room!", image_path="static/last_motion.jpg"):
    if not DISCORD_WEBHOOK_URL:
        print("[Notifier Error] DISCORD_WEBHOOK_URL is missing from .env")
        return False

    if not os.path.exists(image_path):
        print(f"[Notifier Error] File not found: {image_path}")
        return False

    filename = os.path.basename(image_path)

    payload = {
        "content": f"@everyone **{title}**\n{message}"
    }

    try:
        with open(image_path, "rb") as img:
            files = {
                "file": (filename, img, "image/jpeg")
            }
            response = requests.post(
                DISCORD_WEBHOOK_URL,
                data=payload,
                files=files,
                timeout=5
            )

        if response.status_code in [200, 204]:
            print("[Notifier] Discord notification sent successfully!")
            return True
        else:
            print(f"[Notifier Error] Discord status code: {response.status_code}")
            return False

    except Exception as e:
        print(f"[Notifier Exception] Failed to send notification: {e}")
        return False

if __name__ == "__main__":
    send_notification()