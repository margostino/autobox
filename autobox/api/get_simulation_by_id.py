from fastapi import HTTPException

from autobox.cache.cache import Cache
from autobox.schemas.simulation import (
    SimulationStatusAgentResponse,
    SimulationStatusResponse,
)


async def handle_get_simulation_by_id(simulation_id: int):
    cache = Cache.simulation()
    simulation_status = await cache.get_simulation_status(simulation_id)
    if simulation_status is not None:
        return SimulationStatusResponse(
            simulation_id=simulation_status.simulation_id,
            status=simulation_status.status,
            details=simulation_status.details,
            started_at=simulation_status.started_at,
            finished_at=simulation_status.finished_at,
            summary=simulation_status.summary,
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
