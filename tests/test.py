import asyncio

from dotenv import load_dotenv

from src.agents.agent import Agent
from src.agents.planner import Planner
from src.agents.supervisor import Supervisor
from src.autobox import Simulator
from src.config.loader import load_config
from src.network import messaging
from src.network.base import Network
from src.tools.base import BaseTool

load_dotenv()

config = load_config()

messaging = messaging.MessageBroker()
supervisor = Supervisor(name="Supervisor", message_broker=messaging)
tools = [
    BaseTool(
        "evaluate_and_reply_proposal",
        "useful when sending a proposal to another country",
        {
            "proposal": {
                "type": "string",
                "description": "The proposal to be evaluated",
            },
            "country": {
                "type": "string",
                "description": "The country to which the proposal is being sent",
            },
        },
    )
]
sweden_agent = Agent(
    name="SwedenRepresentative",
    mailbox=asyncio.Queue(),
    message_broker=messaging,
    description="This is a Sweden Representative Agent. Its responsibility is to represent Sweden in the negotiation",
    tools=tools,
)
argentina_agent = Agent(
    name="ArgentinaRepresentative",
    mailbox=asyncio.Queue(),
    message_broker=messaging,
    description="Argentina Representative Agent. Its responsibility is to represent Argentina in the negotiation",
    tools=tools,
)

agents = [sweden_agent, argentina_agent]
agent_profiles = [agent.get_agent_profile() for agent in agents]
tool_profiles = [tool.get_tool_profile() for tool in tools]
planner = Planner({"agents": agent_profiles, "tools": tool_profiles})

network = Network(
    agents=agents,
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
