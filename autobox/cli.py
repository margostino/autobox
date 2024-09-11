import asyncio
import sys

from autobox.bootstrap.bootstrap import prepare_simulation
from autobox.cache.cache import Cache
from autobox.common.logger import Logger
from autobox.schemas.simulation import SimulationRequest


async def run_local_simulation(simulation_request: SimulationRequest):
    logger = Logger.get_instance()
    cache = Cache.simulation()

    try:
        simulation = await prepare_simulation(simulation_request)
        logger.info(f"Starting local simulation ({simulation.id})...")
        await cache.update_simulation_status(simulation.id, "in progress")
        asyncio.run(simulation.run())
    except Exception as e:
        logger.error(f"Simulation encountered an error: {str(e)}")
        sys.exit(1)
    logger.info("Simulation finished successfully.")
