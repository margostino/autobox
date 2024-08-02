import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List
from uuid import uuid4
from venv import logger

from fastapi import BackgroundTasks, FastAPI
from pydantic import BaseModel

from autobox.core.simulator import Simulator, prepare_simulation
from autobox.logger.logger import print_banner
from autobox.schemas.simulation_request import SimulationRequest


class SimulationStatus(BaseModel):
    simulation_id: str
    status: str
    details: SimulationRequest
    simulation: Simulator = None


class SimulationStatusResponse(BaseModel):
    simulation_id: str
    status: str
    details: SimulationRequest


running_simulations: Dict[str, SimulationStatus] = {}
simulations_lock = asyncio.Lock()
app = FastAPI()


async def get_simulation_status(simulation_id: str):
    async with simulations_lock:
        simulation_status = running_simulations.get(simulation_id)
    return simulation_status


async def update_simulation_status(simulation_id: str, status: str):
    async with simulations_lock:
        simulation_status = running_simulations.get(simulation_id)
        if simulation_status is not None:
            simulation_status.status = status
    return simulation_status


@app.get("/simulations", response_model=List[SimulationStatusResponse])
async def get_simulations():
    async with simulations_lock:
        simulations = [
            simulation_status for _, simulation_status in running_simulations.items()
        ]

    simulation_response = [
        SimulationStatusResponse(**simulation.dict(exclude={"simulation"}))
        for simulation in simulations
    ]
    return simulation_response


@app.post("/simulations/{simulation_id}/abort")
async def abort_simulation(simulation_id: str):
    simulation_status = await update_simulation_status(simulation_id, "aborted")
    simulation_status.simulation.abort()
    return {"simulation_id": simulation_id, "status": "aborted"}


async def run_simulation_task(simulation_id: str, request: SimulationRequest):
    try:
        simulation = prepare_simulation(request)
        async with simulations_lock:
            running_simulations[simulation_id] = SimulationStatus(
                simulation_id=simulation_id,
                status="in progress",
                details=request,
                simulation=simulation,
            )
        await simulation.run(timeout=request.simulation.timeout)
        simulation_status = await get_simulation_status(simulation_id)
        if simulation_status.status != "aborted":
            await update_simulation_status(simulation_id, "completed")
    except Exception as e:
        logger.error("Error preparing simulation: %s", e)
        await update_simulation_status(simulation_id, "failed")


def run_async_in_thread(async_func, *args):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(async_func(*args))
    loop.close()


@app.post("/simulations")
async def post_simulations(
    request: SimulationRequest, background_tasks: BackgroundTasks
):
    simulation_id = str(uuid4())
    executor = ThreadPoolExecutor(max_workers=1)

    background_tasks.add_task(
        executor.submit,
        run_async_in_thread,
        run_simulation_task,
        simulation_id,
        request,
    )

    # loop = asyncio.get_event_loop()
    # loop.run_in_executor(executor, run_async_in_thread, run_simulation_task, request)

    return {"status": "in progress", "simulation_id": simulation_id}


if __name__ == "__main__":
    import uvicorn

    print_banner()

    uvicorn.run(app, host="127.0.0.1", port=8000)
