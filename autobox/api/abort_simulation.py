from fastapi import HTTPException

from autobox.cache.cache import Cache


async def handle_abort_simulation(simulation_id: int):
    cache = Cache.simulation()
    simulation = await cache.update_simulation_status(simulation_id, "aborted")
    if simulation is not None:
        simulation.abort()
        return {"simulation_id": simulation_id, "status": "aborted"}
    else:
        raise HTTPException(status_code=404, detail="simulation not found")
