import asyncio
from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel, PrivateAttr

from autobox.core.simulation import Simulation
from autobox.schemas.metrics import Metric
from autobox.schemas.simulation import SimulationRequest, SimulationStatus


class SimulationCache(BaseModel):
    simulations: Dict[str, SimulationStatus] = {}
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
            simulation_status = self.simulations.get(simulation_id)
            if simulation_status is not None:
                simulation_status.status = status
                simulation_status.finished_at = finished_at
                return simulation_status
            else:
                return None

    async def init_simulation(
        self,
        status: str,
        request: Optional[SimulationRequest],
        simulation: Optional[Simulation],
        metrics: Dict[str, Metric],
    ):
        async with self._lock:
            self.simulations[simulation.id] = SimulationStatus(
                simulation_id=simulation.id,
                status=status,
                details=request,
                simulation=simulation,
                started_at=datetime.now(),
                metrics=metrics,
            )
