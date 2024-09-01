import datetime
from typing import List

from pydantic import BaseModel, Field

from autobox.core.simulation import Simulation


class MailboxConfig(BaseModel):
    max_size: int


class LLMConfig(BaseModel):
    model: str


class AgentConfig(BaseModel):
    name: str
    verbose: bool
    backstory: str
    llm: LLMConfig
    mailbox: MailboxConfig
    role: str


class OrchestratorConfig(BaseModel):
    name: str
    mailbox: MailboxConfig
    instruction: str


class SimulationConfig(BaseModel):
    max_steps: int
    timeout: int
    task: str


class SimulationRequest(BaseModel):
    simulation: SimulationConfig
    orchestrator: OrchestratorConfig
    agents: List[AgentConfig]


class InstructionRequest(BaseModel):
    instruction: str


class SimulationStatus(BaseModel):
    simulation_id: str
    status: str
    details: SimulationRequest
    started_at: datetime
    finished_at: datetime = Field(default=None)
    simulation: Simulation = Field(default=None)

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
