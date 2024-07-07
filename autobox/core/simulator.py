import asyncio
import time

from autobox.core.network import Network
from autobox.utils import blue, green, yellow


class Simulator:
    network: Network

    def __init__(self, network: Network):
        self.network = network

    # def __init__(self, config: SimulationConfig):
    #     self.workflow = Workflow()
    #     agents = create_agents_from(config)
    #     nodes = create_nodes_from(agents)
    #     edges = create_conditional_edges_from(agents)

    #     for node in nodes:
    #         self.workflow.add_node(node.name, node)

    #     self.workflow.set_entry_point(config.entry_point)

    #     for edge in edges:
    #         self.workflow.add_conditional_edges(edge)

    #     self.graph = self.workflow.compile()

    async def run(self, timeout: int = 120):
        print(f"{green('Autobox is running...')}")
        start_time = time.time()

        # Start network
        task = asyncio.create_task(self.network.run())

        # Implement a timeout for the simulation
        try:
            await asyncio.wait_for(task, timeout=timeout)
        except asyncio.TimeoutError:
            print(f"{yellow('Simulation ended due to timeout.')}")
        finally:
            self.network.stop()
            print(f"{blue('Simulation finished.')}")

        # calculate elapsed time in seconds with no decimal points
        elapsed_time = int(time.time() - start_time)
        print(f"{blue(f"Elapsed time: {elapsed_time} seconds.")}")


# # Either agent can decide to end
# def router(state):
#     # This is the router
#     messages = state["messages"]
#     last_message = messages[-1]
#     if "function_call" in last_message.additional_kwargs:
#         # The previus agent is invoking a tool
#         return "call_tool"
#     if "FINAL ANSWER" in last_message.content:
#         # Any agent decided the work is done
#         return "end"
#     return "continue"


# def tool_node(state, tool_executor):
#     """This runs tools in the graph

#     It takes in an agent action and calls that tool and returns the result."""
#     messages = state["messages"]
#     # Based on the continue condition
#     # we know the last message involves a function call
#     last_message = messages[-1]
#     # We construct an ToolInvocation from the function_call
#     tool_input = json.loads(
#         last_message.additional_kwargs["function_call"]["arguments"]
#     )
#     # We can pass single-arg inputs by value
#     if len(tool_input) == 1 and "__arg1" in tool_input:
#         tool_input = next(iter(tool_input.values()))
#     tool_name = last_message.additional_kwargs["function_call"]["name"]
#     action = ToolInvocation(
#         tool=tool_name,
#         tool_input=tool_input,
#     )
#     # We call the tool_executor and get back a response
#     response = tool_executor.invoke(action)
#     # We use the response to create a FunctionMessage
#     function_message = FunctionMessage(
#         content=f"{tool_name} response: {str(response)}", name=action.tool
#     )
#     # We return a list, because this will get added to the existing list
#     return {"messages": [function_message]}


# # Helper function to create a node for a given agent
# def agent_node(state, agent, name):
#     result = agent.invoke(state)
#     # We convert the agent output into a format that is suitable to append to the global state
#     if isinstance(result, FunctionMessage):
#         pass
#     else:
#         result = HumanMessage(**result.dict(exclude={"type", "name"}), name=name)
#     return {
#         "messages": [result],
#         # Since we have a strict workflow, we can
#         # track the sender so we know who to pass to next.
#         "sender": name,
#     }


# def create_nodes_from(agents):
#     nodes = []
#     tools = [agent.tools for agent in agents]
#     tools = [tool for sublist in tools for tool in sublist]
#     tool_executor = ToolExecutor(tools)
#     node = functools.partial(tool_node, tool_executor=tool_executor)
#     nodes.append(tool_node)
#     for agent in agents:
#         node = functools.partial(agent_node, agent=agent, name=agent.name)
#         nodes.append(node)
#     return nodes


# def create_conditional_edges_from(agents):
#     return []
# self.workflow.add_conditional_edges(
#     "Argentina",
#     router,
#     {"continue": "Sweden", "call_tool": "call_tool", "end": END},
# )
# self.workflow.add_conditional_edges(
#     "Sweden",
#     self.router,
#     {"continue": "Argentina", "call_tool": "call_tool", "end": END},
# )

# self.workflow.add_conditional_edges(
#     "call_tool",
#     # Each agent node updates the 'sender' field
#     # the tool calling node does not, meaning
#     # this edge will route back to the original agent
#     # who invoked the tool
#     lambda x: x["sender"],
#     {
#         "Argentina": "Argentina",
#         "Sweden": "Sweden",
#     },
# )
