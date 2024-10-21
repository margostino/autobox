import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from autobox.schemas.metrics import Metric


class SimulationStatus(str, Enum):
    in_progress = "in progress"
    new = "new"
    failed = "failed"
    completed = "completed"


class MailboxConfig(BaseModel):
    max_size: int


class LLMConfig(BaseModel):
    model: str


class LoggingConfig(BaseModel):
    log_path: Optional[str] = Field(default=None)
    log_file: Optional[str] = Field(default=None)
    verbose: bool = Field(default=False)


class AgentConfig(BaseModel):
    name: str
    backstory: str
    llm: LLMConfig
    mailbox: MailboxConfig
    role: str


class OrchestratorConfig(BaseModel):
    name: str
    mailbox: MailboxConfig
    instruction: str
    llm: LLMConfig


class EvaluatorConfig(BaseModel):
    name: str
    mailbox: MailboxConfig
    llm: LLMConfig


class SimulationConfig(BaseModel):
    name: str
    max_steps: int
    timeout: int
    task: str
    metrics_path: str

    class Config:
        arbitrary_types_allowed = True


class SimulationRequest(BaseModel):
    name: str
    max_steps: int  # TODO: tbd
    timeout: int
    task: str
    metrics_path: str
    logging: LoggingConfig
    orchestrator: OrchestratorConfig
    evaluator: EvaluatorConfig
    agents: List[AgentConfig]
    is_server_mode: bool = Field(default=True)


class InstructionRequest(BaseModel):
    instruction: str


class SimulationCacheValue(BaseModel):
    id: str
    status: str
    started_at: datetime
    finished_at: datetime = Field(default=None)
    # simulation: Simulation = Field(default=None)
    metrics: Dict[str, Metric] = Field(default={})
    summary: str = Field(default=None)

    class Config:
        arbitrary_types_allowed = True


class SimulationAgentResponse(BaseModel):
    id: int
    name: str


class SimulationResponse(BaseModel):
    id: str
    status: str
    name: str
    started_at: datetime
    finished_at: datetime = Field(default=None)
    agents: List[SimulationAgentResponse]
    orchestrator: SimulationAgentResponse
    evaluator: SimulationAgentResponse
    summary: Optional[str] = None
    progress: Optional[int] = None

    class Config:
        arbitrary_types_allowed = True
