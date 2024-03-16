import os

from src.engine.orchestrator import Orchestrator
from utils.loaders import load_config


class Autobox:
    def __init__(self):
        config = load_config(os.getenv("AUTOBOX_CONFIG_PATH"))
        orchestrator = Orchestrator(config)
        self.config = config
        self.simulator = orchestrator.simulator

    async def run(self):
        task = self.config["tasks"][0]["task"]  # TODO: Add support for multiple tasks
        timeout = self.config["simulator"]["timeout"]
        await self.simulator.run(task, timeout=timeout)
