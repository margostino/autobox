import asyncio
from typing import List

from autobox.network.agent import Agent, MessageBroker, Supervisor


class Network:
    supervisor: Supervisor
    message_broker: MessageBroker
    agents: List[Agent]

    def __init__(
        self, agents: List[Agent], supervisor: Supervisor, message_broker: MessageBroker
    ):
        self.agents = agents
        self.message_broker = message_broker
        self.supervisor = supervisor

    def register_agent(self, agent: Agent):
        self.agents.append(agent)

    async def run(self, input_message: str):
        # Start agents
        tasks = []
        tasks.append(asyncio.create_task(self.supervisor.start(input_message)))

        for agent in self.agents:
            tasks.append(asyncio.create_task(agent.run()))

        a = await asyncio.gather(*tasks)
        print(a)

    def stop(self):
        for agent in self.agents:
            agent.running = False
        print("Network stopped.")
