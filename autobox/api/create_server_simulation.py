from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from fastapi import BackgroundTasks, Response, status

from autobox.bootstrap.bootstrap import prepare_simulation
from autobox.cache.cache import Cache
from autobox.common.logger import Logger
from autobox.runner.event_loop import EventLoop
from autobox.schemas.simulation import SimulationRequest


async def handle_create_server_simulation(
    request: SimulationRequest, background_tasks: BackgroundTasks, response: Response
):
    simulation_id: str = None
    logger = Logger.get_instance()
    cache = Cache.simulation()

    try:
        simulation = await prepare_simulation(request)
        simulation_id = simulation.id
        await cache.update_simulation_status(simulation_id, "in progress")
        executor = ThreadPoolExecutor(max_workers=1)
        event_loop = EventLoop(
            simulation_id=simulation.id,
            cache=cache,
            simulation=simulation,
        )
        background_tasks.add_task(executor.submit, event_loop.run)

        # loop = asyncio.get_event_loop()
        # loop.run_in_executor(executor, run_async_in_thread, run_simulation_task, request)
        response.status_code = status.HTTP_201_CREATED
        return {
            "status": "in progress",
            "simulation_id": simulation.id,
            "agents": [
                {"name": agent.name, "id": agent.id}
                for agent in simulation.network.workers
            ],
        }
    except Exception as e:
        logger.error("Error preparing simulation: %s", e)
        await cache.update_simulation_status(simulation_id, "failed", datetime.now())
        return {"status": "failed", "simulation_id": simulation_id, "error": str(e)}
