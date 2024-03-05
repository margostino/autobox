import asyncio
from typing import List

from autobox.agents.agent import Agent
from autobox.agents.planner import Planner
from autobox.agents.supervisor import Supervisor
from autobox.network.messaging import MessageBroker


class Network:
    supervisor: Supervisor
    message_broker: MessageBroker
    agents: List[Agent]
    running: bool
    planner: Planner

    def __init__(
        self,
        agents: List[Agent],
        supervisor: Supervisor,
        message_broker: MessageBroker,
        planner: Planner,
    ):
        self.agents = agents
        self.supervisor = supervisor
        self.message_broker = message_broker
        self.planner = planner

    def register_agent(self, agent: Agent):
        self.agents.append(agent)

    async def run(self, task: str):
        self.running = True
        plan = self.planner.plan(task)
        print(f"Plan: {plan}")
        async_tasks = [self.supervisor.solve(task), self.listen()]
        task_result = await asyncio.gather(*async_tasks)
        print(task_result)

    async def listen(self):
        while self.running:
            if not self.message_broker.mailbox.empty():
                message = self.message_broker.mailbox.get_nowait()
                self.supervisor.mailbox.put_nowait(message)
            else:
                await asyncio.sleep(1)

    def stop(self):
        for agent in self.agents:
            agent.running = False
        print("Network stopped.")
