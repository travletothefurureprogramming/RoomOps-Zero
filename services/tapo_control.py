import asyncio
import os
from dotenv import load_dotenv
from tapo import ApiClient
from tapo.requests import Color

load_dotenv(".env")

username = {
    "l900": os.getenv("l900_user"),
    "l535": os.getenv("l535_user")
}

password = {
    "l900": os.getenv("l900_pass"),
    "l535": os.getenv("l535_pass")
}

ip = {
    "l900": os.getenv("l900_ip"),
    "l535": os.getenv("l535_ip")
}


class L900:
    def __init__(self):
        self.ip = ip["l900"]
        self.username = username["l900"]
        self.password = password["l900"]
        self.client = ApiClient(self.username, self.password)
        self.device = None

    async def connect(self):
        self.device = await self.client.l900(self.ip)

    async def turn_on(self):
        if not self.device:
            await self.connect()
        await self.device.on()

    async def turn_off(self):
        if not self.device:
            await self.connect()
        await self.device.off()

    async def set_colour(self,colour):
        if not self.device:
            await self.connect()
        if colour == "red":
            await self.device.set_color(Color.OrangeRed)
        elif colour == "blue":
            await self.device.set_color(Color.LightSkyBlue)
        elif colour == "green":
            await self.device.set_color(Color.LightGreen)


class L535:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.ip = ip["l535"]
            cls._instance.username = username["l535"]
            cls._instance.password = password["l535"]
            cls._instance.client = ApiClient(cls._instance.username, cls._instance.password)
            cls._instance.device = None
        return cls._instance

    async def connect(self):
        self.device = await self.client.l535(self.ip)

    async def turn_on(self):
        if not self.device:
            await self.connect()
        await self.device.on()

    async def turn_off(self):
        if not self.device:
            await self.connect()
        await self.device.off()

    
    async def set_colour(self,colour):
        if not self.device:
            await self.connect()
        if colour == "red":
            await self.device.set_color(Color.DarkRed)
        elif colour == "blue":
            await self.device.set_color(Color.LightSkyBlue)
        elif colour == "green":
            await self.device.set_color(Color.LightGreen)



class DeviceFactory:
    @staticmethod
    async def turn_on(device_name: str):
        if device_name.lower() == "l900":
            dev = L900()
            await dev.connect()
            await dev.turn_on()
            return dev
        elif device_name.lower() == "l535":
            dev = L535()
            await dev.connect()
            await dev.turn_on()
            return dev

    @staticmethod
    async def turn_off(device_name: str):
        if device_name.lower() == "l900":
            dev = L900()
            await dev.connect()
            await dev.turn_off()
            return dev
        elif device_name.lower() == "l535":
            dev = L535()
            await dev.connect()
            await dev.turn_off()
            return dev

    @staticmethod
    async def set_colour(device_name: str,colour):
        if device_name.lower() == "l900":
            dev = L900()
            await dev.connect()
            await dev.set_colour(colour)
            return dev
        elif device_name.lower() == "l535":
            dev = L535()
            await dev.connect()
            await dev.set_colour(colour)
            return dev
        





async def main():
    await DeviceFactory.turn_on("l900")

if __name__ == "__main__":
    asyncio.run(main())