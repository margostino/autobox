from typing import List, Optional


class LLMConfig:
    def __init__(self, model: str):
        self.model = model


class AgentConfig:
    def __init__(
        self,
        name: str,
        backstory: str,
        verbose: bool,
        llm: Optional[LLMConfig] = None,
    ):
        self.llm = llm
        self.name = name
        self.backstory = backstory
        self.verbose = verbose


class SimulationConfig:
    def __init__(
        self,
        max_steps: int,
        task: str,
        agents: List[AgentConfig],
    ):
        self.max_steps = max_steps
        self.task = task
        self.agents = agents
