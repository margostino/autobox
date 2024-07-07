import argparse
import asyncio

from autobox.config import load_config
from autobox.core.agent import Agent
from autobox.core.llm import LLM
from autobox.core.messaging import MessageBroker
from autobox.core.network import Network
from autobox.core.orchestrator import Orchestrator
from autobox.core.prompts.agent import prompt as agent_prompt
from autobox.core.prompts.orchestrator import prompt as orchestrator_prompt
from autobox.core.prompts.tools.agents import get_tools
from autobox.core.simulator import Simulator


def main():
    parser = argparse.ArgumentParser(description="Autobox")
    parser.add_argument(
        "--config-file",
        type=str,
        required=True,
        default="config.toml",
        help="Path to the configuration file",
    )

    args = parser.parse_args()

    print(f"Using configuration file: {args.config_file}")

    config = load_config(args.config_file)

    task = config.task

    # file_path = f"{os.environ.get("TOOLS_PATH")}/agents.json"
    # with open(file_path, "r", encoding="utf-8") as file:
    #     tools = json.load(file)

    message_broker = MessageBroker()

    agents = []
    agent_ids = {}
    agent_names = []
    for agent in config.agents:
        agent = Agent(
            name=agent.name,
            mailbox=asyncio.Queue(maxsize=10),
            message_broker=message_broker,
            llm=LLM(agent_prompt(agent.backstory)),
            task=task,
        )
        agent_ids[agent.name] = agent.id
        agents.append(agent)
        agent_names.append(agent.name)
        message_broker.subscribe(agent)

    tools = get_tools(agent_names)

    orchestrator = Orchestrator(
        name="ORCHESTRATOR",
        mailbox=asyncio.Queue(maxsize=10),
        message_broker=message_broker,
        llm=LLM(orchestrator_prompt(), tools=tools, parallel_tool_calls=True),
        agent_ids=agent_ids,
        task=task,
    )

    message_broker.subscribe(orchestrator)

    network = Network(
        agents=agents,
        orchestrator=orchestrator,
        message_broker=message_broker,
    )

    simulator = Simulator(network)
    asyncio.run(simulator.run(timeout=300))


main()
