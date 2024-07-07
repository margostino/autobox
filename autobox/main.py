import asyncio
import json

from autobox.core.agent import Agent

# from autobox.config.loader import load_config
from autobox.core.llm import LLM
from autobox.core.messaging import MessageBroker
from autobox.core.network import Network
from autobox.core.orchestrator import Orchestrator
from autobox.core.prompts.agent import prompt as agent_prompt
from autobox.core.prompts.orchestrator import prompt as orchestrator_prompt
from autobox.core.simulator import Simulator


def main():
    # config = load_config()

    task = "We need to come up with a bi-collateral agreement to fight Climate Change"

    file_path = "/Users/martin.dagostino/workspace/margostino/autobox/autobox/core/prompts/tools/agents.json"

    with open(file_path, "r") as file:
        tools = json.load(file)

    message_broker = MessageBroker()

    sweden_agent = Agent(
        name="SWEDEN",
        mailbox=asyncio.Queue(maxsize=10),
        message_broker=message_broker,
        llm=LLM(agent_prompt()),
        task=task,
    )
    argentina_agent = Agent(
        name="ARGENTINA",
        mailbox=asyncio.Queue(maxsize=10),
        message_broker=message_broker,
        llm=LLM(agent_prompt()),
        task=task,
    )
    orchestrator = Orchestrator(
        name="ORCHESTRATOR",
        mailbox=asyncio.Queue(maxsize=10),
        message_broker=message_broker,
        llm=LLM(orchestrator_prompt(), tools=tools, parallel_tool_calls=True),
        agent_ids={
            sweden_agent.name: sweden_agent.id,
            argentina_agent.name: argentina_agent.id,
        },
        task=task,
    )

    message_broker.subscribe(sweden_agent)
    message_broker.subscribe(argentina_agent)
    message_broker.subscribe(orchestrator)

    network = Network(
        agents=[sweden_agent, argentina_agent],
        orchestrator=orchestrator,
        message_broker=message_broker,
    )

    simulator = Simulator(network)
    asyncio.run(simulator.run(timeout=300))


main()
