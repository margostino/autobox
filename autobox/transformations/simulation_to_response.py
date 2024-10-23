from autobox.core.simulation import Simulation
from autobox.schemas.simulation import SimulationAgentResponse, SimulationResponse


def transform(simulation: Simulation) -> SimulationResponse:
    return SimulationResponse(
        id=simulation.id,
        name=simulation.name,
        status=simulation.status,
        started_at=simulation.started_at,
        finished_at=simulation.finished_at,
        summary=simulation.summary,
        progress=simulation.progress,
        public_dashboard_url=simulation.public_dashboard_url,
        internal_dashboard_url=simulation.internal_dashboard_url,
        agents=[
            SimulationAgentResponse(id=agent_id, name=agent_name)
            for agent_name, agent_id in simulation.network.orchestrator.worker_ids.items()
        ],
        orchestrator=SimulationAgentResponse(
            id=simulation.network.orchestrator.id,
            name=simulation.network.orchestrator.name,
        ),
        evaluator=SimulationAgentResponse(
            id=simulation.network.evaluator.id,
            name=simulation.network.evaluator.name,
        ),
    )
