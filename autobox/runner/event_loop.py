import asyncio
from asyncio.log import logger
from datetime import datetime

from openai import BaseModel

from autobox.cache.simulation import SimulationCache
from autobox.core.simulation import Simulation


class EventLoop(BaseModel):
    simulation_id: str
    cache: SimulationCache
    simulation: Simulation

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.start_simulation())
        loop.close()

    async def start_simulation(self):
        try:
            self.simulation.plan()
            await self.simulation.run()
            simulation_status = await self.cache.get_simulation_status(
                self.simulation_id
            )
            if simulation_status.status != "aborted":
                await self.cache.update_simulation_status(
                    self.simulation_id, "completed", datetime.now()
                )
        except Exception as e:
            logger.error("Error running simulation: %s", e)
            await self.cache.update_simulation_status(
                self.simulation_id, "failed", datetime.now()
            )
