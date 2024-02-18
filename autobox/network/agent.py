# import asyncio
# import random
# from asyncio import Queue
# from typing import Dict

# from langchain.agents import AgentExecutor, create_openai_functions_agent
# from langchain.chains import LLMChain
# from langchain.prompts import PromptTemplate
# from langchain.tools import StructuredTool, tool
# from langchain_openai import ChatOpenAI
# from pydantic import BaseModel, Field

# from autobox.network.mail import Message

# messages = [
#     "Hello, I am here to help you",
#     "I am a bot, I can help you with your queries",
#     "I am a player footballer",
#     "I am a player cricketer",
#     "I like computer games",
#     "I wanna be a president",
#     "I am a doctor",
#     "One day I will go to Everest and climb it",
# ]


# class LLMInput(BaseModel):
#     input: int = Field(
#         description="should be a number",
#     )


# def get_country_prompt_for(country_name: str) -> PromptTemplate:
#     return PromptTemplate.from_template(
#         f"""
#         You are representative of {country_name}.
#         Your job is to establish communication with other countries and agree on an action plan to fight Climate Change.
#         Keep your answers short and to the point: Max 50 words.

#         You finish when you and other countries have an bilateral agreement to fight Climate Change. The agreement should include:
#             - Objetives: what you want to achieve
#             - Action plan: how you will achieve your objetives
#             - Resources: what you need to achieve your objetives
#             - Timeline: when you will achieve your objetives

#         In order to achieve your goals:
#          - you have to be collaborative with other countries and help them out with resources and services.
#          - you have to ask other countries for help.

#         Input: {{input}}
#         """
#     )


# class Agent:
#     id: int
#     name: str
#     mailbox: Queue
#     message_broker: "MessageBroker"
#     supervisor: "Supervisor"
#     agent_executor: AgentExecutor

#     def __init__(self, name: str, mailbox: Queue, message_broker: "MessageBroker"):
#         self.id = hash(name) % 1000
#         self.name = name
#         self.running = True
#         self.mailbox = mailbox
#         self.message_broker = message_broker
#         self.agent_executor = self.create_agent_executor()

#     def create_agent_executor(self):
#         llm = ChatOpenAI(model="gpt-4-1106-preview")
#         tool_prompt = PromptTemplate.from_template(
#             """
#                 You are a smart assistant.
#                 Your job is to increment a number to 1 and return it.
#                 Input: {input}
#             """
#         )
#         llm_chain = LLMChain(llm=llm, prompt=tool_prompt)
#         llm_tool = StructuredTool.from_function(
#             func=llm_chain.run,
#             name="IncrementalTool",
#             args_schema=LLMInput,
#             description="useful tool to increment a number to 1",
#         )
#         tools = [llm_tool, self.should_finish]
#         agent_prompt = PromptTemplate.from_template(
#             """
#                 You are a helpful AI assistant, collaborating with other assistants.
#                 Use the provided tools to progress towards answering the question.
#                 If you are unable to fully answer, that's OK, another assistant with different tools will help where you left off. Execute what you can to make progress.
#                 Your job is to increment the original number by 1.
#                 You should finish when there is a end condition. You should check end condition regulary using your tool to know that.
#                 If you or any of the other assistants have the end condition, prefix your response with FINAL ANSWER so the team knows to stop.
#                 You have access to the following tools: {tool_names}.
#                 Input: {input}
#                 MessagePlaceholder: {agent_scratchpad}
#             """
#         )
#         # functions = [format_tool_to_openai_function(t) for t in tools]
#         # system_message = "You should reach an agreement with other countries in order to establish a action plan to fight Climate Change"
#         # agent_prompt = agent_prompt.partial(system_message=system_message)
#         agent_prompt = agent_prompt.partial(
#             tool_names=", ".join([tool.name for tool in tools])
#         )
#         # agent = agent_prompt | llm.bind_functions(functions)
#         agent = create_openai_functions_agent(llm, tools, agent_prompt)
#         agent_executor = AgentExecutor(
#             agent=agent,
#             tools=tools,
#             verbose=True,
#             max_iterations=100,
#             max_execution_time=300,
#             return_intermediate_steps=True,
#         )
#         return agent_executor

#     @tool(name="check-end-condition", args_schema=Agent)
#     def should_finish(self, *args) -> bool:
#         """
#         This tool is useful to check the end condition.
#         It returns a boolean flag (True: it should finish)
#         """
#         if not self.mailbox.empty():
#             message: Message = self.mailbox.get_nowait()
#             return message.value == "DONE"

#     async def handle_message(self, message: Message):
#         print(f"Agent {self.id} received message: {message.value}")
#         random_message = random.choice(messages)
#         # response = self.agent_executor.invoke({"messages": [random_message]})
#         response = self.agent_executor.invoke({"input": 0})
#         reply_message = Message(
#             to_agent_id=message.from_agent_id,
#             value=random_message,
#             from_agent_id=self.id,
#         )
#         self.message_broker.publish(reply_message)

#     async def run(self):
#         while self.running:
#             if not self.mailbox.empty():
#                 message: Message = self.mailbox.get_nowait()
#                 await self.handle_message(message)
#             await asyncio.sleep(1)


# class Supervisor:
#     name: str
#     mailbox: Queue
#     entry_agent_id: int
#     agents: Dict[int, Agent]
#     message_broker: "MessageBroker"

#     def __init__(self, name: str, message_broker: "MessageBroker"):
#         self.name = name
#         self.entry_agent_id = None
#         self.agents = {}
#         self.mailbox = Queue(maxsize=10 * 2)
#         self.message_broker = message_broker

#     async def start(self, input_message: str):
#         # pick a random agent id distinct from the entry agent id
#         from_agent_id = self.entry_agent_id
#         while from_agent_id == self.entry_agent_id:
#             from_agent_id = random.choice(list(self.agents.keys()))

#         message = Message(
#             to_agent_id=self.entry_agent_id,
#             value=input_message,
#             from_agent_id=from_agent_id,
#         )
#         self.message_broker.publish(message)

#     def register_agent(self, agent: Agent, is_initial=False):
#         agent.supervisor = self
#         self.agents[agent.id] = agent
#         self.entry_agent_id = agent.id if is_initial else self.entry_agent_id

#     def send(self, message: Message):
#         self.message_broker.publish(message)


# class MessageBroker:

#     def __init__(self):
#         self.subscribers = {}

#     def subscribe(self, agent: Agent):
#         self.subscribers[agent.id] = agent

#     def publish(self, message: Message):
#         if message.to_agent_id in self.subscribers:
#             self.subscribers[message.to_agent_id].mailbox.put_nowait(message)
#         else:
#             raise ValueError(f"Agent with id {message.to_agent_id} not found")


# class Router:
#     agents: Dict[int, Agent]

#     def __init__(self, agents: Dict[int, Agent]):
#         self.agents = agents

#     def route(self, message: Message):
#         if message.to_agent_id in self.agents:
#             self.agents[message.to_agent_id].mailbox.put_nowait(message)
#         else:
#             raise ValueError(f"Agent with id {message.to_agent_id} not found")
