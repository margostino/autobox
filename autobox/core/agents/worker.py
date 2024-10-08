import json

from pydantic import Field

from autobox.core.agents.base import BaseAgent
from autobox.schemas.message import Message
from autobox.utils.console import blue, spin


class Worker(BaseAgent):
    human_instruction: str = Field(default=None)
    backstory: str

    async def handle_message(self, message: Message):
        if message.from_agent_id is None:
            self.logger.info(f"{blue(f'👩‍💻 Human instructed agent {self.name} ({self.id}) with instruction: {message.value}')}")
            self.human_instruction = message.value
            return

        to_agent_id = message.from_agent_id
        if message.value == "end":
            self.logger.info(f"{blue(f"Agent {self.name} ({self.id}) is stopping...")}")
            self.is_end = True
            return

        self.logger.info(f"{blue(f"📨 Agent {self.name} ({self.id}) handling message from orchestrator...")}")

        json_message_value = json.loads(message.value)
        # agent_decisions = json_message_value["agent_decisions"]
        arguments = json.loads(json_message_value["arguments"])
        task_status = arguments["task_status"]
        instruction = self.human_instruction if self.human_instruction else arguments["instruction"]
        thinking_process = arguments["thinking_process"]

        self.logger.info(f"{blue(f'📜 Instruction for Agent {self.name} ({self.id}):')} {instruction}")
        self.logger.info(f"{blue(f'📊 Task status {self.name} ({self.id}):')} {task_status}")
        self.logger.info(f"{blue(f'💭 Thinking process {self.name} ({self.id}):')} {thinking_process}")

        # self.memory['worker'].append(agent_decisions)

        chat_completion_messages = [
            {
                "role": "user",
                "content": f"Your previous messages for previous instructions: {json.dumps(self.memory['worker'])}",
            },
            {
                "role": "user",
                "content": f"Current task status: {task_status}",
            },
            {
                "role": "user",
                "content": f"Instruction: {instruction}",
            },
        ]

        completion = (spin(f"🧠 Agent {self.name} ({self.id}) is thinking...", lambda: self.llm.think(self.name, chat_completion_messages))
                    if self.is_local_mode
                    else self.llm.think(self.name, chat_completion_messages)[0])  # TODO: do it safe

        value = completion.choices[0].message.content
        self.memory['worker'].append(value)
        reply_message = Message(
            to_agent_id=to_agent_id,
            value=value,
            from_agent_id=self.id,
        )
        self.message_broker.publish(reply_message)
