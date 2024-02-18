import random

from autobox.agents.base import Agent
from autobox.network.message_broker import Message, MessageBroker

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


class Worker(Agent):
    # supervisor: Supervisor

    def __init__(
        self,
        name: str,
        mailbox,
        message_broker=MessageBroker,
        description: str = None,
    ):
        super().__init__(name, mailbox, message_broker, description)

    async def _handle(self, message: str):
        random_message = random.choice(messages)
        reply = Message(random_message, self.id)
        self.message_broker.mailbox.put_nowait(reply)
        print(f"Worker ({self.name}/{self.id}) handling: {message}")
