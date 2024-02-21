import asyncio
from typing import List

from autobox.agents.supervisor import Supervisor
from autobox.agents.worker import Worker
from autobox.network.messaging import MessageBroker


class Network:
    supervisor: Supervisor
    message_broker: MessageBroker
    agents: List[Worker]
    running: bool

    def __init__(
        self,
        agents: List[Worker],
        supervisor: Supervisor,
        message_broker: MessageBroker,
    ):
        self.agents = agents
        self.supervisor = supervisor
        self.message_broker = message_broker

    def register_agent(self, agent: Worker):
        self.agents.append(agent)

    async def run(self, task: str):
        self.running = True
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
