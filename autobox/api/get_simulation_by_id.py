from fastapi import HTTPException

from autobox.cache.cache import Cache
from autobox.transformations.simulation_to_response import transform


async def handle_get_simulation_by_id(id: int):
    cache = Cache.simulation()
    simulation = await cache.get_simulation_status(id)
    if simulation is not None:
        return transform(simulation)
    else:
        raise HTTPException(status_code=404, detail="simulation not found")
