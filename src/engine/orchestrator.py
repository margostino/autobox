import asyncio
import importlib
from typing import Dict

from dotenv import load_dotenv

from src.agents.router import Router
from src.agents.supervisor import Supervisor
from src.agents.worker import Worker
from src.engine.network import Network
from src.engine.simulator import Simulator
from src.tools.base import BaseTool

load_dotenv()


class Orchestrator:

    def __init__(self, config: Dict = None):
        tools = {}
        for tool in config["tools"]:
            tool_name = tool["name"]
            module_path = f"config.tools.{tool_name}"
            module = importlib.import_module(module_path)
            function = getattr(module, tool_name)
            tool["function"] = function
            tool = BaseTool(**tool)
            tools[tool_name] = tool

        router = Router(name="Router", tools=tools)
        workers: Dict[int, Worker] = {}
        for worker in config["agents"]:
            worker_tools = {}
            for tool_name in worker["tools"]:
                worker_tools[tool_name] = tools[tool_name]
            worker["tools"] = worker_tools
            worker["router"] = router
            new_worker = Worker(**worker)
            workers[new_worker.id] = new_worker

        router.register_workers(workers)
        supervisor = Supervisor(name="Supervisor", workers=workers)
        network = Network(workers=workers, supervisor=supervisor, router=router)

        self.simulator = Simulator(network)

    def run(self):
        asyncio.run(
            self.simulator.run(
                task="We need to come up with a bi-collateral agreement to fight Climate Change"
            )
        )
