import asyncio

from autobox.common.logger import Logger
from autobox.core.llm import LLM
from autobox.core.messaging import MessageBroker
from autobox.core.network import Network
from autobox.core.orchestrator import Orchestrator
from autobox.core.prompts.orchestrator import prompt as orchestrator_prompt
from autobox.core.prompts.tools.worker import get_tools
from autobox.core.prompts.worker import prompt as agent_prompt
from autobox.core.simulation import Simulation
from autobox.core.worker import Worker
from autobox.schemas.simulation import SimulationRequest


def prepare_simulation(config: SimulationRequest):
    simulation_config = config.simulation
    orchestrator_config = config.orchestrator
    logging_config = config.simulation.logging

    message_broker = MessageBroker()

    workers = []
    worker_ids = {}
    worker_names = {}
    workers_memory_for_orchestrator = {}
    for agent in config.agents:
        worker = Worker(
            name=agent.name,
            mailbox=asyncio.Queue(maxsize=agent.mailbox.max_size),
            message_broker=message_broker,
            llm=LLM(agent_prompt(simulation_config.task, agent.backstory)),
            task=simulation_config.task,
            logger=Logger(
                agent_name=agent.name,
                verbose=agent.verbose,
                log_path=logging_config.file_path,
            ),
            memory={"worker": []},
        )
        worker_ids[worker.name] = worker.id
        workers.append(worker)
        worker_names[worker.name] = agent.role
        message_broker.subscribe(worker.id, worker.mailbox)
        workers_memory_for_orchestrator[worker.name] = []

    tools = get_tools(worker_names)

    orchestrator = Orchestrator(
        name=orchestrator_config.name,
        mailbox=asyncio.Queue(maxsize=orchestrator_config.mailbox.max_size),
        message_broker=message_broker,
        llm=LLM(
            orchestrator_prompt(
                simulation_config.task,
                simulation_config.max_steps,
                orchestrator_config.instruction,
            ),
            tools=tools,
            parallel_tool_calls=True,
        ),
        worker_ids=worker_ids,
        task=simulation_config.task,
        logger=Logger(
            agent_name=orchestrator_config.name,
            verbose=orchestrator_config.verbose,
            log_path=logging_config.file_path,
        ),
        memory={"orchestrator": [], **workers_memory_for_orchestrator},
        max_steps=simulation_config.max_steps,
    )

    message_broker.subscribe(orchestrator.id, orchestrator.mailbox)

    network = Network(
        workers=workers,
        orchestrator=orchestrator,
        message_broker=message_broker,
    )

    return Simulation(network=network, timeout=config.simulation.timeout)
