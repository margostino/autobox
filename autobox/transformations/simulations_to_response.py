from typing import List

from autobox.core.simulation import Simulation
from autobox.schemas.simulation import SimulationResponse
from autobox.transformations.simulation_to_response import (
    transform as transform_single_simulation,
)


def transform(simulations: List[Simulation]) -> List[SimulationResponse]:
    return [transform_single_simulation(simulation) for simulation in simulations]
