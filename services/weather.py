import python_weather
import asyncio



async def get_temperature(city: str) -> None:

  async with python_weather.Client(unit=python_weather.METRIC) as client:
    weather = await client.get(city)

    return weather.temperature



if __name__ == '__main__':
  print(asyncio.run(get_temperature("Kavala")))