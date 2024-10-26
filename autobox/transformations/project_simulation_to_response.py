from autobox.core.simulation import Simulation
from autobox.schemas.simulation import ProjectSimulationResponse


def transform(simulation: Simulation) -> ProjectSimulationResponse:
    return ProjectSimulationResponse(
        id=simulation.id,
        name=simulation.name,
        status=simulation.status,
        progress=simulation.progress,
        started_at=simulation.started_at,
        finished_at=simulation.finished_at,
        aborted_at=simulation.aborted_at,
    )
