import asyncio
from abc import ABC, abstractmethod

from pydantic import BaseModel, Field

from src.engine.messaging import Message
from src.llm.openai import LLM


class LLMInput(BaseModel):
    input: int = Field(
        description="should be a number",
    )


class BaseAgent(ABC):

    def __init__(
        self,
        name: str,
        description: str,
        tools: dict = None,
        model: str = None,
        router=None,
    ):
        self.id = hash(name) % 1000
        self.name = name
        self.description = description
        self.mailbox = asyncio.Queue()
        self.memory = []
        self.llm = LLM()
        self.running = True
        self.tools = tools
        self.router = router

    async def listen(self):
        while self.running:
            if not self.mailbox.empty():
                message = self.mailbox.get_nowait()
                # print(f"Agent {self.name} received message: {message}")
                await self._handle(message)
            else:
                await asyncio.sleep(1)

    @abstractmethod
    async def _handle(self, message: Message):
        pass

    def to_prompt(self):
        return {
            "name": self.name,
            "id": self.id,
            "description": self.description,
            "tools": self.tools.keys(),
        }
