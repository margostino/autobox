import asyncio
import random
from asyncio import Queue
from typing import Dict

from autobox.network.mail import Message

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


class Agent:
    id: int
    name: str
    mailbox: Queue
    message_broker: "MessageBroker"
    supervisor: "Supervisor"

    def __init__(self, name: str, mailbox: Queue, message_broker: "MessageBroker"):
        self.id = hash(name) % 1000
        self.name = name
        self.running = True
        self.mailbox = mailbox
        self.message_broker = message_broker

    async def handle_message(self, message: Message):
        print(f"Agent {self.id} received message: {message.value}")
        random_message = random.choice(messages)
        reply_message = Message(
            to_agent_id=message.from_agent_id,
            value=random_message,
            from_agent_id=self.id,
        )
        self.message_broker.publish(reply_message)

    async def run(self):
        count = 0
        while count < 5:
            # while self.running:
            if not self.mailbox.empty():
                message = self.mailbox.get_nowait()
                count += 1
                await self.handle_message(message)
            await asyncio.sleep(1)


class Supervisor:
    name: str
    mailbox: Queue
    entry_agent_id: int
    agents: Dict[int, Agent]
    message_broker: "MessageBroker"

    def __init__(self, name: str, message_broker: "MessageBroker"):
        self.name = name
        self.entry_agent_id = None
        self.agents = {}
        self.mailbox = Queue(maxsize=10 * 2)
        self.message_broker = message_broker

    async def start(self, input_message: str):
        # pick a random agent id distinct from the entry agent id
        from_agent_id = self.entry_agent_id
        while from_agent_id == self.entry_agent_id:
            from_agent_id = random.choice(list(self.agents.keys()))

        message = Message(
            to_agent_id=self.entry_agent_id,
            value=input_message,
            from_agent_id=from_agent_id,
        )
        self.message_broker.publish(message)

    def register_agent(self, agent: Agent, is_initial=False):
        agent.supervisor = self
        self.agents[agent.id] = agent
        self.entry_agent_id = agent.id if is_initial else self.entry_agent_id

    def send(self, message: Message):
        self.message_broker.publish(message)


class MessageBroker:

    def __init__(self):
        self.subscribers = {}

    def subscribe(self, agent: Agent):
        self.subscribers[agent.id] = agent

    def publish(self, message: Message):
        if message.to_agent_id in self.subscribers:
            self.subscribers[message.to_agent_id].mailbox.put_nowait(message)
        else:
            raise ValueError(f"Agent with id {message.to_agent_id} not found")
