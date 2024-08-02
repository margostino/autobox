from concurrent.futures import ThreadPoolExecutor
from typing import List
from uuid import uuid4

from fastapi import BackgroundTasks, FastAPI, HTTPException

from autobox.cache.simulation import SimulationCache
from autobox.common.logger import print_banner
from autobox.runner.event_loop import EventLoop
from autobox.schemas.simulation import SimulationRequest, SimulationStatusResponse

cache = SimulationCache()
app = FastAPI()


@app.get("/simulations", response_model=List[SimulationStatusResponse])
async def get_simulations():
    simulations = await cache.get_all_simulations()
    simulation_response = [
        SimulationStatusResponse(**simulation.dict(exclude={"simulation"}))
        for simulation in simulations
    ]
    return simulation_response


@app.post("/simulations/{simulation_id}/abort")
async def abort_simulation(simulation_id: str):
    simulation_status = await cache.update_simulation_status(simulation_id, "aborted")
    if simulation_status is not None:
        simulation_status.simulation.abort()
        return {"simulation_id": simulation_id, "status": "aborted"}
    else:
        raise HTTPException(status_code=404, detail="simulation not found")


@app.post("/simulations")
async def post_simulations(
    request: SimulationRequest, background_tasks: BackgroundTasks
):
    simulation_id = str(uuid4())
    executor = ThreadPoolExecutor(max_workers=1)

    event_loop = EventLoop(simulation_id=simulation_id, cache=cache, request=request)

    background_tasks.add_task(executor.submit, event_loop.run)

    # loop = asyncio.get_event_loop()
    # loop.run_in_executor(executor, run_async_in_thread, run_simulation_task, request)

    return {"status": "in progress", "simulation_id": simulation_id}


if __name__ == "__main__":
    import uvicorn

    print_banner()

    uvicorn.run(app, host="127.0.0.1", port=8000)
