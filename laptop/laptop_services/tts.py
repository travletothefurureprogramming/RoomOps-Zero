import asyncio
import io
import pygame
import edge_tts

pygame.mixer.init()

async def text_to_speech(text: str):
    communicate = edge_tts.Communicate(text, voice="el-GR-NestorasNeural")
    
    mp3_fp = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            mp3_fp.write(chunk["data"])
            
    mp3_fp.seek(0)

    pygame.mixer.music.load(mp3_fp, "mp3")
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

def say(text: str):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(text_to_speech(text))
    finally:
        loop.close()

