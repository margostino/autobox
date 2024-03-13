from src.engine.orchestrator import Orchestrator


class Autobox:
    def __init__(self):
        orchestrator = Orchestrator()
        self.simulator = orchestrator.simulator

    async def run(self, task: str, timeout: int = 60):
        await self.simulator.run(task, timeout=timeout)
