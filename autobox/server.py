import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List
from uuid import uuid4

from fastapi import BackgroundTasks, FastAPI
from pydantic import BaseModel

from autobox.core.simulator import prepare_simulation
from autobox.logger.logger import print_banner
from autobox.schemas.simulation_request import SimulationRequest

running_tasks: Dict[str, SimulationRequest] = {}
tasks_lock = asyncio.Lock()


class TaskStatus(BaseModel):
    task_id: str
    status: str
    details: SimulationRequest


app = FastAPI()


@app.get("/simulations", response_model=List[TaskStatus])
async def get_simulations():
    async with tasks_lock:
        tasks = [task_status for _, task_status in running_tasks.items()]
    return tasks


async def run_simulation_task(task_id: str, request: SimulationRequest):
    simulation = prepare_simulation(request)
    await simulation.run(timeout=request.simulation.timeout)
    async with tasks_lock:
        running_tasks[task_id] = TaskStatus(
            task_id=task_id, status="completed", details=request
        )


def run_async_in_thread(async_func, *args):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(async_func(*args))
    loop.close()


@app.post("/simulations")
async def post_simulations(
    request: SimulationRequest, background_tasks: BackgroundTasks
):
    task_id = str(uuid4())
    async with tasks_lock:
        running_tasks[task_id] = TaskStatus(
            task_id=task_id, status="in progress", details=request
        )

    executor = ThreadPoolExecutor(max_workers=1)

    background_tasks.add_task(
        executor.submit, run_async_in_thread, run_simulation_task, task_id, request
    )

    # loop = asyncio.get_event_loop()
    # loop.run_in_executor(executor, run_async_in_thread, run_simulation_task, request)

    return {"status": "in progress", "task_id": task_id}


if __name__ == "__main__":
    import uvicorn

    print_banner()

    uvicorn.run(app, host="127.0.0.1", port=8000)
