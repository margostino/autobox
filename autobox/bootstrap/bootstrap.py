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
from autobox.core.prompts.metrics_calculator import METRICS_CALCULATOR_PROMPT
from autobox.core.prompts.metrics_calculator import prompt as metrics_calculator_prompt
from autobox.core.prompts.orchestrator import prompt as orchestrator_prompt
from autobox.core.prompts.summary import SUMMARY_PROMPT
from autobox.core.prompts.summary import prompt as summary_prompt
from autobox.core.prompts.tools.worker import get_tools
from autobox.core.prompts.worker import prompt as agent_prompt
from autobox.core.simulation import Simulation
from autobox.metrics.grafana import create_grafana_dashboard
from autobox.metrics.prometheus import create_prometheus_metrics
from autobox.schemas.constants import DEFAULT_PROMPT
from autobox.schemas.simulation import SimulationRequest
from autobox.utils.normalization import value_to_id


async def prepare_simulation(
    request: SimulationRequest, is_local_mode=False
) -> Simulation:
    log_name = value_to_id(request.simulation.name)
    logger = Logger(
        name=log_name,
        log_path=request.logging.log_path,
        log_file=request.logging.log_file,
        verbose=request.logging.verbose,
    )

    openai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"), max_retries=4)

    simulation_config = request.simulation
    orchestrator_config = request.orchestrator
    simulation_name_id = value_to_id(simulation_config.name)

    logger.info("Bootstrapping simulation...")

    message_broker = MessageBroker(logger=logger)

    workers = []
    worker_ids = {}
    worker_names = {}
    workers_memory_for_orchestrator = {}
    for agent in request.agents:
        worker = Worker(
            name=agent.name,
            mailbox=asyncio.Queue(maxsize=agent.mailbox.max_size),
            message_broker=message_broker,
            llm=LLM(
                system_prompts={
                    DEFAULT_PROMPT: agent_prompt(
                        simulation_config.task, agent.backstory
                    )
                }
            ),
            task=simulation_config.task,
            logger=logger,
            memory={"worker": []},
            backstory=agent.backstory,
            is_local_mode=is_local_mode,
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
            logger=logger,
        )

    metrics_definitions = json.dumps(
        {
            key: (
                metric.model_dump(exclude={"value", "collector_registry"})
                if hasattr(metric, "model_dump")
                else {
                    k: v
                    for k, v in metric.items()
                    if k not in {"value", "collector_registry"}
                }
            )
            for key, metric in metrics.items()
        }
    )

    evaluator = Evaluator(
        name="metric_evaluator",
        mailbox=asyncio.Queue(maxsize=orchestrator_config.mailbox.max_size),
        task=simulation_config.task,
        message_broker=message_broker,
        logger=logger,
        is_local_mode=is_local_mode,
        simulation_name=simulation_name_id,
        llm=LLM(
            system_prompts={
                METRICS_CALCULATOR_PROMPT: metrics_calculator_prompt(
                    task=simulation_config.task,
                    agents={worker.name: worker.backstory for worker in workers},
                ),
                SUMMARY_PROMPT: summary_prompt(
                    task=simulation_config.task,
                    agents={worker.name: worker.backstory for worker in workers},
                ),
            },
        ),
    )

    orchestrator = Orchestrator(
        name=orchestrator_config.name,
        mailbox=asyncio.Queue(maxsize=orchestrator_config.mailbox.max_size),
        message_broker=message_broker,
        llm=LLM(
            system_prompts={
                DEFAULT_PROMPT: orchestrator_prompt(
                    simulation_config.task,
                    simulation_config.max_steps,
                    orchestrator_config.instruction,
                    metrics=metrics_definitions,
                )
            },
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
        logger=logger,
        is_local_mode=is_local_mode,
    )

    message_broker.subscribe(orchestrator.id, orchestrator.mailbox)
    message_broker.subscribe(evaluator.id, evaluator.mailbox)

    network = Network(
        workers=workers,
        orchestrator=orchestrator,
        evaluator=evaluator,
        message_broker=message_broker,
        logger=logger,
    )

    simulation = Simulation(
        network=network,
        timeout=request.simulation.timeout,
        logger=logger,
    )
    await Cache.simulation().init_simulation("created", request, simulation, metrics)

    evaluator.simulation_id = simulation.id
    create_prometheus_metrics(metrics)
    logger.info("Metrics loaded into Prometheus")
    grafana_response = await create_grafana_dashboard(
        simulation_name_id, simulation.id, metrics
    )
    logger.info(f"Grafana dashboard created: {grafana_response['status']}")
    # TODO: do it properly and support remote servers
    dashboard_url = f"http://localhost:3000{grafana_response['url']}?orgId=1&refresh=5s"
    logger.info(f"Dashboard URL: {dashboard_url}")

    return simulation
