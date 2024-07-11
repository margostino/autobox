import asyncio
import time

from autobox.core.network import Network
from autobox.utils import blue, green, yellow


class Simulator:
    network: Network

    def __init__(self, network: Network):
        self.network = network

    async def run(self, timeout: int = 120):
        print(f"{green('✅ Autobox is running')}")
        start_time = time.time()

        # Start network
        task = asyncio.create_task(self.network.run())

        try:
            await asyncio.wait_for(task, timeout=timeout)
        except asyncio.TimeoutError:
            print(f"{yellow('Simulation ended due to timeout.')}")
        finally:
            self.network.stop()            
            print(f"{blue('🔚 Simulation finished.')}")

        elapsed_time = int(time.time() - start_time)
        print(f"{blue(f"⏱️ Elapsed time: {elapsed_time} seconds.")}")
