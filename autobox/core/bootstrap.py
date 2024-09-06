import asyncio
import json

from autobox.cache.metrics import MetricsCache
from autobox.common.logger import Logger
from autobox.core.llm import LLM
from autobox.core.messaging import MessageBroker
from autobox.core.metric_collector import MetricCollector
from autobox.core.network import Network
from autobox.core.orchestrator import Orchestrator
from autobox.core.prompts.orchestrator import prompt as orchestrator_prompt
from autobox.core.prompts.tools.worker import get_tools
from autobox.core.prompts.worker import prompt as agent_prompt
from autobox.core.simulation import Simulation
from autobox.core.worker import Worker
from autobox.schemas.simulation import SimulationRequest
from autobox.utils.normalization import value_to_id


def prepare_simulation(config: SimulationRequest):
    simulation_config = config.simulation
    orchestrator_config = config.orchestrator
    logging_config = config.simulation.logging

    logger = Logger(
        name=simulation_config.name,
        verbose=simulation_config.verbose,
        log_path=logging_config.file_path,
    )

    simulation_name_id = value_to_id(simulation_config.name)

    logger.info("Bootstrapping simulation...")

    metric_collector = MetricCollector(logger=logger)

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
            logger=logger,
            memory={"worker": []},
            backstory=agent.backstory,
        )
        worker_ids[worker.name] = worker.id
        workers.append(worker)
        worker_names[worker.name] = agent.role
        message_broker.subscribe(worker.id, worker.mailbox)
        workers_memory_for_orchestrator[worker.name] = []

    tools = get_tools(worker_names)

    metrics = metric_collector.load_metrics_for_simulation(
        name=simulation_name_id,
        path=simulation_config.metrics_path,
        workers=workers,
        orchestrator_name=orchestrator_config.name,
        orchestrator_instruction=orchestrator_config.instruction,
        task=simulation_config.task,
    )
    metrics_cache = MetricsCache(metrics=metrics)

    metrics_definitions = json.dumps(
        {key: metric.model_dump(exclude="value") for key, metric in metrics.items()}
    )

    orchestrator = Orchestrator(
        name=orchestrator_config.name,
        mailbox=asyncio.Queue(maxsize=orchestrator_config.mailbox.max_size),
        message_broker=message_broker,
        llm=LLM(
            orchestrator_prompt(
                simulation_config.task,
                simulation_config.max_steps,
                orchestrator_config.instruction,
                metrics=metrics_definitions,
            ),
            tools=tools,
            parallel_tool_calls=True,
        ),
        worker_ids=worker_ids,
        task=simulation_config.task,
        logger=logger,
        memory={"orchestrator": [], **workers_memory_for_orchestrator},
        max_steps=simulation_config.max_steps,
        metrics_cache=metrics_cache,
        instruction=orchestrator_config.instruction,
    )

    message_broker.subscribe(orchestrator.id, orchestrator.mailbox)

    network = Network(
        workers=workers,
        orchestrator=orchestrator,
        message_broker=message_broker,
        logger=logger,
    )

    return Simulation(
        network=network,
        timeout=config.simulation.timeout,
        logger=logger,
    )
