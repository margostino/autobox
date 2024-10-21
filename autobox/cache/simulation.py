import asyncio
from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel, PrivateAttr

from autobox.core.simulation import Simulation


class SimulationCache(BaseModel):
    simulations: Dict[str, Simulation] = {}
    _lock: asyncio.Lock = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        self._lock = asyncio.Lock()

    async def get_simulation_status(self, simulation_id: str):
        async with self._lock:
            simulation_status = self.simulations.get(simulation_id, None)
        return simulation_status

    async def get_simulation_metrics(self, simulation_id: str):
        async with self._lock:
            simulation_status = self.simulations.get(simulation_id, None)
            if simulation_status is not None:
                return simulation_status.metrics
        return None

    async def get_all_simulations(self):
        async with self._lock:
            simulations = [
                simulation_status for _, simulation_status in self.simulations.items()
            ]
            simulations.sort(key=lambda x: x.started_at, reverse=True)
        return simulations

    async def update_simulation_status(
        self, simulation_id: str, status: str, finished_at: datetime = None
    ):
        async with self._lock:
            simulation = self.simulations.get(simulation_id)
            if simulation is not None:
                simulation.status = status
                simulation.finished_at = finished_at
                return simulation
            else:
                return None

    async def init_simulation(
        self,
        simulation: Optional[Simulation],
    ):
        async with self._lock:
            self.simulations[simulation.id] = simulation
