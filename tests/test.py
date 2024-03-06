import os

from dotenv import load_dotenv

from src.agents.supervisor import Supervisor
from src.config.loader import load_config
from src.network.messaging import MessageBroker
from src.tools.base import BaseTool

load_dotenv()

config = load_config(os.getenv("AUTOBOX_CONFIG_PATH"))

messaging = MessageBroker()
supervisor = Supervisor(name="Supervisor", message_broker=messaging)

tools = []
for tool_config in config["tools"]:
    tool = BaseTool(**tool_config)
    tool.message_broker = messaging
    tool.supervisor = supervisor
    messaging.register_tool(tool)
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
