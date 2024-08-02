import asyncio
from asyncio.log import logger
from datetime import datetime

from openai import BaseModel

from autobox.cache.simulation import SimulationCache
from autobox.core.simulation import prepare_simulation
from autobox.schemas.simulation import SimulationRequest


class EventLoop(BaseModel):
    simulation_id: str
    cache: SimulationCache
    request: SimulationRequest

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.start_simulation(self.simulation_id, self.request))
        loop.close()

    async def start_simulation(self, simulation_id: str, request: SimulationRequest):
        try:
            simulation = prepare_simulation(request)
            await self.cache.init_simulation(
                simulation_id, "in progress", request, simulation
            )
            await simulation.run(timeout=request.simulation.timeout)
            simulation_status = await self.cache.get_simulation_status(simulation_id)
            if simulation_status.status != "aborted":
                await self.cache.update_simulation_status(
                    simulation_id, "completed", datetime.now()
                )
        except Exception as e:
            logger.error("Error preparing simulation: %s", e)
            await self.cache.update_simulation_status(
                simulation_id, "failed", datetime.now()
            )
