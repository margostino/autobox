from asyncio import Queue
from typing import Dict

from pydantic import BaseModel

from autobox.common.logger import Logger
from autobox.schemas.message import Message
from autobox.utils.console import green, red


class MessageBroker(BaseModel):
    subscribers: Dict[str, Queue] = {}
    logger: Logger

    class Config:
        arbitrary_types_allowed = True

    def subscribe(self, agent_id: str, mailbox: Queue):
        self.logger.info(f"{green(f"✅ Agent {agent_id} subscribed to message broker")}")
        self.subscribers[agent_id] = mailbox
        self.logger.info(f"📬 Subscribed agent with id {agent_id}")

    def publish(self, message: Message):
        if message.to_agent_id in self.subscribers:
            self.subscribers[message.to_agent_id].put_nowait(message)
        else:
            raise ValueError(f"{red(f"Agent with id {message.to_agent_id} not found")}")
