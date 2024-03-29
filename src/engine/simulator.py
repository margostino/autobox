import asyncio
import time

from src.engine.network import Network


class Simulator:
    network: Network

    def __init__(self, network: Network):
        self.network = network

    async def run(self, task: str, timeout: int = 60):
        print("[Simulator] Autobox started...")
        start_time = time.time()

        # Start network
        async_task = asyncio.create_task(self.network.run(task))

        try:
            await asyncio.wait_for(async_task, timeout=timeout)
        except asyncio.TimeoutError:
            print("[Simulator] Simulation ended due to timeout.")
        finally:
            self.network.stop()
            print("[Simulator] Simulation finished.")

        elapsed_time = int(time.time() - start_time)
        print(f"[Simulator] Elapsed time: {elapsed_time} seconds.")
