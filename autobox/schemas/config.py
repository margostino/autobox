from typing import List, Optional


class MailBoxConfig:
    def __init__(self, name: str, max_size: int):
        self.name = name
        self.max_size = max_size


class OrchestratorConfig:
    def __init__(self, name: str, mailbox: MailBoxConfig, verbose: bool):
        self.name = name
        self.mailbox = mailbox
        self.verbose = verbose


class LLMConfig:
    def __init__(self, model: str):
        self.model = model


class AgentConfig:
    def __init__(
        self,
        name: str,
        backstory: str,
        verbose: bool,
        mailbox: MailBoxConfig,
        llm: Optional[LLMConfig] = None,
    ):
        self.llm = llm
        self.name = name
        self.backstory = backstory
        self.verbose = verbose
        self.mailbox = mailbox


class SimulationConfig:
    def __init__(
        self,
        max_steps: int,
        task: str,
        agents: List[AgentConfig],
        orchestrator: OrchestratorConfig,
    ):
        self.max_steps = max_steps
        self.task = task
        self.agents = agents
        self.orchestrator = orchestrator
