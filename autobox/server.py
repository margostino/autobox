from asyncio.log import logger
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import List
from uuid import uuid4

from fastapi import BackgroundTasks, FastAPI, HTTPException, Response, status

from autobox.cache.simulation import SimulationCache
from autobox.common.logger import print_banner
from autobox.core.bootstrap import prepare_simulation
from autobox.runner.event_loop import EventLoop
from autobox.schemas.simulation import (
    InstructionRequest,
    SimulationRequest,
    SimulationStatusAgentResponse,
    SimulationStatusResponse,
)

cache = SimulationCache()
app = FastAPI()


@app.get("/simulations", response_model=List[SimulationStatusResponse])
async def get_simulations():
    simulations = await cache.get_all_simulations()
    # simulation_response = [
    #     SimulationStatusResponse(**simulation.model_dump(exclude={"simulation"}))
    #     for simulation in simulations
    # ]
    simulation_response = [
        SimulationStatusResponse(
            simulation_id=simulation_status.simulation_id,
            status=simulation_status.status,
            details=simulation_status.details,
            started_at=simulation_status.started_at,
            finished_at=simulation_status.finished_at,
            agents=[
                SimulationStatusAgentResponse(id=agent_id, name=agent_name)
                for agent_name, agent_id in simulation_status.simulation.network.orchestrator.worker_ids.items()
            ],
            orchestrator=SimulationStatusAgentResponse(
                id=simulation_status.simulation.network.orchestrator.id,
                name=simulation_status.simulation.network.orchestrator.name,
            ),
        )
        for simulation_status in simulations
    ]
    return simulation_response


@app.get("/simulations/{simulation_id}", response_model=SimulationStatusResponse)
async def get_simulation_by_id(simulation_id: str):
    simulation_status = await cache.get_simulation_status(simulation_id)
    if simulation_status is not None:
        return SimulationStatusResponse(
            simulation_id=simulation_status.simulation_id,
            status=simulation_status.status,
            details=simulation_status.details,
            started_at=simulation_status.started_at,
            finished_at=simulation_status.finished_at,
            agents=[
                SimulationStatusAgentResponse(id=agent_id, name=agent_name)
                for agent_name, agent_id in simulation_status.simulation.network.orchestrator.worker_ids.items()
            ],
            orchestrator=SimulationStatusAgentResponse(
                id=simulation_status.simulation.network.orchestrator.id,
                name=simulation_status.simulation.network.orchestrator.name,
            ),
        )
    else:
        raise HTTPException(status_code=404, detail="simulation not found")


@app.post("/simulations/{simulation_id}/abort")
async def abort_simulation(simulation_id: str):
    simulation_status = await cache.update_simulation_status(simulation_id, "aborted")
    if simulation_status is not None:
        simulation_status.simulation.abort()
        return {"simulation_id": simulation_id, "status": "aborted"}
    else:
        raise HTTPException(status_code=404, detail="simulation not found")


@app.post("/simulations/{simulation_id}/agents/{agent_id}/instruction")
async def update_simulation_instruction(
    simulation_id: str, agent_id: str, request: InstructionRequest, response: Response
):
    simulation_status = await cache.get_simulation_status(simulation_id)
    if simulation_status is None:
        raise HTTPException(status_code=404, detail="simulation not found")
    # TODO: validate if agent_id exists
    simulation_status.simulation.network.send_intruction_for_workers(
        agent_id=int(agent_id), instruction=request.instruction
    )
    response.status_code = status.HTTP_200_OK
    return response


@app.post("/simulations")
async def post_simulations(
    request: SimulationRequest, background_tasks: BackgroundTasks, response: Response
):
    simulation_id = str(uuid4())

    try:
        simulation = prepare_simulation(request)
        await cache.init_simulation(simulation_id, "in progress", request, simulation)
        executor = ThreadPoolExecutor(max_workers=1)
        event_loop = EventLoop(
            simulation_id=simulation_id, cache=cache, simulation=simulation
        )
        background_tasks.add_task(executor.submit, event_loop.run)

        # loop = asyncio.get_event_loop()
        # loop.run_in_executor(executor, run_async_in_thread, run_simulation_task, request)
        response.status_code = status.HTTP_201_CREATED
        return {
            "status": "in progress",
            "simulation_id": simulation_id,
            "agents": [
                {"name": agent.name, "id": agent.id}
                for agent in simulation.network.workers
            ],
        }
    except Exception as e:
        logger.error("Error preparing simulation: %s", e)
        await cache.update_simulation_status(simulation_id, "failed", datetime.now())
        return {"status": "failed", "simulation_id": simulation_id, "error": str(e)}


if __name__ == "__main__":
    import uvicorn

    print_banner()

    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
