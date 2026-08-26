import scrollphathd as sphd
import asyncio

current_text = "READY"

def set_text(text: str):
    global current_text
    current_text = text
    sphd.clear()
    sphd.write_string(current_text)

async def start_matrix_loop():
    set_text("RoomOps Zero")
    while True:
        sphd.show()
        sphd.scroll(1)
        await asyncio.sleep(0.05)