import asyncio

from dotenv import load_dotenv

from autobox.agents.supervisor import Supervisor
from autobox.agents.worker import Worker
from autobox.autobox import Simulator
from autobox.config.loader import load_config
from autobox.network import messaging
from autobox.network.base import Network

load_dotenv()

config = load_config()

messaging = messaging.MessageBroker()
supervisor = Supervisor(name="Supervisor", message_broker=messaging)

sweden_agent = Worker(
    name="SwedenRepresentative",
    mailbox=asyncio.Queue(),
    message_broker=messaging,
    description="This is a Sweden Representative Agent. Its responsibility is to represent Sweden in the negotiation",
)
argentina_agent = Worker(
    name="ArgentinaRepresentative",
    mailbox=asyncio.Queue(),
    message_broker=messaging,
    description="Argentina Representative Agent. Its responsibility is to represent Argentina in the negotiation",
)

supervisor.register_agent(argentina_agent)
supervisor.register_agent(sweden_agent)

network = Network(
    agents=[sweden_agent, argentina_agent],
    supervisor=supervisor,
    message_broker=messaging,
)

simulator = Simulator(network)

asyncio.run(
    simulator.run(
        task="We need to come up with a bi-collateral agreement to fight Climate Change"
    )
)
