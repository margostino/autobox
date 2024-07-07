import asyncio
import json
from asyncio import Queue
from typing import Dict

from autobox.core.agent import Agent
from autobox.core.llm import LLM
from autobox.core.mail import Message
from autobox.core.messaging import MessageBroker
from autobox.utils import blue, green, spin, yellow


class Orchestrator(Agent):
    name: str
    mailbox: Queue
    entry_agent_id: int
    agents: Dict[int, Agent]
    message_broker: MessageBroker
    agent_ids: Dict[str, int]
    task: str
    is_initial: bool

    def __init__(
        self,
        name: str,
        mailbox: Queue,
        message_broker: MessageBroker,
        llm: LLM,
        agent_ids: Dict[str, int],
        task: str,
        is_initial=True,
    ):
        super().__init__(name, mailbox, message_broker, llm, task)
        self.entry_agent_id = None
        self.agents = {}
        self.mailbox = Queue(maxsize=10 * 2)
        self.agent_ids = agent_ids
        self.agent_names = {value: key for key, value in agent_ids.items()}
        self.is_initial = is_initial

    async def run(self):        
        print(f"{green(f"Orchestrator {self.name} ({self.id}) is running...")}")

        if self.is_initial:
            self.is_initial = False
            print(f"{blue(f"Final task: {self.task}")}")
            await self.handle_message(Message(value=None))

        while not self.is_end:
            if not self.mailbox.empty():
                message = self.mailbox.get_nowait()
                await self.handle_message(message)
            await asyncio.sleep(1)

    async def handle_message(self, message: Message):
        if message.from_agent_id is None:
            print(f"{blue(f"Orchestrator {self.name} ({self.id}) preparing initial message...")}")
        else:
            from_agent_name = self.agent_names[message.from_agent_id]
            print(f"{blue(f"Orchestrator {self.name} ({self.id}) handling message from {from_agent_name}...")}")
            print(f"{yellow(f"{from_agent_name} said:")} {message.value}")
            self.memory.append(f"{from_agent_name} said: {message.value}")

        agent_decisions = self.memory

        chat_completion_messages = [
            {
                "role": "user",
                "content": f"Final Task: {self.task}",
            },
            {
                "role": "user",
                "content": f"Previous partial decisions, suggestions, requirements and more from other agents: {json.dumps(agent_decisions)}",
            },
        ]

        completion = spin(f"Orchestrator {self.name} ({self.id}) is thinking...", lambda: self.llm.think(self.name, chat_completion_messages))
        
        tool_calls = completion.choices[0].message.tool_calls
        reply_messages = []
        if tool_calls is not None and len(tool_calls):
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                agent_id = self.agent_ids[function_name]
                arguments = tool_call.function.arguments
                reply_messages.append(
                    Message(
                        to_agent_id=agent_id,
                        value=json.dumps(
                            {
                                "task": self.task,
                                "agent_decisions": self.memory,
                                "arguments": arguments,
                            }
                        ),
                        from_agent_id=self.id,
                    )
                )
        else:
            self.is_end = True
            value = completion.choices[0].message.content
            print(f"{green('Orchestrator is ending process...')}")
            print(f"{blue(f"Final result: {value}")}")

            reply_messages = [
                Message(
                    to_agent_id=id,
                    value="end",
                    from_agent_id=self.id,
                )
                for id in self.agent_ids.values()
            ]

        for reply_message in reply_messages:
            self.message_broker.publish(reply_message)

    async def start(self, task: str):
        print(f"Orchestrator {self.name} is running...")
        while not self.is_end:
            if not self.mailbox.empty():
                message = self.mailbox.get_nowait()
                agent_name = self.agent_ids[message.from_agent_id]
                self.memory.append(f"{agent_name}: {message.value}")
                await self.handle_message(message)

            if self.is_initial:
                self.is_initial = False
                completion, should_function_call = self.llm.think(
                    [
                        {
                            "role": "user",
                            "content": f"Final Task: {task}",
                        },
                        {
                            "role": "user",
                            "content": "Partial status:",
                        },
                    ],
                    parallel_tool_calls=True,
                )

                if should_function_call:
                    function_name = completion[0].function.name
                    agent_id = self.agent_ids[function_name]
                    arguments = completion[0].function.arguments
                    message = Message(
                        to_agent_id=agent_id,
                        value=json.dumps(
                            {
                                "task": task,
                                "agent_decisions": self.memory,
                                "arguments": arguments,
                            }
                        ),
                        from_agent_id=self.id,
                    )
                    self.message_broker.publish(message)
                else:
                    self.is_end = True
            await asyncio.sleep(1)

    def register_agent(self, agent: Agent, is_initial=False):
        agent.supervisor = self
        self.agents[agent.id] = agent
        self.entry_agent_id = agent.id if is_initial else self.entry_agent_id

    def send(self, message: Message):
        self.message_broker.publish(message)
