import asyncio
import json
from asyncio import Queue

from openai.types.chat import ChatCompletion

from autobox.core.llm import LLM
from autobox.core.mail import Message
from autobox.utils import blue, green, spin

# from autobox.core.messaging import MessageBroker

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
    def __init__(
        self,
        name: str,
        mailbox: Queue,
        message_broker: "MessageBroker",
        llm: LLM,
        task: str,
    ):
        self.id = hash(name) % 1000
        self.name = name
        self.running = True
        self.mailbox = mailbox
        self.message_broker = message_broker
        self.llm = llm
        self.memory = []
        self.task = task
        self.is_end = False

    async def send_reply(self, to_agent_id, completion: ChatCompletion):
        value = completion.choices[0].message.content
        reply_message = Message(
            to_agent_id=to_agent_id,
            value=value,
            from_agent_id=self.id,
        )
        self.message_broker.publish(reply_message)
        await asyncio.sleep(1)

    async def handle_message(self, message: Message):
        print(f"{blue(f"Agent {self.name} ({self.id}) handling message from orchestrator...")}")
        to_agent_id = message.from_agent_id
        if message.value == "end":
            print(f"{blue(f"Agent {self.name} ({self.id}) is stopping...")}")
            self.is_end = True
            return

        json_message_value = json.loads(message.value)
        agent_decisions = json_message_value["agent_decisions"]
        arguments = json.loads(json_message_value["arguments"])
        task_status = arguments["task_status"]
        instruction = arguments["instruction"]
        thinking_process = arguments["thinking_process"]

        print(f"{blue(f'Instruction for Agent {self.name} ({self.id}):')} {instruction}")
        print(f"{blue(f'Current task status {self.name} ({self.id}):')} {task_status}")
        print(f"{blue(f'Thinking process {self.name} ({self.id}):')} {thinking_process}")

        self.memory.append(agent_decisions)

        chat_completion_messages = [
            {
                "role": "user",
                "content": f"Final Task: {self.task}",
            },
            {
                "role": "user",
                "content": f"Previous partial decisions, suggestions, requirements and more from other agents: {json.dumps(agent_decisions)}",
            },
            {
                "role": "user",
                "content": f"Current general task status: {task_status}",
            },
            {
                "role": "user",
                "content": f"Instruction: {instruction}",
            },
        ]

        completion = spin(f"Agent {self.name} ({self.id}) is thinking...", lambda: self.llm.think(self.name, chat_completion_messages))

        value = completion.choices[0].message.content
        reply_message = Message(
            to_agent_id=to_agent_id,
            value=value,
            from_agent_id=self.id,
        )
        self.message_broker.publish(reply_message)

    async def run(self):
        print(f"{green(f"Agent {self.name} ({self.id}) is running...")}")
        while not self.is_end:
            if not self.mailbox.empty():
                message = self.mailbox.get_nowait()
                await self.handle_message(message)
            await asyncio.sleep(1)