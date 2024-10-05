import asyncio
import json
from typing import Dict

from openai.types.chat import ChatCompletion
from pydantic import Field

from autobox.core.agents.base import BaseAgent
from autobox.schemas.message import Message
from autobox.utils.console import blue, green, spin_with_handler, yellow
from autobox.utils.llm import extract_chat_completion


class Orchestrator(BaseAgent):
    worker_ids: Dict[str, int] = {}
    worker_names: Dict[int, str] = {}
    iterations_counter: int = Field(default=0)
    max_steps: int = Field(default=5)
    instruction: str
    evaluator_id: int

    async def handle_message(self, message: Message):
        if message.from_agent_id is None:
            self.logger.info(f"{blue(f"📬 Orchestrator {self.name} ({self.id}) preparing initial message...")}")
            agent_decisions = []
        else:
            from_agent_name = self.worker_names[message.from_agent_id]
            self.logger.info(f"{blue(f"📨 Orchestrator {self.name} ({self.id}) handling message from {from_agent_name}...")}")
            self.logger.info(f"{yellow(f"🗣️ {from_agent_name} said:")} {message.value}")
            self.memory[from_agent_name].append(f"{from_agent_name} said: {message.value}")
            agent_decisions = self.memory[from_agent_name]

        self.message_broker.publish(Message(
                        to_agent_id=self.evaluator_id,
                        value=json.dumps(
                            {
                                "memory": self.memory,
                                "iterations_counter": self.iterations_counter,
                                "is_first": message.from_agent_id is None,
                            }
                        ),
                        from_agent_id=self.id,
                    ))

        chat_completion_messages = [
            {
                "role": "user",
                "content": f"Your previous thinking process: {json.dumps(self.memory['orchestrator'])}",
            },
            {
                "role": "user",
                "content": f"Previous agents' partial messages: {json.dumps(agent_decisions)}",
            },
            {
                "role": "user",
                "content": f"ITERATION COUNTER: {self.iterations_counter}",
            },
        ]

        completion = (spin_with_handler(f"🧠 Orchestrator {self.name} ({self.id}) is thinking...", Orchestrator.handle_spin_completion, lambda: self.llm.think(self.name, chat_completion_messages))
            if self.is_local_mode
            else self.llm.think(self.name, chat_completion_messages)[0])  # TODO: do it safe

        tool_calls = completion.choices[0].message.tool_calls
        reply_messages = []
        if tool_calls is not None and len(tool_calls):
            self.iterations_counter += 1
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                agent_id = self.worker_ids[function_name]
                arguments = tool_call.function.arguments
                self.memory["orchestrator"].append(f"Orchestrator called {function_name} with arguments: {arguments}")
                reply_messages.append(
                    Message(
                        to_agent_id=agent_id,
                        value=json.dumps(
                            {
                                "task": self.task,
                                # "agent_decisions": self.memory,
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
                for id in self.worker_ids.values()
            ]

        for reply_message in reply_messages:
            self.message_broker.publish(reply_message)

        if self.is_end:
            asyncio.sleep(4)
            value = completion.choices[0].message.content
            self.logger.info(f"{green('🔚 Orchestrator is ending process...')}")
            self.logger.info(f"{blue('🔄 Total iterations:')} {self.iterations_counter}")
            self.logger.info(f"{blue('🏁 Final result:')} {value}")

    def send(self, message: Message):
        self.message_broker.publish(message)

    @staticmethod
    def handle_spin_completion(chat_completion: ChatCompletion) -> str:
        message, should_call_tools = extract_chat_completion(chat_completion)

        if not should_call_tools:
            return "Do not need more iterations. Task is done."

        return f"Orchestrator decided to call tools: {[message['function_name'] for message in message]}"
