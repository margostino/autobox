import asyncio

from dotenv import load_dotenv

from autobox.agents.agent import Agent
from autobox.agents.planner import Planner
from autobox.agents.supervisor import Supervisor
from autobox.autobox import Simulator
from autobox.config.loader import load_config
from autobox.network import messaging
from autobox.network.base import Network

load_dotenv()

config = load_config()

messaging = messaging.MessageBroker()
supervisor = Supervisor(name="Supervisor", message_broker=messaging)

sweden_agent = Agent(
    name="SwedenRepresentative",
    mailbox=asyncio.Queue(),
    message_broker=messaging,
    description="This is a Sweden Representative Agent. Its responsibility is to represent Sweden in the negotiation",
)
argentina_agent = Agent(
    name="ArgentinaRepresentative",
    mailbox=asyncio.Queue(),
    message_broker=messaging,
    description="Argentina Representative Agent. Its responsibility is to represent Argentina in the negotiation",
)

planner = Planner()

network = Network(
    agents=[sweden_agent, argentina_agent],
    supervisor=supervisor,
    message_broker=messaging,
    planner=planner,
)

simulator = Simulator(network)

asyncio.run(
    simulator.run(
        task="We need to come up with a bi-collateral agreement to fight Climate Change"
    )
)
