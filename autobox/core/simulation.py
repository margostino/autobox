import asyncio
import time
from uuid import uuid4

from pydantic import BaseModel, Field

from autobox.common.logger import Logger
from autobox.core.network import Network
from autobox.utils.console import blue, green, yellow


class Simulation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    network: Network
    timeout: int = Field(default=120)
    logger: Logger

    class Config:
        arbitrary_types_allowed = True

    async def run(self):
        self.logger.info(f"{green('✅ Simulation is running')}")
        start_time = time.time()

        task = asyncio.create_task(self.network.run(self.id))

        try:
            await asyncio.wait_for(task, timeout=self.timeout)
        except asyncio.TimeoutError:
            self.logger.info(f"{yellow('Simulation ended due to timeout.')}")
        finally:
            self.network.stop()
            self.logger.info(f"{blue('🔚 Simulation finished.')}")

        elapsed_time = int(time.time() - start_time)
        self.logger.info(f"{blue(f"⏱️ Elapsed time: {elapsed_time} seconds.")}")

    def abort(self):
        self.network.stop()
        self.logger.info(f"{blue('🔚 Simulation aborted.')}")
