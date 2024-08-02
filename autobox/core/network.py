import asyncio
from typing import List

from pydantic import BaseModel

from autobox.core.agent import Agent
from autobox.core.messaging import MessageBroker
from autobox.utils import blue


class Network(BaseModel):
    message_broker: MessageBroker
    workers: List[Agent]
    orchestrator: Agent

    def register_agent(self, worker: Agent):
        self.workers.append(worker)

    async def run(self):
        tasks = [asyncio.create_task(self.orchestrator.run())] + [
            asyncio.create_task(worker.run()) for worker in self.workers
        ]
        await asyncio.gather(*tasks)

    def stop(self):
        for worker in self.workers:
            worker.is_end = True
        self.orchestrator.is_end = True
        print(f"{blue('🔴 Network stopped.')}")
