from typing import List, Optional


class LLMConfig:
    def __init__(self, model: str):
        self.model = model


class ToolConfig:
    def __init__(
        self,
        name: str,
        type: str,
        model: str,
        prompt_template: str,
        description: str,
        input_description: str,
    ):
        self.name = name
        self.type = type
        self.model = model
        self.description = description
        self.prompt_template = prompt_template
        self.input_description = input_description


class AgentConfig:
    def __init__(
        self,
        name: str,
        role: str,
        verbose: bool,
        system_message: str,
        llm: Optional[LLMConfig] = None,
        tools: Optional[List[ToolConfig]] = None,
    ):
        self.llm = llm
        self.name = name
        self.role = role
        self.verbose = verbose
        self.system_message = system_message
        self.tools = tools if tools is not None else []


class SimulationConfig:
    def __init__(
        self,
        max_steps: int,
        initial_input: str,
        entry_point: str,
        agents: List[AgentConfig],
    ):
        self.max_steps = max_steps
        self.initial_input = initial_input
        self.entry_point = entry_point
        self.agents = agents
