import asyncio
from abc import ABC, abstractmethod

from pydantic import BaseModel, Field

from engine.messaging import Message


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
        verbose: bool = False,
    ):
        self.id = hash(name) % 1000
        self.name = name
        self.description = description
        self.mailbox = asyncio.Queue()
        self.memory = []
        self.running = True
        self.tools = tools
        self.router = router
        self.verbose = verbose

    async def listen(self):
        while self.running:
            if not self.mailbox.empty():
                message = self.mailbox.get_nowait()
                await self._handle(message)
            else:
                await asyncio.sleep(1)

    def stop(self):
        self.running = False

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

    def logger(self, message):
        print(f"({self.name}) {message}")
