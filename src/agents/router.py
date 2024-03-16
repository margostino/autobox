from typing import Dict

from src.agents.base import BaseAgent
from src.agents.planner import Planner
from src.agents.worker import Worker
from src.engine.messaging import Message
from src.tools.base import BaseTool


class Router(BaseAgent):
    workers: Dict[int, Worker]
    planner: Planner
    current_step = 0

    def __init__(
        self,
        name: str,
        tools: Dict[str, BaseTool] = None,
        verbose: bool = False,
    ):
        super().__init__(
            name=name,
            description="Supervisor",
            verbose=verbose,
        )
        self.tools = tools
        self.plan = None

    async def _handle(self, message: Message):
        if not self.memory:
            task = message.value
            self.plan = self.planner.plan(task)
            self.track(f"task received: {task}")
            self.track(f"plan: {self.plan}")

        if message.from_agent_id is None:
            self.current_step = 0
        else:
            self.current_step += 1

        if self.current_step >= len(self.plan.steps):
            self.track("task completed, stopping router and workers")
            self.record(message.value)
            for worker in self.workers.values():
                worker.stop()
            self.stop()
            return

        to_agent_id = self.plan.steps[self.current_step].agent_id
        to_agent_name = self.plan.steps[self.current_step].agent
        sub_task = self.plan.steps[self.current_step].sub_task

        if message.from_agent_id is None:
            message.value = sub_task
        else:
            message.value = f"""
            {sub_task}
            ```
            {message.value}
            ```
            """
        message.from_agent_id = self.id
        self.track(f"routing message to {to_agent_name} with sub-task: {sub_task}")
        self.workers[to_agent_id].mailbox.put_nowait(message)

    def register_workers(self, workers: Dict[int, Worker]):
        self.workers = workers
        self.generate_planner()

    def register_worker(self, worker: Worker):
        self.workers[worker.id] = worker
        self.generate_planner()

    def generate_planner(self):
        agents_prompt = [worker.to_prompt() for worker in self.workers.values()]
        tools_prompt = [tool.to_prompt() for tool in self.tools.values()]
        self.planner = Planner({"agents": agents_prompt, "tools": tools_prompt})
