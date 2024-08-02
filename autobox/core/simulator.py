import asyncio
import time

from pydantic import BaseModel

from autobox.core.llm import LLM
from autobox.core.mail import Message
from autobox.core.messaging import MessageBroker
from autobox.core.network import Network
from autobox.core.orchestrator import Orchestrator
from autobox.core.prompts.agent import prompt as agent_prompt
from autobox.core.prompts.orchestrator import prompt as orchestrator_prompt
from autobox.core.prompts.tools.agents import get_tools
from autobox.core.worker import Worker
from autobox.schemas.simulation_request import SimulationRequest
from autobox.utils import blue, green, yellow


class Simulator(BaseModel):
    network: Network

    async def run(self, timeout: int = 120):
        print(f"{green('✅ Autobox is running')}")
        start_time = time.time()

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

    def abort(self):
        self.network.stop()
        print(f"{blue('🔚 Simulation aborted.')}")


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
    message_broker.publish(Message(value=None, to_agent_id=orchestrator.id))

    network = Network(
        workers=workers,
        orchestrator=orchestrator,
        message_broker=message_broker,
    )

    return Simulator(network=network)
