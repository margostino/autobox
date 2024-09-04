from typing import List, Optional


class MailBoxConfig:
    def __init__(self, max_size: int):
        self.max_size = max_size


class OrchestratorConfig:
    def __init__(
        self, name: str, mailbox: MailBoxConfig, verbose: bool, instruction: str
    ):
        self.name = name
        self.mailbox = mailbox
        self.verbose = verbose
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
        verbose: bool = False,
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
        timeout: int,
        task: str,
        logging: LoggingConfig,
        agents: List[AgentConfig],
        orchestrator: OrchestratorConfig,
    ):
        self.max_steps = max_steps
        self.task = task
        self.agents = agents
        self.orchestrator = orchestrator
        self.timeout = timeout
        self.loggings = logging
