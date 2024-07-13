import asyncio
import time

from autobox.core.agent import Agent
from autobox.core.llm import LLM
from autobox.core.messaging import MessageBroker
from autobox.core.network import Network
from autobox.core.orchestrator import Orchestrator
from autobox.core.prompts.agent import prompt as agent_prompt
from autobox.core.prompts.orchestrator import prompt as orchestrator_prompt
from autobox.core.prompts.tools.agents import get_tools
from autobox.schemas.config import SimulationConfig
from autobox.utils import blue, green, yellow


class Simulator:
    network: Network

    def __init__(self, network: Network):
        self.network = network

    async def run(self, timeout: int = 120):
        print(f"{green('✅ Autobox is running')}")
        start_time = time.time()

        # Start network
        task = asyncio.create_task(self.network.run())

        try:
            await asyncio.wait_for(task, timeout=timeout)
        except asyncio.TimeoutError:
            print(f"{yellow('Simulation ended due to timeout.')}")
        finally:
            self.network.stop()            
            print(f"{blue('🔚 Simulation finished.')}")

        elapsed_time = int(time.time() - start_time)
        print(f"{blue(f"⏱️ Elapsed time: {elapsed_time} seconds.")}")


def prepare_simulation(config: SimulationConfig):
    task = config.task

    message_broker = MessageBroker()

    agents = []
    agent_ids = {}
    agent_names = []
    for agent in config.agents:
        agent = Agent(
            name=agent.name,
            mailbox=asyncio.Queue(maxsize=agent.mailbox["max_size"]),
            message_broker=message_broker,
            llm=LLM(agent_prompt(task, agent.backstory)),
            task=task,
        )
        agent_ids[agent.name] = agent.id
        agents.append(agent)
        agent_names.append(agent.name)
        message_broker.subscribe(agent)

    tools = get_tools(agent_names)

    orchestrator = Orchestrator(
        name=config.orchestrator["name"],
        mailbox=asyncio.Queue(maxsize=config.orchestrator["mailbox"]["max_size"]),
        message_broker=message_broker,
        llm=LLM(orchestrator_prompt(task), tools=tools, parallel_tool_calls=True),
        agent_ids=agent_ids,
        task=task,
    )

    message_broker.subscribe(orchestrator)

    network = Network(
        agents=agents,
        orchestrator=orchestrator,
        message_broker=message_broker,
    )

    return Simulator(network)

