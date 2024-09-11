from typing import List, Optional


class LLMConfig:
    def __init__(self, model: str):
        self.model = model


class MailBoxConfig:
    def __init__(self, max_size: int):
        self.max_size = max_size


class EvaluatorConfig:
    def __init__(
        self,
        name: str,
        mailbox: MailBoxConfig,
        llm: Optional[LLMConfig] = None,
    ):
        self.name = name
        self.mailbox = mailbox
        self.llm = llm


class OrchestratorConfig:
    def __init__(
        self,
        name: str,
        mailbox: MailBoxConfig,
        instruction: str,
        llm: Optional[LLMConfig] = None,
    ):
        self.name = name
        self.mailbox = mailbox
        self.instruction = instruction
        self.llm = llm


class LoggingConfig:
    def __init__(self, file_path: Optional[str] = None, verbose: bool = False):
        self.file_path = file_path
        self.verbose = verbose


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
        evaluator: EvaluatorConfig,
        metrics_path: str = None,
    ):
        self.max_steps = max_steps
        self.task = task
        self.agents = agents
        self.orchestrator = orchestrator
        self.timeout = timeout
        self.loggings = logging
        self.name = name
        self.metrics_path = metrics_path
        self.evaluator = evaluator


class ServerConfig:
    def __init__(self, host: str, port: int, reload: bool, logging: LoggingConfig):
        self.host = host
        self.port = port
        self.reload = reload
        self.logging = logging
