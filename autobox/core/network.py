import asyncio
from typing import List

from autobox.core.agent import Agent
from autobox.core.messaging import MessageBroker
from autobox.core.orchestrator import Orchestrator
from autobox.utils import blue


class Network:
    message_broker: MessageBroker
    agents: List[Agent]
    orchestrator: Orchestrator

    def __init__(
        self,
        agents: List[Agent],
        orchestrator: Orchestrator,
        message_broker: MessageBroker,
    ):
        self.agents = agents
        self.message_broker = message_broker
        self.orchestrator = orchestrator

    def register_agent(self, agent: Agent):
        self.agents.append(agent)

    async def run(self):
        # Start agents
        tasks = [asyncio.create_task(self.orchestrator.run())] + [
            asyncio.create_task(agent.run()) for agent in self.agents
        ]
        await asyncio.gather(*tasks)

    def stop(self):
        for agent in self.agents:
            agent.running = False
        print(f"{blue('🔴 Network stopped.')}")
