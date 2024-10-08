import asyncio
from typing import List

from pydantic import BaseModel

from autobox.common.logger import Logger
from autobox.core.agents.evaluator import Evaluator
from autobox.core.agents.orchestrator import Orchestrator
from autobox.core.agents.utils.messaging import MessageBroker
from autobox.core.agents.worker import Worker
from autobox.schemas.message import Message
from autobox.utils.console import blue


class Network(BaseModel):
    message_broker: MessageBroker
    workers: List[Worker]
    orchestrator: Orchestrator
    evaluator: Evaluator
    logger: Logger

    class Config:
        arbitrary_types_allowed = True

    def register_agent(self, worker: Worker):
        self.workers.append(worker)

    async def run(self, simulation_id: str):
        self.message_broker.publish(
            Message(value=None, to_agent_id=self.orchestrator.id)
        )
        tasks = (
            [asyncio.create_task(self.orchestrator.run(simulation_id))]
            + [asyncio.create_task(self.evaluator.run(simulation_id))]
            + [
                asyncio.create_task(worker.run(simulation_id))
                for worker in self.workers
            ]
        )
        await asyncio.gather(*tasks)

    def stop(self):
        for worker in self.workers:
            worker.is_end = True
        self.orchestrator.is_end = True
        self.logger.info(f"{blue('🔴 Network stopped.')}")

    def send_intruction_for_workers(self, agent_id: int, instruction: str):
        self.message_broker.publish(Message(value=instruction, to_agent_id=agent_id))
