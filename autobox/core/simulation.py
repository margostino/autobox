import asyncio
from datetime import datetime
from typing import Dict
from uuid import uuid4

from pydantic import BaseModel, Field

from autobox.common.logger import Logger
from autobox.core.network import Network
from autobox.schemas.metrics import Metric
from autobox.schemas.simulation import SimulationStatus
from autobox.utils.console import blue, green, yellow


class Simulation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    status: SimulationStatus = Field(default=SimulationStatus.in_progress)
    started_at: datetime = Field(default=None)
    finished_at: datetime = Field(default=None)
    network: Network
    timeout: int = Field(default=120)
    logger: Logger
    metrics: Dict[str, Metric] = Field(default={})
    summary: str = Field(default=None)
    progress: int = Field(default=0)

    class Config:
        arbitrary_types_allowed = True

    async def run(self):
        self.logger.info(f"{green('✅ Simulation is running')}")
        self.started_at = datetime.now()

        task = asyncio.create_task(self.network.run(self.id))

        try:
            await asyncio.wait_for(task, timeout=self.timeout)
        except asyncio.TimeoutError:
            self.logger.info(f"{yellow('Simulation ended due to timeout.')}")
        finally:
            self.network.stop()
            self.logger.info(f"{blue('🔚 Simulation finished.')}")

        self.finished_at = datetime.now()
        elapsed_time = int((self.finished_at - self.started_at).total_seconds())
        self.progress = 100
        self.logger.info(f"{blue(f"⏱️ Elapsed time: {elapsed_time} seconds.")}")

    def abort(self):
        self.network.stop()
        self.logger.info(f"{blue('🔚 Simulation aborted.')}")
