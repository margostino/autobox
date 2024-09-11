import asyncio
import json
import os

from openai import OpenAI

from autobox.bootstrap.metrics.builder import define_metrics
from autobox.bootstrap.metrics.loader import load_metrics
from autobox.cache.cache import Cache
from autobox.common.logger import Logger
from autobox.core.agents.evaluator import Evaluator
from autobox.core.agents.orchestrator import Orchestrator
from autobox.core.agents.utils.llm import LLM
from autobox.core.agents.utils.messaging import MessageBroker
from autobox.core.agents.worker import Worker
from autobox.core.network import Network
from autobox.core.prompts.metrics_calculator import prompt as metrics_calculator_prompt
from autobox.core.prompts.orchestrator import prompt as orchestrator_prompt
from autobox.core.prompts.tools.worker import get_tools
from autobox.core.prompts.worker import prompt as agent_prompt
from autobox.core.simulation import Simulation
from autobox.schemas.simulation import SimulationRequest
from autobox.utils.normalization import value_to_id


async def prepare_simulation(request: SimulationRequest) -> Simulation:
    logger = Logger.get_instance()

    openai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"), max_retries=4)

    simulation_config = request.simulation
    orchestrator_config = request.orchestrator
    simulation_name_id = value_to_id(simulation_config.name)

    logger.info("Bootstrapping simulation...")

    message_broker = MessageBroker()

    workers = []
    worker_ids = {}
    worker_names = {}
    workers_memory_for_orchestrator = {}
    for agent in request.agents:
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

    metrics = load_metrics(
        name=simulation_name_id,
        path=simulation_config.metrics_path,
    )
    if metrics is None:
        metrics = define_metrics(
            name=simulation_name_id,
            path=simulation_config.metrics_path,
            workers=workers,
            orchestrator_name=orchestrator_config.name,
            orchestrator_instruction=orchestrator_config.instruction,
            task=simulation_config.task,
            openai=openai,
        )

    metrics_definitions = json.dumps(
        {key: metric.model_dump(exclude="value") for key, metric in metrics.items()}
    )

    evaluator = Evaluator(
        name="metric_evaluator",
        mailbox=asyncio.Queue(maxsize=orchestrator_config.mailbox.max_size),
        task=simulation_config.task,
        message_broker=message_broker,
        logger=logger,
        llm=LLM(
            metrics_calculator_prompt(
                task=simulation_config.task,
                agents={worker.name: worker.backstory for worker in workers},
                metrics=json.dumps(
                    {
                        metric.name: metric.model_dump_json()
                        for metric in metrics.values()
                    }
                ),
            )
        ),
    )
    # evaluator.set_cache(metrics)

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
        worker_names={value: key for key, value in worker_ids.items()},
        task=simulation_config.task,
        memory={"orchestrator": [], **workers_memory_for_orchestrator},
        max_steps=simulation_config.max_steps,
        instruction=orchestrator_config.instruction,
        evaluator_id=evaluator.id,
    )

    message_broker.subscribe(orchestrator.id, orchestrator.mailbox)
    message_broker.subscribe(evaluator.id, evaluator.mailbox)

    network = Network(
        workers=workers,
        orchestrator=orchestrator,
        evaluator=evaluator,
        message_broker=message_broker,
    )

    simulation = Simulation(network=network, timeout=request.simulation.timeout)
    await Cache.simulation().init_simulation("created", request, simulation, metrics)
    return simulation
