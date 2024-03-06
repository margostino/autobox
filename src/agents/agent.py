import random

from src.agents.base import BaseAgent
from src.network.messaging import Message

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

    def __init__(self, name: str, description: str = None, tools: dict = None):
        super().__init__(name, description, tools)

    async def _handle(self, message: Message):
        x = self.llm.invoke(message.value)
        random_message = random.choice(messages)
        reply = Message(random_message, self.id)

        print(
            f"Worker ({self.name}/{self.id}) handling message from {message.from_agent_id}: {message.value}"
        )
