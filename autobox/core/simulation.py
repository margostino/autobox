import asyncio

from autobox.core.llm import LLM
from autobox.core.messaging import MessageBroker
from autobox.core.network import Network
from autobox.core.orchestrator import Orchestrator
from autobox.core.prompts.agent import prompt as agent_prompt
from autobox.core.prompts.orchestrator import prompt as orchestrator_prompt
from autobox.core.prompts.tools.agents import get_tools
from autobox.core.simulator import Simulator
from autobox.core.worker import Worker
from autobox.schemas.simulation import SimulationRequest


def prepare_simulation(config: SimulationRequest):
    task = config.simulation.task

    message_broker = MessageBroker()

    workers = []
    worker_ids = {}
    worker_names = []
    for agent in config.agents:
        worker = Worker(
            name=agent.name,
            mailbox=asyncio.Queue(maxsize=agent.mailbox.max_size),
            message_broker=message_broker,
            llm=LLM(agent_prompt(task, agent.backstory)),
            task=task,
        )
        worker_ids[worker.name] = worker.id
        workers.append(worker)
        worker_names.append(worker.name)
        message_broker.subscribe(worker.id, worker.mailbox)

    tools = get_tools(worker_names)

    orchestrator = Orchestrator(
        name=config.orchestrator.name,
        mailbox=asyncio.Queue(maxsize=config.orchestrator.mailbox.max_size),
        message_broker=message_broker,
        llm=LLM(orchestrator_prompt(task), tools=tools, parallel_tool_calls=True),
        worker_ids=worker_ids,
        task=task,
    )

    message_broker.subscribe(orchestrator.id, orchestrator.mailbox)

    network = Network(
        workers=workers,
        orchestrator=orchestrator,
        message_broker=message_broker,
    )

    return Simulator(network=network)
