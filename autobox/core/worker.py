import json

from autobox.core.agent import Agent
from autobox.schemas.message import Message
from autobox.utils.console import blue, spin


class Worker(Agent):

    async def handle_message(self, message: Message):
        to_agent_id = message.from_agent_id
        if message.value == "end":
            print(f"{blue(f"Agent {self.name} ({self.id}) is stopping...")}")
            self.is_end = True
            return

        print(f"{blue(f"📨 Agent {self.name} ({self.id}) handling message from orchestrator...")}")

        json_message_value = json.loads(message.value)
        agent_decisions = json_message_value["agent_decisions"]
        arguments = json.loads(json_message_value["arguments"])
        task_status = arguments["task_status"]
        instruction = arguments["instruction"]
        thinking_process = arguments["thinking_process"]

        print(f"{blue(f'📜 Instruction for Agent {self.name} ({self.id}):')} {instruction}")
        print(f"{blue(f'📊 Task status {self.name} ({self.id}):')} {task_status}")
        print(f"{blue(f'💭 Thinking process {self.name} ({self.id}):')} {thinking_process}")

        self.memory.append(agent_decisions)

        chat_completion_messages = [
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
