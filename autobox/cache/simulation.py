import asyncio
from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel

from autobox.core.simulation import Simulation
from autobox.schemas.simulation import SimulationRequest, SimulationStatus


class SimulationCache(BaseModel):
    simulations: Dict[str, SimulationStatus] = {}
    lock: asyncio.Lock = asyncio.Lock()

    class Config:
        arbitrary_types_allowed = True

    async def get_simulation_status(self, simulation_id: str):
        async with self.lock:
            simulation_status = self.simulations.get(simulation_id)
        return simulation_status

    async def get_all_simulations(self):
        async with self.lock:
            simulations = [
                simulation_status for _, simulation_status in self.simulations.items()
            ]
            simulations.sort(key=lambda x: x.started_at, reverse=True)
        return simulations

    async def update_simulation_status(
        self, simulation_id: str, status: str, finished_at: datetime = None
    ):
        async with self.lock:
            simulation_status = self.simulations.get(simulation_id)
            if simulation_status is not None:
                simulation_status.status = status
                simulation_status.finished_at = finished_at
                return simulation_status
            else:
                return None

    async def init_simulation(
        self,
        simulation_id: str,
        status: str,
        request: Optional[SimulationRequest],
        simulation: Optional[Simulation],
    ):
        async with self.lock:
            self.simulations[simulation_id] = SimulationStatus(
                simulation_id=simulation_id,
                status=status,
                details=request,
                simulation=simulation,
                started_at=datetime.now(),
            )
