import random

from autobox.agents.base import BaseAgent
from autobox.network.messaging import Message, MessageBroker
from autobox.tools.base import BaseTool

messages = [
    "Hello, I am here to help you",
    "I am a bot, I can help you with your queries",
    "I am a player footballer",
    "I am a player cricketer",
    "I like computer games",
    "I wanna be a president",
    "I am a doctor",
    "One day I will go to Everest and climb it",
]


class Agent(BaseAgent):
    # supervisor: Supervisor

    def __init__(
        self,
        name: str,
        mailbox,
        message_broker=MessageBroker,
        description: str = None,
        tools: list[BaseTool] = None,
    ):
        super().__init__(name, mailbox, message_broker, description, tools)

    async def _handle(self, message: Message):
        x = self.llm.invoke(message.value)
        random_message = random.choice(messages)
        reply = Message(random_message, self.id)
        self.message_broker.mailbox.put_nowait(reply)
        print(
            f"Worker ({self.name}/{self.id}) handling message from {message.from_agent_id}: {message.value}"
        )
