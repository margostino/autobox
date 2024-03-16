import asyncio

from src.engine.autobox import Autobox


async def main():
    autobox = Autobox()
    await autobox.run()


asyncio.run(main())
