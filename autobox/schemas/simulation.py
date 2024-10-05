import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from autobox.core.simulation import Simulation
from autobox.schemas.metrics import Metric


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
    logging: LoggingConfig
    simulation: SimulationConfig
    orchestrator: OrchestratorConfig
    evaluator: EvaluatorConfig
    agents: List[AgentConfig]
    is_server_mode: bool = Field(default=True)


class InstructionRequest(BaseModel):
    instruction: str


class SimulationStatus(BaseModel):
    simulation_id: str
    status: str
    details: SimulationRequest
    started_at: datetime
    finished_at: datetime = Field(default=None)
    simulation: Simulation = Field(default=None)
    metrics: Dict[str, Metric] = Field(default={})

    class Config:
        arbitrary_types_allowed = True


class SimulationStatusAgentResponse(BaseModel):
    id: int
    name: str


class SimulationStatusResponse(BaseModel):
    simulation_id: str
    status: str
    details: SimulationRequest
    started_at: datetime
    finished_at: datetime = Field(default=None)
    agents: List[SimulationStatusAgentResponse]
    orchestrator: SimulationStatusAgentResponse

    class Config:
        arbitrary_types_allowed = True
