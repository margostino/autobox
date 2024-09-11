from typing import Optional

from autobox.cache.metrics import MetricsCache
from autobox.cache.simulation import SimulationCache


class Cache:
    _instance: Optional["Cache"] = None

    def __init__(self):
        self.simulation_cache = SimulationCache()

    @classmethod
    def get_instance(cls) -> "Cache":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def init(cls):
        cls.get_instance()

    @classmethod
    def metrics(cls) -> MetricsCache:
        return cls._instance.metrics_cache

    @classmethod
    def simulation(cls) -> SimulationCache:
        return cls.get_instance().simulation_cache
