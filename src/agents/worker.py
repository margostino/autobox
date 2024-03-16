from llm.openai import LLM
from prompts.worker import WORKER_PROMPT
from src.agents.base import BaseAgent
from src.engine.messaging import Message


class Worker(BaseAgent):

    def __init__(
        self,
        name: str,
        description: str = None,
        tools: dict = None,
        model: str = None,
        router=None,
        verbose: bool = False,
    ):
        super().__init__(name, description, tools, model, router, verbose)
        self.llm = LLM(WORKER_PROMPT)

    async def _handle(self, message: Message):
        self.track(f"handling message from {message.from_agent_name}")
        response = self.llm.invoke(message.value)
        self.record(response)
        reply = Message(response, self.id, self.name)
        self.router.mailbox.put_nowait(reply)
        self.track("reply sent to router")
