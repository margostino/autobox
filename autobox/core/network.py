import asyncio
from typing import List

from autobox.core.agent import Agent, Supervisor
from autobox.core.messaging import MessageBroker
from autobox.core.orchestrator import Orchestrator
from autobox.utils import blue


class Network:
    supervisor: Supervisor
    message_broker: MessageBroker
    agents: List[Agent]
    orchestrator: Orchestrator

    def __init__(
        self,
        agents: List[Agent],
        supervisor: Supervisor,
        orchestrator: Orchestrator,
        message_broker: MessageBroker,
    ):
        self.agents = agents
        self.message_broker = message_broker
        self.supervisor = supervisor
        self.orchestrator = orchestrator

    def register_agent(self, agent: Agent):
        self.agents.append(agent)

    async def run(self):
        # Start agents
        # self.message_broker.publish(
        #     Message(
        #         to_agent_id=self.agents[0].id,
        #         value=input_message,
        #         from_agent_id=None,
        #     )
        # )
        tasks = [
            # asyncio.create_task(self.supervisor.start(input_message)),
            asyncio.create_task(self.orchestrator.run())
        ] + [asyncio.create_task(agent.run()) for agent in self.agents]
        a = await asyncio.gather(*tasks)
        print(a)

    def stop(self):
        for agent in self.agents:
            agent.running = False
        print(f"{blue('Network stopped.')}")
