import scrollphathd as sphd
import asyncio

async def write_text(text:str):
    while True:
        sphd.write_string(text)

        sphd.show()
        sphd.scroll(1)
        await asyncio.sleep(0.05)

asyncio.run(write_text("Hello World!"))