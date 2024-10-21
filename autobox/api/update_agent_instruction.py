from fastapi import HTTPException, Response, status

from autobox.cache.cache import Cache
from autobox.schemas.simulation import InstructionRequest


async def handle_update_simulation_instruction(
    simulation_id: str, agent_id: str, request: InstructionRequest, response: Response
):
    cache = Cache.simulation()
    simulation_status = await cache.get_simulation_status(simulation_id)
    if simulation_status is None:
        raise HTTPException(status_code=404, detail="simulation not found")
    # TODO: validate if agent_id exists
    simulation_status.network.send_intruction_for_workers(
        agent_id=int(agent_id), instruction=request.instruction
    )
    response.status_code = status.HTTP_200_OK
    return response
