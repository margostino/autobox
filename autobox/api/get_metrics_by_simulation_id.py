from fastapi import HTTPException

from autobox.cache.cache import Cache
from autobox.transformations.metrics_to_response import transform


async def handle_get_metrics_by_simulation_id(simulation_id: int):
    cache = Cache.simulation()
    metrics = await cache.get_simulation_metrics(simulation_id)
    if metrics is None:
        raise HTTPException(status_code=404, detail="simulation not found")
    return transform(metrics)
