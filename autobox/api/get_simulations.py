from autobox.cache.cache import Cache
from autobox.transformations.simulations_to_response import transform


async def handle_get_simulations():
    cache = Cache.simulation()
    simulations = await cache.get_all_simulations()
    simulations = sorted(simulations, key=lambda s: s.started_at, reverse=True)
    return transform(simulations)
