from typing import List, Optional


class MailBoxConfig:
    def __init__(self, max_size: int):
        self.max_size = max_size


class OrchestratorConfig:
    def __init__(self, name: str, mailbox: MailBoxConfig, instruction: str):
        self.name = name
        self.mailbox = mailbox
        self.instruction = instruction


class LLMConfig:
    def __init__(self, model: str):
        self.model = model


class LoggingConfig:
    def __init__(self, file_path: Optional[str] = None):
        self.file_path = file_path


class AgentConfig:
    def __init__(
        self,
        name: str,
        backstory: str,
        mailbox: MailBoxConfig,
        llm: Optional[LLMConfig] = None,
    ):
        self.llm = llm
        self.name = name
        self.backstory = backstory
        self.mailbox = mailbox


class SimulationConfig:
    def __init__(
        self,
        name: str,
        max_steps: int,
        timeout: int,
        task: str,
        logging: LoggingConfig,
        agents: List[AgentConfig],
        orchestrator: OrchestratorConfig,
        verbose: bool = False,
    ):
        self.max_steps = max_steps
        self.task = task
        self.agents = agents
        self.orchestrator = orchestrator
        self.timeout = timeout
        self.loggings = logging
        self.verbose = verbose
        self.name = name
