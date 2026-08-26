import scrollphathd as sphd
import asyncio
from services.weather import get_temperature

current_text = "READY"
sphd.rotate(180)

def set_text(text: str):
    global current_text
    current_text = text
    sphd.clear()
    sphd.write_string(current_text)

async def start_matrix_loop():
    set_text("RoomOps Zero")
    for i in range(3):
        sphd.show()
        sphd.scroll(1)
        await asyncio.sleep(0.05)
    set_text(f"{await get_temperature("Kavala")}C")
    while True:
        sphd.show()
        sphd.scroll(1)
        await asyncio.sleep(0.05)