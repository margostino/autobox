from autobox.core.agent import Agent
from autobox.core.mail import Message
from autobox.utils import green, red


class MessageBroker:

    def __init__(self):
        self.subscribers = {}

    def subscribe(self, agent: Agent):
        print(f"{green(f"✅ Agent {agent.name} ({agent.id}) subscribed to message broker")}")
        self.subscribers[agent.id] = agent

    def publish(self, message: Message):
        if message.to_agent_id in self.subscribers:
            self.subscribers[message.to_agent_id].mailbox.put_nowait(message)
        else:
            raise ValueError(f"{red(f"Agent with id {message.to_agent_id} not found")}")
