import httpx

LAPTOP_URL = "http://192.168.1.18:9000"

client = httpx.AsyncClient(
    base_url=LAPTOP_URL,
    timeout=3.0
)


async def say(text: str):
    await client.get(f"/api/say/{text}")


async def alarm():
    await client.get("/api/alarm")


async def stop_alarm():
    await client.get("/api/alarm/stop")


async def morning(temperature: float):
    await client.get(
        f"/api/assistant/start-morning-brief/{temperature}"
    )