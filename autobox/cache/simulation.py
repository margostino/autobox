import asyncio
from typing import Dict

from pydantic import BaseModel

from autobox.schemas.simulation import SimulationStatus


class SimulationCache(BaseModel):
    running_simulations: Dict[str, SimulationStatus] = {}
    simulations_lock = asyncio.Lock()

    async def get_simulation_status(self, simulation_id: str):
        async with self.simulations_lock:
            simulation_status = self.running_simulations.get(simulation_id)
        return simulation_status

    async def update_simulation_status(self, simulation_id: str, status: str):
        async with self.simulations_lock:
            simulation_status = self.running_simulations.get(simulation_id)
            if simulation_status is not None:
                simulation_status.status = status
        return simulation_status
