from autobox.cache.cache import Cache
from autobox.schemas.simulation import (
    SimulationStatusAgentResponse,
    SimulationStatusResponse,
)


async def handle_get_simulations():
    cache = Cache.simulation()
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
