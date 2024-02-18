import asyncio

from dotenv import load_dotenv

from autobox.agents.supervisor import Supervisor
from autobox.agents.worker import Worker
from autobox.autobox import Simulator
from autobox.config.loader import load_config
from autobox.network import message_broker

# from autobox.network.agent import Agent, MessageBroker, Supervisor
from autobox.network.network import Network

load_dotenv()

config = load_config()

message_broker = message_broker.MessageBroker()
supervisor = Supervisor(name="Supervisor", message_broker=message_broker)

sweden_agent = Worker(
    name="SwedenRepresentative",
    # mailbox=asyncio.Queue(maxsize=10),
    mailbox=asyncio.Queue(),
    message_broker=message_broker,
    description="Sweden Representative",
    # supervisor=supervisor,
)
argentina_agent = Worker(
    name="ArgentinaRepresentative",
    # mailbox=asyncio.Queue(maxsize=10),
    mailbox=asyncio.Queue(),
    message_broker=message_broker,
    description="Argentina Representative",
    # supervisor=supervisor,
)

supervisor.register_agent(argentina_agent)
supervisor.register_agent(sweden_agent)

network = Network(
    agents=[sweden_agent, argentina_agent],
    supervisor=supervisor,
    message_broker=message_broker,
)

simulator = Simulator(network)

asyncio.run(
    simulator.run(
        task="We need to come up with a bi-collateral agreement to fight Climate Change"
    )
)
