import asyncio
from abc import ABC, abstractmethod
from asyncio import Queue
from typing import Any, List

from pydantic import BaseModel, Field, model_validator

from autobox.core.llm import LLM
from autobox.core.messaging import MessageBroker
from autobox.schemas.message import Message
from autobox.utils.console import green


class Agent(BaseModel, ABC):
    name: str
    mailbox: Queue
    message_broker: MessageBroker
    llm: LLM
    task: str
    memory: List[Any] = []
    id: int = Field(init=False)
    is_end: bool = False

    @model_validator(mode="before")
    @classmethod
    def set_id(cls, values):
        name = values.get("name")
        if name is None:
            raise ValueError("name must be set")
        values["id"] = hash(name) % 1000
        return values

    class Config:
        arbitrary_types_allowed = True

    @abstractmethod
    async def handle_message(self, message: Message):
        pass

    async def run(self):
        print(f"{green(f"🟢 Agent {self.name} ({self.id}) is running")}")
        while not self.is_end:
            if not self.mailbox.empty():
                message = self.mailbox.get_nowait()
                await self.handle_message(message)
            await asyncio.sleep(1)
