import asyncio
from typing import Dict, List

from pydantic import BaseModel, PrivateAttr


class TracesCache(BaseModel):
    traces: Dict[str, List[str]] = {}
    _lock: asyncio.Lock = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        self._lock = asyncio.Lock()

    def get_or_create_traces_by(self, simulation_id: str):
        return self.traces.setdefault(simulation_id, [])

    def get_traces_by(self, simulation_id: str):
        return self.traces.get(simulation_id, [])

    async def append_trace(self, simulation_id: str, trace: str):
        async with self._lock:
            traces = self.traces.get(simulation_id)
            traces.append(trace)
            return traces

    async def init_traces(
        self,
        simulation_id: str,
    ):
        async with self._lock:
            self.traces[simulation_id] = []
