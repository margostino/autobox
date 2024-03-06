import asyncio
import random
from asyncio import Queue
from typing import Dict

from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field

from src.agents.agent import Agent
from src.agents.base import BaseAgent
from src.network.messaging import Message, MessageBroker

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


class LLMInput(BaseModel):
    input: int = Field(
        description="should be a number",
    )


def get_country_prompt_for(country_name: str) -> PromptTemplate:
    return PromptTemplate.from_template(
        f"""
        You are representative of {country_name}. 
        Your job is to establish communication with other countries and agree on an action plan to fight Climate Change.    
        Keep your answers short and to the point: Max 50 words.
        
        You finish when you and other countries have an bilateral agreement to fight Climate Change. The agreement should include:
            - Objetives: what you want to achieve
            - Action plan: how you will achieve your objetives
            - Resources: what you need to achieve your objetives
            - Timeline: when you will achieve your objetives
            
        In order to achieve your goals:
         - you have to be collaborative with other countries and help them out with resources and services.        
         - you have to ask other countries for help.
        
        Input: {{input}}
        """
    )


class Supervisor(BaseAgent):
    agents: Dict[int, Agent]

    def __init__(self, name: str, message_broker: MessageBroker):
        super().__init__(
            name=name,
            mailbox=Queue(),
            message_broker=message_broker,
            description="Supervisor",
        )
        self.agents = {}

    async def solve(self, task: str):
        self.memory["task"] = task
        # start listening
        async_tasks = [agent.listen() for agent in self.agents.values()]
        async_tasks.append(self.listen())

        # simulate agent routing
        agent_id = random.choice(list(self.agents.keys()))
        agent = self.agents[agent_id]
        message = Message(
            value=task,
            from_agent_id=self.id,
        )
        agent.mailbox.put_nowait(message)
        self.memory["initial_agent"] = agent

        async_results = await asyncio.gather(*async_tasks)
        return async_results

    # async def route(self, task: str):
    #     while self.running:
    #         agent_id = random.choice(list(self.agents.keys()))
    #         agent = self.agents[agent_id]
    #         agent.mailbox.put_nowait(task)
    #         await asyncio.sleep(2)
    #         # get random number from zero to keys of agents
    #         # agent = self.agents[random.randint(0, len(self.agents) - 1)]

    async def _handle(self, message: Message):
        if self.should_stop(message.value):
            self.running = False
        random_message = random.choice(messages)
        reply = Message(random_message, self.id)
        self.message_broker.mailbox.put_nowait(reply)
        print(
            f"Supervisor ({self.name}/{self.id}) handling message from {message.from_agent_id}: {message.value}"
        )

    def should_stop(self, message: str):
        return message == "I am a doctor"

    # async def start(self, input_message: str):
    #     # pick a random agent id distinct from the entry agent id
    #     from_agent_id = self.entry_agent_id
    #     while from_agent_id == self.entry_agent_id:
    #         from_agent_id = random.choice(list(self.agents.keys()))

    #     message = Message(
    #         to_agent_id=self.entry_agent_id,
    #         value=input_message,
    #         from_agent_id=from_agent_id,
    #     )
    #     self.message_broker.publish(message)

    def register_agent(self, agent: Agent):
        self.agents[agent.id] = agent

    # def send(self, message: Message):
    #     self.message_broker.publish(message)


# class Router:
#     agents: Dict[int, Agent]

#     def __init__(self, agents: Dict[int, Agent]):
#         self.agents = agents

#     def route(self, message: Message):
#         if message.to_agent_id in self.agents:
#             self.agents[message.to_agent_id].mailbox.put_nowait(message)
#         else:
#             raise ValueError(f"Agent with id {message.to_agent_id} not found")
