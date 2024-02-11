import asyncio

from dotenv import load_dotenv

from autobox.autobox import Simulator
from autobox.config.loader import load_config
from autobox.network.agent import Agent, MessageBroker, Supervisor
from autobox.network.network import Network

load_dotenv()

config = load_config()

message_broker = MessageBroker()
supervisor = Supervisor(name="Supervisor", message_broker=message_broker)

sweden_agent = Agent(
    name="Sweden Representative",
    mailbox=asyncio.Queue(maxsize=10),
    message_broker=message_broker,
)
argentina_agent = Agent(
    name="Argentina Representative",
    mailbox=asyncio.Queue(maxsize=10),
    message_broker=message_broker,
)

message_broker.subscribe(sweden_agent)
message_broker.subscribe(argentina_agent)
supervisor.register_agent(argentina_agent, is_initial=True)
supervisor.register_agent(sweden_agent)

network = Network(
    agents=[sweden_agent, argentina_agent],
    supervisor=supervisor,
    message_broker=message_broker,
)

simulator = Simulator(network)
asyncio.run(
    simulator.run(
        "We need to come up with a bi-collateral agreement to fight Climate Change"
    )
)
