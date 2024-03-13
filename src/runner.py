import asyncio

from src.engine.autobox import Autobox


async def main():
    autobox = Autobox()
    await autobox.run("Research about Black Holes and print the highlights in Spanish.")


asyncio.run(main())
