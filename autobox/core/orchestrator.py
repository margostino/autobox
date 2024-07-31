import asyncio
import json
from asyncio import Queue
from typing import Dict

from openai.types.chat import ChatCompletion

from autobox.core.agent import Agent
from autobox.core.llm import LLM
from autobox.core.mail import Message
from autobox.core.messaging import MessageBroker
from autobox.utils import (blue, extract_chat_completion, green,
                           spin_with_handler, yellow)


class Orchestrator(Agent):
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
        self.iterations_counter = 0

    async def run(self):
        print(f"{green(f"🟢 Orchestrator {self.name} ({self.id}) is running")}")
        # TODO: ack agents?

        if self.is_initial:
            self.is_initial = False
            print(f"{blue(f"📋 Task: {self.task}")}")
            await self.handle_message(Message(value=None))

        while not self.is_end:
            if not self.mailbox.empty():
                message = self.mailbox.get_nowait()
                await self.handle_message(message)
            await asyncio.sleep(1)

    async def handle_message(self, message: Message):
        if message.from_agent_id is None:
            print(f"{blue(f"📬 Orchestrator {self.name} ({self.id}) preparing initial message...")}")
        else:
            from_agent_name = self.agent_names[message.from_agent_id]
            print(f"{blue(f"📨 Orchestrator {self.name} ({self.id}) handling message from {from_agent_name}...")}")
            print(f"{yellow(f"🗣️ {from_agent_name} said:")} {message.value}")
            self.memory.append(f"{from_agent_name} said: {message.value}")

        agent_decisions = self.memory

        chat_completion_messages = [
            {
                "role": "user",
                "content": f"Previous partial decisions, suggestions, requirements and more from other agents: {json.dumps(agent_decisions)}",
            },
        ]

        completion = spin_with_handler(f"🧠 Orchestrator {self.name} ({self.id}) is thinking...", Orchestrator.handle_spin_completion, lambda: self.llm.think(self.name, chat_completion_messages))
        
        tool_calls = completion.choices[0].message.tool_calls
        reply_messages = []
        if tool_calls is not None and len(tool_calls):
            self.iterations_counter += 1
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

        if self.is_end:
            asyncio.sleep(4)
            value = completion.choices[0].message.content
            print(f"{green('Orchestrator is ending process...')}")
            print('\n\n')
            print(f"{blue('🔄 Total iterations:')} {self.iterations_counter}")
            print(f"{blue('🏁 Final result:')} {value}")
            print('\n\n')

    def register_agent(self, agent: Agent, is_initial=False):
        agent.supervisor = self
        self.agents[agent.id] = agent
        self.entry_agent_id = agent.id if is_initial else self.entry_agent_id

    def send(self, message: Message):
        self.message_broker.publish(message)

    @staticmethod
    def handle_spin_completion(chat_completion: ChatCompletion) -> str:
        message, should_call_tools = extract_chat_completion(chat_completion)

        if not should_call_tools:
            return "Do not need more iterations. Task is done."
        
        return f"Orchestrator decided to call tools: {[message['function_name'] for message in message]}"
