from asyncio import Queue
from typing import Dict

from pydantic import BaseModel

from autobox.core.mail import Message
from autobox.utils import green, red


class MessageBroker(BaseModel):
    subscribers: Dict[str, Queue] = {}

    class Config:
        arbitrary_types_allowed = True

    def subscribe(self, agent_id: str, mailbox: Queue):
        print(f"{green(f"✅ Agent {agent_id} subscribed to message broker")}")
        self.subscribers[agent_id] = mailbox
        print(f"📬 Subscribed agent with id {agent_id}")

    def publish(self, message: Message):
        if message.to_agent_id in self.subscribers:
            self.subscribers[message.to_agent_id].put_nowait(message)
        else:
            raise ValueError(f"{red(f"Agent with id {message.to_agent_id} not found")}")
